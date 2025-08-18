#!/usr/bin/env python3

# coffy/cli/sql_cli.py
# author: nsarathy

"""
This CLI tool provides a command-line interface for interacting with SQL databases.
"""

import argparse
import json
import os
import sys
from typing import List

# coffy imports
from coffy.sql import init, query, close  # provides SQLDict for SELECTs

OK = 0
ERR = 1


def _die(msg: str, code: int = ERR) -> None:
    """
    Print an error message and exit.
    msg -- The error message to print.
    code -- The exit code (default: ERR)
    """
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def _require_db(db: str) -> str:
    """
    Ensure the given database path is valid.
    db -- The database path to check.
    """
    if not db:
        _die("missing --db PATH")
    if db.strip() in (":memory:", "file::memory:?cache=shared"):
        _die("in-memory databases are not allowed in this CLI, provide a file path")
    return db


def _load_sql(source: str) -> str:
    """
    Load SQL from a string or file.
    source -- The SQL source to load.
    """
    # Support @file.sql, same as many CLIs
    if source.startswith("@"):
        path = source[1:]
        if not os.path.exists(path):
            _die(f"SQL file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return source


def _split_statements(sql: str) -> List[str]:
    """
    Split SQL into individual statements.
    sql -- The SQL script to split.
    """
    # naive split by ';', good enough for simple scripts without embedded ';'
    parts = [s.strip() for s in sql.split(";")]
    return [s for s in parts if s]


def _is_select(stmt: str) -> bool:
    """
    Check if a SQL statement is a SELECT query.
    stmt -- The SQL statement to check.
    """
    s = stmt.lstrip().lower()
    # treat common CTE starts as read
    return s.startswith("select") or s.startswith("with")


def _print_select_result(res, as_json: bool, pretty: bool) -> None:
    """
    Print the result of a SELECT query.
    res -- The query result.
    as_json -- Whether to print as JSON.
    pretty -- Whether to pretty-print JSON.
    """
    if as_json:
        data = res.as_list()
        if pretty:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(data, ensure_ascii=False))
    else:
        # falls back to SQLDict.__repr__ pretty table
        print(res)


def _export_result(res, out_path: str) -> None:
    """
    Export the query result to a file.
    res -- The query result.
    out_path -- The output file path.
    """
    ext = os.path.splitext(out_path)[1].lower()
    if ext == ".json":
        res.to_json(out_path)
        print(f"wrote {out_path}")
    elif ext == ".csv":
        res.to_csv(out_path)
        print(f"wrote {out_path}")
    else:
        _die("unsupported export extension, use .json or .csv")


def cmd_init(args: argparse.Namespace) -> int:
    """
    Initialize a new SQL database.
    args -- The command-line arguments.
    """
    db = _require_db(args.db)
    init(db)
    # Opening creates the file if missing, close immediately
    close()
    print(f"initialized {db}")
    return OK


def cmd_run(args: argparse.Namespace) -> int:
    """
    Run SQL statements.
    args -- The command-line arguments.
    """
    db = _require_db(args.db)
    sql = _load_sql(args.sql)
    stmts = _split_statements(sql)
    if not stmts:
        _die("no SQL to execute")

    init(db)
    last_status = OK
    try:
        for i, stmt in enumerate(stmts, start=1):
            if _is_select(stmt):
                res = query(stmt)
                # optional export per run, only valid if single SELECT or user accepts last SELECT export
                if args.out and i == len(stmts):
                    _export_result(res, args.out)
                else:
                    _print_select_result(res, as_json=args.json, pretty=args.pretty)
            else:
                status = query(stmt)  # returns status dict
                print(json.dumps(status))
        return last_status
    finally:
        close()


def cmd_export(args: argparse.Namespace) -> int:
    """
    Export query results to a file.
    args -- The command-line arguments.
    """
    db = _require_db(args.db)
    sql = _load_sql(args.sql)
    if not _is_select(sql):
        _die("export requires a SELECT or WITH query")
    if not args.out:
        _die("missing --out PATH.{json,csv}")

    init(db)
    try:
        res = query(sql)
        _export_result(res, args.out)
        return OK
    finally:
        close()


def cmd_view(args: argparse.Namespace) -> int:
    """
    View query results in a web browser.
    args -- The command-line arguments.
    """
    db = _require_db(args.db)
    sql = _load_sql(args.sql)
    if not _is_select(sql):
        _die("view requires a SELECT or WITH query")

    init(db)
    try:
        res = query(sql)
        # launches default browser
        res.view(title=args.title or "SQL Query Results")
        return OK
    finally:
        close()


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """
    p = argparse.ArgumentParser(
        prog="coffy-sql",
        description="File-backed CLI for coffy.sql, simple SQLite workflows",
    )
    p.add_argument(
        "--db", required=True, help="Path to SQLite file, must be a file, not in-memory"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sp_init = sub.add_parser("init", help="Create or open a database file")
    sp_init.set_defaults(func=cmd_init)

    sp_run = sub.add_parser("run", help="Run SQL, prints results for SELECT")
    sp_run.add_argument("sql", help="SQL string, or @path/to/file.sql")
    sp_run.add_argument(
        "--json", action="store_true", help="Emit SELECT results as JSON to stdout"
    )
    sp_run.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON when using --json"
    )
    sp_run.add_argument(
        "--out", help="If last statement is SELECT, export to .json or .csv"
    )
    sp_run.set_defaults(func=cmd_run)

    sp_export = sub.add_parser("export", help="Run a SELECT and write to .json or .csv")
    sp_export.add_argument("sql", help="SELECT query, or @path/to/file.sql")
    sp_export.add_argument(
        "--out", required=True, help="Output path ending in .json or .csv"
    )
    sp_export.set_defaults(func=cmd_export)

    sp_view = sub.add_parser(
        "view", help="Run a SELECT and open HTML viewer in browser"
    )
    sp_view.add_argument("sql", help="SELECT query, or @path/to/file.sql")
    sp_view.add_argument("--title", help="Browser tab title")
    sp_view.set_defaults(func=cmd_view)

    return p


def main(argv: List[str] | None = None) -> int:
    """
    Main entry point for the CLI.
    argv -- The command-line arguments.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        _die("interrupted", ERR)
    except Exception as e:
        _die(str(e), ERR)


if __name__ == "__main__":
    sys.exit(main())
