# coffy/sql/orm.py
# author: nsarathy

"""
This module provides a simple ORM layer on top of SQLite.
"""

from __future__ import annotations
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from .engine import get_connection
from .sqldict import SQLDict


# Field descriptors


class Field:
    """
    Class representing a database field.
    """

    sql_type: str
    primary_key: bool
    nullable: bool
    default: Any

    def __init__(
        self,
        sql_type: str,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
    ):
        """
        Initialize a new Field instance.
        sql_type -- The SQL data type of the field.
        primary_key -- Whether this field is a primary key.
        nullable -- Whether this field can be null.
        default -- The default value for this field.
        """
        self.sql_type = sql_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.name = ""  # set by ModelMeta

    def ddl(self) -> str:
        """
        Generate the SQL DDL statement for this field.
        """
        bits = [self.name, self.sql_type]
        if self.primary_key:
            bits.append("PRIMARY KEY")
        if not self.nullable:
            bits.append("NOT NULL")
        if self.default is not None:
            bits.append("DEFAULT ?")  # bound when emitting CREATE
        return " ".join(bits)


class Integer(Field):
    """
    Class representing an INTEGER field.
    """

    def __init__(self, **kw):
        """
        Initialize a new Integer field.
        kw -- Additional keyword arguments for the field.
        """
        super().__init__("INTEGER", **kw)


class Real(Field):
    def __init__(self, **kw):
        """
        Initialize a new Real field.
        kw -- Additional keyword arguments for the field.
        """
        super().__init__("REAL", **kw)


class Text(Field):
    def __init__(self, **kw):
        """
        Initialize a new Text field.
        kw -- Additional keyword arguments for the field.
        """
        super().__init__("TEXT", **kw)


class Blob(Field):
    def __init__(self, **kw):
        """
        Initialize a new Blob field.
        kw -- Additional keyword arguments for the field.
        """
        super().__init__("BLOB", **kw)


# Model metaclass


class ModelMeta(type):
    """
    Metaclass for all models.
    """

    def __new__(mcls, name, bases, attrs):
        """
        Initialize a new ModelMeta instance.
        mcls -- The metaclass itself.
        name -- The name of the model class.
        bases -- The base classes of the model.
        attrs -- The attributes of the model.
        Returns the new model class.
        """
        if name == "Model":
            return super().__new__(mcls, name, bases, attrs)

        # collect fields
        fields: Dict[str, Field] = {}
        for k, v in list(attrs.items()):
            if isinstance(v, Field):
                v.name = k
                fields[k] = v

        attrs["_meta"] = {
            "table": attrs.get("__tablename__", name.lower()),
            "fields": fields,
            "pk": next((f.name for f in fields.values() if f.primary_key), None),
        }

        cls = super().__new__(mcls, name, bases, attrs)
        return cls


# Query builder

T = TypeVar("T", bound="Model")


def _quote_ident(ident: str) -> str:
    """
    Quote an identifier. Supports qualified names like table.column.
    Only allows [A-Za-z0-9_] in each part.
    ident -- The identifier to quote.
    Returns the quoted identifier.
    """
    parts = ident.split(".")
    out = []
    for p in parts:
        if not p or not p.replace("_", "").isalnum():
            raise ValueError(f"Invalid identifier: {ident!r}")
        out.append(f'"{p}"')
    return ".".join(out)


def _cols_and_placeholders(d: Dict[str, Any]) -> Tuple[str, str, List[Any]]:
    """
    Generate the column names and placeholders for a SQL statement.
    d -- The dictionary of column names and values.
    Returns the column names, placeholders, and values.
    """
    cols = ", ".join(_quote_ident(k) for k in d.keys())
    qs = ", ".join("?" for _ in d)
    return cols, qs, list(d.values())


