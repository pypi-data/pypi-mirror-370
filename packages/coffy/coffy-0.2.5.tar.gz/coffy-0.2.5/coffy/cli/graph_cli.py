#!/usr/bin/env python3

# coffy/cli/graph_cli.py
# author: nsarathy

"""
This CLI tool provides a command-line interface for interacting with graph databases.
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Optional

from coffy.graph import GraphDB

OK = 0
ERR = 1


# --------------------------
# utils
# --------------------------


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
        _die("in-memory graphs are not allowed in this CLI, provide a JSON file path")
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


def _parse_labels(val: Optional[str]) -> Optional[list]:
    """
    Parse labels from a CSV string or JSON array string.
    val -- The string to parse.
    """
    if val is None:
        return None
    # allow JSON or CSV
    try:
        j = json.loads(val)
        if isinstance(j, list):
            return j
        if isinstance(j, str):
            return [j]
    except Exception:
        pass
    return [s.strip() for s in val.split(",") if s.strip()]


def _parse_props_kv(items: Optional[list]) -> Dict[str, Any]:
    """
    Convert ['k=v', 'x=10', 'flag=true'] into {'k': 'v', 'x': 10, 'flag': True}.
    Values are JSON-parsed when possible, else kept as strings.
    items -- A list of strings in the format 'key=value'.
    """
    props: Dict[str, Any] = {}
    for item in items or []:
        if "=" not in item:
            _die(f"invalid --prop '{item}', must be key=value")
        k, v = item.split("=", 1)
        try:
            props[k] = json.loads(v)
        except Exception:
            props[k] = v
    return props


def _merge_props(
    kv_props: Dict[str, Any], json_props: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge props from --prop (key=value) and --props (JSON). Key=value wins on conflicts.
    kv_props -- The key=value properties from --prop.
    json_props -- The JSON properties from --props.
    """
    base = dict(json_props or {})
    base.update(kv_props)
    return base


def _open_db(path: str, directed: bool) -> GraphDB:
    """
    Open a graph database.
    path -- The file path to the database.
    directed -- Whether the graph is directed.
    """
    # GraphDB defaults to undirected unless directed=True
    return GraphDB(path=path, directed=bool(directed))


def _print_json(obj, pretty: bool = False):
    """
    Print a JSON object to stdout.
    obj -- The JSON object to print.
    pretty -- Whether to pretty-print the JSON (default: False).
    """
    print(json.dumps(obj, indent=2 if pretty else None, ensure_ascii=False))


# --------------------------
# commands
# --------------------------


def cmd_init(args: argparse.Namespace) -> int:
    """
    Initialize a new graph database.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    _ensure_parent(path)
    db = _open_db(path, args.directed)
    if not os.path.exists(path):
        db.save(path)
    print(f"initialized graph at {path} (directed={bool(args.directed)})")
    return OK


def cmd_add_node(args: argparse.Namespace) -> int:
    """
    Add a new node to the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    labels = _parse_labels(args.labels)
    kv = _parse_props_kv(args.prop)
    json_props = _load_json_arg(args.props) if args.props else None
    if json_props is not None and not isinstance(json_props, dict):
        _die("--props must be a JSON object")
    props = _merge_props(kv, json_props)
    db.add_node(args.id, labels=labels, **props)
    _ensure_parent(path)
    db.save()
    _print_json({"status": "ok", "node_id": args.id})
    return OK


def cmd_add_nodes(args: argparse.Namespace) -> int:
    """
    Add new nodes to the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    nodes = _load_json_arg(args.nodes)
    if not isinstance(nodes, list):
        _die("--nodes must be a JSON array of node dicts")
    db.add_nodes(nodes)
    _ensure_parent(path)
    db.save()
    _print_json({"status": "ok", "inserted": len(nodes)})
    return OK


def cmd_add_rel(args: argparse.Namespace) -> int:
    """
    Add a new relationship to the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    kv = _parse_props_kv(args.prop)
    json_props = _load_json_arg(args.props) if args.props else None
    if json_props is not None and not isinstance(json_props, dict):
        _die("--props must be a JSON object")
    props = _merge_props(kv, json_props)
    db.add_relationship(args.source, args.target, rel_type=args.type, **props)
    _ensure_parent(path)
    db.save()
    _print_json(
        {
            "status": "ok",
            "source": args.source,
            "target": args.target,
            "type": args.type,
        }
    )
    return OK


