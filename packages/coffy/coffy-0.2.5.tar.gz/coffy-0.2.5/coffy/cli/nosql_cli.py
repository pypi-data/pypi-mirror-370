#!/usr/bin/env python3

# coffy/cli/nosql_cli.py
# author: nsarathy

"""
This CLI tool provides a command-line interface for interacting with NoSQL databases.
"""

import argparse
import json
import os
import sys
from typing import List

from coffy.nosql import db

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


def _ensure_parent(path: str) -> None:
    """
    Ensure the parent directory of the given path exists.
    path -- The file path to check.
    """
    parent = os.path.dirname(path)
    os.makedirs(parent or ".", exist_ok=True)


def _require_path(path: str) -> str:
    """
    Ensure the given path is valid.
    path -- The file path to check.
    """
    if not path:
        _die("missing --path FILE.json")
    if path.strip() in (":memory:", None):
        _die("in-memory stores are not allowed in this CLI, provide a JSON file path")
    if not path.endswith(".json"):
        _die("path must end with .json")
    return path


def _load_json_arg(s: str):
    """
    Load a JSON object from a string or file.
    s -- The string or file path to load.
    """
    if s == "-":
        return json.load(sys.stdin)
    if s.startswith("@"):
        with open(s[1:], "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(s)


def _parse_scalar(s: str):
    """
    Parse a scalar value from a string.
    s -- The string to parse.
    """
    try:
        return json.loads(s)
    except Exception:
        return s


def cmd_init(args: argparse.Namespace) -> int:
    """
    Initialize a new NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)
    _ensure_parent(path)
    if not os.path.exists(path):
        col.save(path)
    print(f"initialized collection '{args.collection}' at {path}")
    return OK


def cmd_add(args: argparse.Namespace) -> int:
    """
    Add a new document to the NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)
    doc = _load_json_arg(args.document)
    res = col.add(doc)
    _ensure_parent(path)
    col.save(path)
    print(json.dumps(res))
    return OK


def cmd_add_many(args: argparse.Namespace) -> int:
    """
    Add multiple documents to the NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)
    docs = _load_json_arg(args.documents)
    if not isinstance(docs, list):
        _die("add-many requires a JSON array")
    res = col.add_many(docs)
    _ensure_parent(path)
    col.save(path)
    print(json.dumps(res))
    return OK


def cmd_query(args: argparse.Namespace) -> int:
    """
    Query the NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)

    q = col.where(args.field)
    op = args.op.lower()

    needs_value = {"eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "matches"}
    if op in needs_value and args.value is None:
        _die(f"--value is required for op '{op}'")
    if op == "exists" and args.value is not None:
        _die("--value must not be provided for op 'exists'")

    if op in {"in", "nin"}:
        if args.value is None:
            _die(f"--value (JSON array) is required for op '{op}'")
        val = (
            _load_json_arg(args.value)
            if args.value.startswith(("@", "-"))
            else json.loads(args.value)
        )
        if not isinstance(val, list):
            _die(f"--value for '{op}' must be a JSON array")
    elif op in {"eq", "ne", "gt", "gte", "lt", "lte", "matches"}:
        val = _parse_scalar(args.value)
    else:
        val = None

    if op == "eq":
        q = q.eq(val)
    elif op == "ne":
        q = q.ne(val)
    elif op == "gt":
        q = q.gt(val)
    elif op == "gte":
        q = q.gte(val)
    elif op == "lt":
        q = q.lt(val)
    elif op == "lte":
        q = q.lte(val)
    elif op == "in":
        q = q.in_(val)
    elif op == "nin":
        q = q.nin(val)
    elif op == "exists":
        q = q.exists()
    elif op == "matches":
        q = q.matches(val)
    else:
        _die(f"unsupported operator: {args.op}")

    if args.count:
        print(q.count())
    elif args.first:
        print(json.dumps(q.first(), indent=2, ensure_ascii=False))
    else:
        docs = q.run(fields=args.fields).as_list() if args.fields else q.run().as_list()
        if args.out:
            _ensure_parent(args.out)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            print(f"wrote {args.out}")
        else:
            print(
                json.dumps(docs, indent=2 if args.pretty else None, ensure_ascii=False)
            )
    return OK


def cmd_agg(args: argparse.Namespace) -> int:
    """
    Aggregate data in the NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)

    if args.agg == "sum":
        val = col.sum(args.field)
    elif args.agg == "avg":
        val = col.avg(args.field)
    elif args.agg == "min":
        val = col.min(args.field)
    elif args.agg == "max":
        val = col.max(args.field)
    elif args.agg == "count":
        val = col.count()
    else:
        _die(f"unsupported aggregation: {args.agg}")

    print(val)
    return OK


def cmd_clear(args: argparse.Namespace) -> int:
    """
    Clear all documents in the NoSQL database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    col = db(args.collection, path=path)
    res = col.clear()
    _ensure_parent(path)
    col.save(path)
    print(json.dumps(res))
    return OK


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """
    p = argparse.ArgumentParser(
        prog="coffy-nosql",
        description="File-backed CLI for coffy.nosql (embedded JSON document store)",
    )
    p.add_argument("--collection", required=True, help="Collection name")
    p.add_argument(
        "--path", required=True, help="Path to JSON file backing the collection"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sp_init = sub.add_parser("init", help="Initialize collection file")
    sp_init.set_defaults(func=cmd_init)

    sp_add = sub.add_parser(
        "add", help="Add one document (JSON string, @file, or - for stdin)"
    )
    sp_add.add_argument(
        "document", help='JSON document, e.g. {"id":1} or @doc.json or -'
    )
    sp_add.set_defaults(func=cmd_add)

    sp_add_many = sub.add_parser(
        "add-many", help="Add many documents (JSON array string, @file, or -)"
    )
    sp_add_many.add_argument(
        "documents", help='JSON array, e.g. [{"id":2}] or @docs.json or -'
    )
    sp_add_many.set_defaults(func=cmd_add_many)

    sp_query = sub.add_parser("query", help="Simple query on one field")
    sp_query.add_argument(
        "--field", required=True, help="Field name, dot notation supported"
    )
    sp_query.add_argument(
        "--op",
        required=True,
        help="Operator: eq, ne, gt, gte, lt, lte, in, nin, exists, matches",
    )
    sp_query.add_argument(
        "--value", help="Value for operator. JSON array for in or nin"
    )
    sp_query.add_argument("--fields", nargs="+", help="Projection fields")
    mx = sp_query.add_mutually_exclusive_group()
    mx.add_argument("--count", action="store_true", help="Return count only")
    mx.add_argument("--first", action="store_true", help="Return first match only")
    sp_query.add_argument("--out", help="Write results to JSON file")
    sp_query.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON to stdout"
    )
    sp_query.set_defaults(func=cmd_query)

    sp_agg = sub.add_parser("agg", help="Collection-level aggregation")
    sp_agg.add_argument(
        "agg",
        choices=["sum", "avg", "min", "max", "count"],
        help="Aggregation function",
    )
    sp_agg.add_argument("--field", help="Field name, not required for count")
    sp_agg.set_defaults(func=cmd_agg)

    sp_clear = sub.add_parser("clear", help="Clear all documents in collection")
    sp_clear.set_defaults(func=cmd_clear)

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