def _assignments(d: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    Generate the SET clause for an UPDATE statement.
    d -- The dictionary of column names and values.
    Returns the SET clause and values.
    """
    sets = ", ".join(f"{_quote_ident(k)} = ?" for k in d.keys())
    return sets, list(d.values())


# condition builder supports nested AND/OR trees
Cond = Union[
    Tuple[str, str, Any],  # ("col", "op", value)
    Tuple[Union["Cond", "CondList"], Literal["AND", "OR"], Union["Cond", "CondList"]],
]
CondList = List[Union[Cond, "CondList"]]


def _compile_condition(cond: Union[Cond, CondList]) -> Tuple[str, List[Any]]:
    """
    Compile a condition into SQL.
    cond -- The condition to compile.
    Returns the compiled SQL and parameters.
    """
    if isinstance(cond, list):
        # implicit AND chain
        sqls, params = [], []
        for c in cond:
            s, p = _compile_condition(c)
            sqls.append(f"({s})")
            params.extend(p)
        return " AND ".join(sqls), params

    # leaf or junction
    if (
        isinstance(cond, tuple)
        and len(cond) == 3
        and isinstance(cond[1], str)
        and cond[1] in ("AND", "OR")
    ):
        # junction: (left_sql, "AND"/"OR", right_sql) where left_sql and right_sql are themselves compiled subtrees
        left_sql, left_params = _compile_condition(cond[0])  # type: ignore[arg-type]
        right_sql, right_params = _compile_condition(cond[2])  # type: ignore[arg-type]
        return f"({left_sql}) {cond[1]} ({right_sql})", left_params + right_params

    col, op, val = cond
    col_sql = _quote_ident(col)
    if op.upper() == "IN":
        if not isinstance(val, (list, tuple)):
            raise ValueError("IN expects a list or tuple")
        qs = ", ".join("?" for _ in val) or "NULL"
        return f"{col_sql} IN ({qs})", list(val)
    if op.upper() in ("IS", "IS NOT") and val is None:
        return f"{col_sql} {op} NULL", []
    return f"{col_sql} {op} ?", [val]


class Query:
    """
    Build a SQL query.
    """

    def __init__(self, model: Type[T]):
        """
        Initialize a new Query instance.
        model -- The model class to query.
        """
        self.model = model
        self._columns: List[str] = []
        self._where: Optional[Union[Cond, CondList]] = None
        self._order: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._joins: List[Tuple[str, str, str]] = []  # (join_type, table_sql, on_sql)
        self._group_by: List[str] = []
        self._having: Optional[Union[Cond, CondList]] = None
        self._ctes: List[Tuple[str, str, List[Any]]] = []  # (name, sql, params)

    # basic pieces
    def select(self, *cols: str) -> "Query":
        """
        Set the columns to select.
        cols -- The column names to select.
        Returns the Query instance.
        """
        self._columns = list(cols)
        return self

    def where(self, cond: Union[Cond, CondList]) -> "Query":
        """
        Set the WHERE condition for the query.
        cond -- The condition to apply.
        Returns the Query instance.
        """
        self._where = cond
        return self

    def order_by(self, *cols: str) -> "Query":
        """
        Set the ORDER BY clause for the query.
        cols -- The column names to order by.
        Returns the Query instance.
        """
        for c in cols:
            # support "col ASC" or "col DESC"
            parts = c.split()
            ident = parts[0]
            rest = (
                (" " + parts[1].upper())
                if len(parts) > 1 and parts[1].upper() in ("ASC", "DESC")
                else ""
            )
            self._order.append(_quote_ident(ident) + rest)
        return self

    def limit(self, n: int, offset: Optional[int] = None) -> "Query":
        """
        Set the LIMIT clause for the query.
        n -- The maximum number of rows to return.
        offset -- The number of rows to skip before starting to return rows.
        Returns the Query instance.
        """
        self._limit = n
        if offset is not None:
            self._offset = offset
        return self

    def join(self, other_table: str, on: str, kind: str = "INNER") -> "Query":
        """
        Set the JOIN clause for the query.
        other_table -- The table to join with.
        on -- The ON condition for the join.
        kind -- The type of join (INNER, LEFT, RIGHT, FULL).
        Returns the Query instance.
        """

        # on should be a safe SQL like: "users.id = posts.user_id"
        # we still validate identifiers crudely
        def _validate_on(expr: str):
            tokens = [
                t
                for t in expr.replace("=", " ").replace(".", " ").split()
                if t.isidentifier()
            ]
            for t in tokens:
                _quote_ident(t)  # raises if invalid

        _validate_on(on)
        tbl_sql = _quote_ident(other_table)
        kind_u = kind.upper()
        if kind_u not in (
            "INNER",
            "LEFT",
            "RIGHT",
            "FULL",
            "LEFT OUTER",
            "RIGHT OUTER",
            "FULL OUTER",
        ):
            raise ValueError("Unsupported join type")
        self._joins.append((kind_u, tbl_sql, on))
        return self

    def group_by(self, *cols: str) -> "Query":
        """
        Set the GROUP BY clause for the query.
        cols -- The column names to group by.
        Returns the Query instance.
        """
        self._group_by = [_quote_ident(c) for c in cols]
        return self

    def having(self, cond: Union[Cond, CondList]) -> "Query":
        """
        Set the HAVING condition for the query.
        cond -- The condition to apply.
        Returns the Query instance.
        """
        self._having = cond
        return self

    def with_cte(
        self,
        name: str,
        sql: str,
        params: Optional[List[Any]] = None,
        recursive: bool = False,
    ) -> "Query":
        """
        Add a Common Table Expression (CTE) to the query.
        name -- The name of the CTE.
        sql -- The SQL query for the CTE.
        params -- The parameters for the CTE query.
        recursive -- Whether the CTE is recursive.
        Returns the Query instance.
        """
        # name validation, and the SQL should be parameterized with "?"
        _quote_ident(name)
        self._ctes.append(
            (
                ("RECURSIVE " if recursive else "") + _quote_ident(name),
                sql,
                params or [],
            )
        )
        return self

    def _build_select(self) -> Tuple[str, List[Any]]:
        """
        Build the SELECT SQL query.
        Returns the SQL string and a list of parameters.
        """
        table = _quote_ident(self.model._meta["table"])
        cols = ", ".join(self._columns) if self._columns else "*"

        sql_parts = []
        params: List[Any] = []

        if self._ctes:
            cte_bits = []
            for cte_name, cte_sql, cte_params in self._ctes:
                cte_bits.append(f"{cte_name} AS ({cte_sql})")
                params.extend(cte_params)
            sql_parts.append(f"WITH {', '.join(cte_bits)}")

        sql_parts.append(f"SELECT {cols} FROM {table}")

        for kind, tbl_sql, on in self._joins:
            sql_parts.append(f"{kind} JOIN {tbl_sql} ON {on}")

        if self._where is not None:
            where_sql, where_params = _compile_condition(self._where)
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        if self._group_by:
            sql_parts.append("GROUP BY " + ", ".join(self._group_by))
            if self._having is not None:
                h_sql, h_params = _compile_condition(self._having)
                sql_parts.append(f"HAVING {h_sql}")
                params.extend(h_params)

        if self._order:
            sql_parts.append("ORDER BY " + ", ".join(self._order))

        if self._limit is not None:
            sql_parts.append("LIMIT ?")
            params.append(self._limit)
            if self._offset is not None:
                sql_parts.append("OFFSET ?")
                params.append(self._offset)

        return " ".join(sql_parts), params

    def all(self) -> SQLDict:
        """
        Execute the query and return all results.
        """
        sql, params = self._build_select()
        conn = get_connection()
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return SQLDict([dict(zip(cols, r)) for r in rows])

    def first(self) -> Optional[Dict[str, Any]]:
        """
        Execute the query and return the first result.
        """
        self.limit(1)
        res = self.all().as_list()
        return res[0] if res else None

    # simple aggregates
    def aggregate(self, **agg: str) -> Dict[str, Any]:
        """
        Execute the aggregate query and return the results.
        """
        # usage: .aggregate(total="COUNT(*)", avg_age="AVG(age)")
        sels = ", ".join(
            f"{expr} AS {_quote_ident(alias)}" for alias, expr in agg.items()
        )
        base = Query(self.model).select(sels)
        base._where = self._where
        base._joins = self._joins
        base._ctes = self._ctes
        sql, params = base._build_select()
        conn = get_connection()
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        cols = [d[0] for d in cur.description] if cur.description else []
        return dict(zip(cols, row)) if row else {}


# Manager and Model


class Manager:
    """
    Manager class for handling database operations for a specific model.
    """

    def __init__(self, model: Type[T]):
        """
        Initialize the Manager with the given model.
        model -- The model class that this manager is for.
        """
        self.model = model

    def create_table(self, if_not_exists: bool = True) -> None:
        """
        Create the database table for the model.
        if_not_exists -- Whether to create the table only if it does not exist.
        """
        tbl = _quote_ident(self.model._meta["table"])
        fields = self.model._meta["fields"]
        pieces = []
        defaults_params: List[Any] = []
        for f in fields.values():
            ddl = f.ddl()
            pieces.append(ddl)
            if f.default is not None:
                defaults_params.append(f.default)
        sql = f'CREATE TABLE {"IF NOT EXISTS " if if_not_exists else ""}{tbl} ({", ".join(pieces)})'
        conn = get_connection()
        with conn:
            # replace "DEFAULT ?" placeholders once, in order
            if defaults_params:
                # sqlite does not allow bound params in DDL directly
                # so we inline safe literals for defaults using SQLite's quote function
                quoted = []
                for val in defaults_params:
                    q = conn.execute("SELECT quote(?)", (val,)).fetchone()[0]
                    quoted.append(q)
                # inject quoted values in order
                for qv in quoted:
                    sql = sql.replace("DEFAULT ?", f"DEFAULT {qv}", 1)
            conn.execute(sql)

    def drop_table(self, if_exists: bool = True) -> None:
        """
        Drop the database table for the model.
        if_exists -- Whether to drop the table only if it exists.
        """
        tbl = _quote_ident(self.model._meta["table"])
        sql = f'DROP TABLE {"IF EXISTS " if if_exists else ""}{tbl}'
        conn = get_connection()
        with conn:
            conn.execute(sql)

    def insert(self, **values) -> int:
        """
        Insert a new row into the database table for the model.
        values -- The column values to insert.
        Returns the ID of the inserted row.
        """
        tbl = _quote_ident(self.model._meta["table"])
        cols, qs, params = _cols_and_placeholders(values)
        sql = f"INSERT INTO {tbl} ({cols}) VALUES ({qs})"
        conn = get_connection()
        with conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid

    def bulk_insert(self, rows: Iterable[Dict[str, Any]]) -> int:
        """
        Insert multiple rows. Rows may have different key sets.
        Columns that are omitted in a given row will use table defaults.
        Returns total inserted row count.
        """
        rows = list(rows)
        if not rows:
            return 0

        tbl = _quote_ident(self.model._meta["table"])
        valid_cols = set(self.model._meta["fields"].keys())

        # group rows by sorted column tuple so defaults can apply when omitted
        groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
        for r in rows:
            if not isinstance(r, dict):
                raise TypeError("bulk_insert expects dict rows")
            unknown = set(r.keys()) - valid_cols
            if unknown:
                raise ValueError(
                    f"Unknown columns for {self.model._meta['table']}: {sorted(unknown)}"
                )
            key = tuple(sorted(r.keys()))
            groups.setdefault(key, []).append(r)

        total = 0
        conn = get_connection()
        with conn:
            for key_cols, grp in groups.items():
                if not key_cols:
                    # all-default row, use DEFAULT VALUES
                    sql = f"INSERT INTO {tbl} DEFAULT VALUES"
                    cur = conn.executemany(sql, [tuple() for _ in grp])
                    total += cur.rowcount
                    continue

                cols_sql = ", ".join(_quote_ident(c) for c in key_cols)
                qs = ", ".join("?" for _ in key_cols)
                sql = f"INSERT INTO {tbl} ({cols_sql}) VALUES ({qs})"
                params = [tuple(r[c] for c in key_cols) for r in grp]
                cur = conn.executemany(sql, params)
                total += cur.rowcount

        return total

    def update(self, where: Union[Cond, CondList], **values) -> int:
        """
        Update existing rows in the database table for the model.
        where -- The condition to match rows for update.
        values -- The column values to update.
        Returns the number of updated rows.
        """
        tbl = _quote_ident(self.model._meta["table"])
        set_sql, set_params = _assignments(values)
        where_sql, where_params = _compile_condition(where)
        sql = f"UPDATE {tbl} SET {set_sql} WHERE {where_sql}"
        conn = get_connection()
        with conn:
            cur = conn.execute(sql, set_params + where_params)
            return cur.rowcount

    def delete(self, where: Union[Cond, CondList]) -> int:
        """
        Delete rows from the database table for the model.
        where -- The condition to match rows for deletion.
        Returns the number of deleted rows.
        """
        tbl = _quote_ident(self.model._meta["table"])
        where_sql, where_params = _compile_condition(where)
        sql = f"DELETE FROM {tbl} WHERE {where_sql}"
        conn = get_connection()
        with conn:
            cur = conn.execute(sql, where_params)
            return cur.rowcount

    def get(self, **eq_filters) -> Optional[Dict[str, Any]]:
        """
        Get a single row from the database table for the model.
        eq_filters -- The equality filters to apply.
        Returns the matching row, or None if not found.
        """
        # get by equality filters, limited to 1
        conds: List[Cond] = [(k, "=", v) for k, v in eq_filters.items()]
        return self.query().where(conds).first()

    def query(self) -> Query:
        """
        Create a new Query object for the model.
        """
        return Query(self.model)


class Model(metaclass=ModelMeta):
    """
    Base class for database models.
    """

    objects: Manager  # populated in __init_subclass__

    def __init_subclass__(cls, **kwargs):
        """
        Initialize the model class.
        kwargs -- Additional keyword arguments for model initialization.
        """
        super().__init_subclass__(**kwargs)
        cls.objects = Manager(cls)


# Convenience helpers
def to_sqldict(rows: List[Dict[str, Any]]) -> SQLDict:
    """
    Convert a list of dictionaries to a SQLDict.
    """
    return SQLDict(rows)


def raw(sql: str, params: Optional[Iterable[Any]] = None) -> SQLDict:
    """
    Execute a raw SQL query and return the results as a SQLDict.
    """
    conn = get_connection()
    cur = conn.execute(sql, list(params or []))
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    return SQLDict([dict(zip(cols, r)) for r in rows])