def cmd_add_rels(args: argparse.Namespace) -> int:
    """
    Add new relationships to the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    rels = _load_json_arg(args.rels)
    if not isinstance(rels, list):
        _die("--rels must be a JSON array of relationship dicts")
    db.add_relationships(rels)
    _ensure_parent(path)
    db.save()
    _print_json({"status": "ok", "inserted": len(rels)})
    return OK


def cmd_remove_node(args: argparse.Namespace) -> int:
    """
    Remove a node from the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    db.remove_node(args.id)
    _ensure_parent(path)
    db.save()
    _print_json({"status": "ok", "removed_node": args.id})
    return OK


def cmd_remove_rel(args: argparse.Namespace) -> int:
    """
    Remove a relationship from the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    db.remove_relationship(args.source, args.target)
    _ensure_parent(path)
    db.save()
    _print_json(
        {"status": "ok", "removed": {"source": args.source, "target": args.target}}
    )
    return OK


def cmd_find_nodes(args: argparse.Namespace) -> int:
    """
    Find nodes in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    conds = _load_json_arg(args.conds) if args.conds else {}
    if not isinstance(conds, dict):
        _die("--conds must be a JSON object")
    res = db.find_nodes(
        label=args.label,
        fields=args.fields,
        limit=args.limit,
        offset=args.offset,
        **conds,
    )
    data = res.as_list()
    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(data, pretty=args.pretty)
    return OK


def cmd_find_rels(args: argparse.Namespace) -> int:
    """
    Find relationships in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    conds = _load_json_arg(args.conds) if args.conds else {}
    if not isinstance(conds, dict):
        _die("--conds must be a JSON object")
    res = db.find_relationships(
        rel_type=args.type,
        fields=args.fields,
        limit=args.limit,
        offset=args.offset,
        **conds,
    )
    data = res.as_list()
    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(data, pretty=args.pretty)
    return OK


def cmd_match_node_path(args: argparse.Namespace) -> int:
    """
    Match a path of nodes in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    start = _load_json_arg(args.start)
    pattern = _load_json_arg(args.pattern)
    if not isinstance(start, dict):
        _die("--start must be a JSON object of node conditions")
    if not isinstance(pattern, list):
        _die("--pattern must be a JSON array of steps")
    out = db.match_node_path(
        start=start,
        pattern=pattern,
        return_nodes=not args.return_ids,
        node_fields=args.node_fields,
        direction=args.direction,
    )
    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(out, pretty=args.pretty)
    return OK


def cmd_match_full_path(args: argparse.Namespace) -> int:
    """
    Match a full path of nodes and relationships in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    start = _load_json_arg(args.start)
    pattern = _load_json_arg(args.pattern)
    if not isinstance(start, dict):
        _die("--start must be a JSON object of node conditions")
    if not isinstance(pattern, list):
        _die("--pattern must be a JSON array of steps")
    out = db.match_full_path(
        start=start,
        pattern=pattern,
        node_fields=args.node_fields,
        rel_fields=args.rel_fields,
        direction=args.direction,
    )
    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(out, pretty=args.pretty)
    return OK


def cmd_match_structured(args: argparse.Namespace) -> int:
    """
    Match a structured path of nodes and relationships in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    start = _load_json_arg(args.start)
    pattern = _load_json_arg(args.pattern)
    if not isinstance(start, dict):
        _die("--start must be a JSON object of node conditions")
    if not isinstance(pattern, list):
        _die("--pattern must be a JSON array of steps")
    out = db.match_path_structured(
        start=start,
        pattern=pattern,
        node_fields=args.node_fields,
        rel_fields=args.rel_fields,
        direction=args.direction,
    )
    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(out, pretty=args.pretty)
    return OK


