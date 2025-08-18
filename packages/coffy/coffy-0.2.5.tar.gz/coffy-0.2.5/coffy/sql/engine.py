# coffy/sql/engine.py
# author: nsarathy

"""
Shameless SQLite wrapper.
"""

from .sqldict import SQLDict
import sqlite3

# Internal connection state
_connection = None
_cursor = None


def get_connection() -> "sqlite3.Connection":
    """
    Return the active sqlite3 connection initialized by coffy.sql.init(...).
    Raises RuntimeError if not initialized.
    """
    global conn
    if _connection is None:
        raise RuntimeError(
            "Coffy SQL engine is not initialized. Call coffy.sql.init(...) first."
        )
    return _connection


def initialize(db_path=None):
    """
    Initialize the SQL engine with the given database path.
    db_path -- Path to the SQLite database file. If None, uses an in-memory
    """
    global _connection, _cursor
    if _connection:
        return  # already initialized
    # Uses in-memory DB if no path provided
    _connection = sqlite3.connect(db_path or ":memory:")
    _cursor = _connection.cursor()


def execute_query(sql: str):
    """
    Execute a SQL query and return the results.
    sql -- The SQL query to execute.
    Returns SQLDict for SELECT queries or a status dict for other queries.
    """
    global _connection, _cursor
    if _connection is None:
        initialize()  # uses in-memory if not initialized

    try:
        _cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            columns = [desc[0] for desc in _cursor.description]
            rows = _cursor.fetchall()
            return SQLDict([dict(zip(columns, row)) for row in rows])
        else:
            _connection.commit()
            return {"status": "success", "rows_affected": _cursor.rowcount}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def close_connection():
    """Close the database connection."""
    global _connection, _cursor
    if _cursor:
        _cursor.close()
        _cursor = None
    if _connection:
        _connection.close()
        _connection = None