def cmd_neighbors(args: argparse.Namespace) -> int:
    """
    Find the neighbors of a node in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    out = list(db.neighbors(args.id))
    _print_json(out, pretty=args.pretty)
    return OK


def cmd_degree(args: argparse.Namespace) -> int:
    """
    Find the degree of a node in the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    deg = db.degree(args.id)
    _print_json({"id": args.id, "degree": deg})
    return OK


def cmd_clear(args: argparse.Namespace) -> int:
    """
    Clear the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    db.clear()
    _ensure_parent(path)
    db.save()
    _print_json({"status": "ok", "cleared": True})
    return OK


def cmd_export(args: argparse.Namespace) -> int:
    """
    Export the graph data.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    if args.what == "graph":
        data = db.to_dict()
    elif args.what == "nodes":
        data = db.nodes()
    elif args.what == "relationships":
        data = db.relationships()
    else:
        _die("unknown export target, choose nodes, relationships, or graph")

    if args.out:
        _ensure_parent(args.out)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.out}")
    else:
        _print_json(data, pretty=args.pretty)
    return OK


def cmd_view(args: argparse.Namespace) -> int:
    """
    View the graph.
    args -- The command-line arguments.
    """
    path = _require_path(args.path)
    db = _open_db(path, args.directed)
    db.view()
    return OK


# --------------------------
# parser
# --------------------------


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """
    p = argparse.ArgumentParser(
        prog="coffy-graph",
        description="File-backed CLI for coffy.graph (networkx-based graph engine)",
    )
    p.add_argument("--path", required=True, help="Path to JSON file backing the graph")
    p.add_argument("--directed", action="store_true", help="Use a directed graph")
    sub = p.add_subparsers(dest="cmd", required=True)

    # init
    sp = sub.add_parser("init", help="Initialize a graph file")
    sp.set_defaults(func=cmd_init)

    # add-node
    sp = sub.add_parser("add-node", help="Add or update a node")
    sp.add_argument("--id", required=True, help="Node id")
    sp.add_argument(
        "--labels",
        help='Labels as CSV or JSON string, e.g. "Person,Employee" or ["Person"]',
    )
    sp.add_argument("--prop", action="append", help="Property key=value, can repeat")
    sp.add_argument("--props", help="JSON object, @file.json, or -")
    sp.set_defaults(func=cmd_add_node)

    # add-nodes
    sp = sub.add_parser("add-nodes", help="Bulk add nodes")
    sp.add_argument("nodes", help="JSON array of nodes, @file.json, or -")
    sp.set_defaults(func=cmd_add_nodes)

    # add-rel
    sp = sub.add_parser("add-rel", help="Add a relationship")
    sp.add_argument("--source", required=True, help="Source node id")
    sp.add_argument("--target", required=True, help="Target node id")
    sp.add_argument("--type", help="Relationship type")
    sp.add_argument("--prop", action="append", help="Property key=value, can repeat")
    sp.add_argument("--props", help="JSON object, @file.json, or -")
    sp.set_defaults(func=cmd_add_rel)

    # add-rels
    sp = sub.add_parser("add-rels", help="Bulk add relationships")
    sp.add_argument("rels", help="JSON array of relationships, @file.json, or -")
    sp.set_defaults(func=cmd_add_rels)

    # remove-node
    sp = sub.add_parser("remove-node", help="Remove a node")
    sp.add_argument("--id", required=True, help="Node id")
    sp.set_defaults(func=cmd_remove_node)

    # remove-rel
    sp = sub.add_parser("remove-rel", help="Remove a relationship")
    sp.add_argument("--source", required=True, help="Source node id")
    sp.add_argument("--target", required=True, help="Target node id")
    sp.set_defaults(func=cmd_remove_rel)

    # find-nodes
    sp = sub.add_parser("find-nodes", help="Find nodes by label and conditions")
    sp.add_argument("--label", help="Node label to filter")
    sp.add_argument("--conds", help="JSON object of conditions, @file.json, or -")
    sp.add_argument("--fields", nargs="+", help="Projection fields")
    sp.add_argument("--limit", type=int, help="Limit")
    sp.add_argument("--offset", type=int, help="Offset")
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_find_nodes)

    # find-rels
    sp = sub.add_parser("find-rels", help="Find relationships by type and conditions")
    sp.add_argument("--type", help="Relationship type to filter")
    sp.add_argument("--conds", help="JSON object of conditions, @file.json, or -")
    sp.add_argument("--fields", nargs="+", help="Projection fields")
    sp.add_argument("--limit", type=int, help="Limit")
    sp.add_argument("--offset", type=int, help="Offset")
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_find_rels)

    # match-node-path
    sp = sub.add_parser(
        "match-node-path",
        help="Return sequences of nodes or node ids for a path pattern",
    )
    sp.add_argument(
        "--start",
        required=True,
        help="JSON object of start-node conditions, @file.json, or -",
    )
    sp.add_argument(
        "--pattern", required=True, help="JSON array of steps, @file.json, or -"
    )
    sp.add_argument("--node-fields", nargs="+", help="Projection fields for nodes")
    sp.add_argument("--direction", choices=["out", "in", "any"], default="out")
    sp.add_argument(
        "--return-ids",
        action="store_true",
        help="Return node id sequences instead of node dicts",
    )
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_match_node_path)

    # match-full-path
    sp = sub.add_parser(
        "match-full-path", help="Return nodes and relationships along a path pattern"
    )
    sp.add_argument(
        "--start",
        required=True,
        help="JSON object of start-node conditions, @file.json, or -",
    )
    sp.add_argument(
        "--pattern", required=True, help="JSON array of steps, @file.json, or -"
    )
    sp.add_argument("--node-fields", nargs="+", help="Projection fields for nodes")
    sp.add_argument(
        "--rel-fields", nargs="+", help="Projection fields for relationships"
    )
    sp.add_argument("--direction", choices=["out", "in", "any"], default="out")
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_match_full_path)

    # match-structured
    sp = sub.add_parser(
        "match-structured", help="Return structured Cypher-like path objects"
    )
    sp.add_argument(
        "--start",
        required=True,
        help="JSON object of start-node conditions, @file.json, or -",
    )
    sp.add_argument(
        "--pattern", required=True, help="JSON array of steps, @file.json, or -"
    )
    sp.add_argument("--node-fields", nargs="+", help="Projection fields for nodes")
    sp.add_argument(
        "--rel-fields", nargs="+", help="Projection fields for relationships"
    )
    sp.add_argument("--direction", choices=["out", "in", "any"], default="out")
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_match_structured)

    # neighbors
    sp = sub.add_parser("neighbors", help="List neighbor node ids")
    sp.add_argument("--id", required=True, help="Node id")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_neighbors)

    # degree
    sp = sub.add_parser("degree", help="Get node degree")
    sp.add_argument("--id", required=True, help="Node id")
    sp.set_defaults(func=cmd_degree)

    # clear
    sp = sub.add_parser("clear", help="Clear the graph")
    sp.set_defaults(func=cmd_clear)

    # export
    sp = sub.add_parser("export", help="Export nodes, relationships, or entire graph")
    sp.add_argument("what", choices=["nodes", "relationships", "graph"])
    sp.add_argument("--out", help="Write results to JSON file")
    sp.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    sp.set_defaults(func=cmd_export)

    # view
    sp = sub.add_parser("view", help="Open interactive graph visualization")
    sp.set_defaults(func=cmd_view)

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
