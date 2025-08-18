# tests/test_graph_cli.py
# author: nsarathy

import io
import os
import sys
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

# Under test
from coffy.cli.graph_cli import main as cli_main


class TestGraphCli(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.graph_path = os.path.join(self.tmpdir.name, "graph.json")

    # ---------- harness ----------

    def _run(self, argv, expect_exit=False, stdin_data=None):
        """
        Run cli_main with argv, capture stdout and stderr.
        Returns (code, stdout_str, stderr_str).
        If expect_exit is True, catches SystemExit and returns its code.
        """
        out = io.StringIO()
        err = io.StringIO()
        old_stdin = sys.stdin
        if stdin_data is not None:
            sys.stdin = io.StringIO(stdin_data)

        code = 0
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = cli_main(argv)
                if code is None:
                    code = 0
            except SystemExit as e:
                if expect_exit:
                    code = int(e.code) if isinstance(e.code, int) else 1
                else:
                    raise
            finally:
                if stdin_data is not None:
                    sys.stdin = old_stdin
        return code, out.getvalue(), err.getvalue()

    def _init_directed(self, directed=False):
        argv = ["--path", self.graph_path]
        if directed:
            argv.append("--directed")
        argv += ["init"]
        code, out, err = self._run(argv)
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(self.graph_path))
        return out

    def _seed_small_graph(self, directed=False):
        self._init_directed(directed=directed)
        # Add nodes, using Windows-friendly --prop
        self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "A",
                "--labels",
                "Person",
                "--prop",
                "name=Alice",
                "--prop",
                "age=30",
            ]
        )
        self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "B",
                "--labels",
                "Person",
                "--prop",
                "name=Bob",
                "--prop",
                "age=25",
            ]
        )
        self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "C",
                "--labels",
                "Company",
                "--prop",
                "name=Acme",
            ]
        )
        # Relationship
        self._run(
            [
                "--path",
                self.graph_path,
                "add-rel",
                "--source",
                "A",
                "--target",
                "B",
                "--type",
                "KNOWS",
                "--prop",
                "since=2010",
            ]
        )
        self._run(
            [
                "--path",
                self.graph_path,
                "add-rel",
                "--source",
                "B",
                "--target",
                "C",
                "--type",
                "WORKS_AT",
                "--prop",
                "title=Engineer",
            ]
        )

    # ---------- init ----------

    def test_init_creates_file(self):
        code, out, err = self._run(["--path", self.graph_path, "init"])
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(self.graph_path))
        self.assertIn("initialized graph", out.lower())

    def test_init_directed_flag(self):
        out = self._init_directed(directed=True)
        self.assertIn("directed=True", out)

    # ---------- add-node / add-nodes ----------

    def test_add_node_with_prop_and_props_json(self):
        self._init_directed()
        # props via JSON file plus --prop override
        props_file = os.path.join(self.tmpdir.name, "props.json")
        with open(props_file, "w", encoding="utf-8") as f:
            json.dump({"name": "Alice", "age": 20, "city": "X"}, f)
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "A",
                "--labels",
                '["Person","Employee"]',
                "--props",
                f"@{props_file}",
                "--prop",
                "age=30",  # override
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"node_id": "A"', out)

        # Validate via find-nodes projection
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-nodes",
                "--label",
                "Person",
                "--conds",
                '{"name":"Alice"}',
                "--fields",
                "id",
                "name",
                "age",
                "city",
            ]
        )
        data = json.loads(out)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "A")
        self.assertEqual(data[0]["age"], 30)
        self.assertEqual(data[0]["city"], "X")

    def test_add_nodes_bulk_from_stdin(self):
        self._init_directed()
        payload = json.dumps(
            [
                {"id": "X1", "labels": ["Person"], "name": "P1"},
                {"id": "X2", "labels": "Company", "name": "C1"},
            ]
        )
        code, out, err = self._run(
            ["--path", self.graph_path, "add-nodes", "-"], stdin_data=payload
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"inserted": 2', out)

    # ---------- add-rel / add-rels ----------

    def test_add_rel_with_prop_and_props(self):
        self._init_directed()
        # Add nodes first
        self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "A",
                "--labels",
                "Person",
                "--prop",
                "name=Alice",
            ]
        )
        self._run(
            [
                "--path",
                self.graph_path,
                "add-node",
                "--id",
                "B",
                "--labels",
                "Person",
                "--prop",
                "name=Bob",
            ]
        )
        # Relationship with mix of props
        props_file = os.path.join(self.tmpdir.name, "relprops.json")
        with open(props_file, "w", encoding="utf-8") as f:
            json.dump({"since": 2009, "weight": 0.5}, f)
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "add-rel",
                "--source",
                "A",
                "--target",
                "B",
                "--type",
                "KNOWS",
                "--props",
                f"@{props_file}",
                "--prop",
                "since=2010",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"source": "A"', out)
        self.assertIn('"type": "KNOWS"', out)

    def test_add_rels_bulk(self):
        self._seed_small_graph()
        rels_file = os.path.join(self.tmpdir.name, "rels.json")
        with open(rels_file, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {"source": "A", "target": "C", "type": "LIKES", "weight": 0.9},
                    {"source": "C", "target": "A", "type": "EMPLOYS"},
                ],
                f,
            )
        code, out, err = self._run(
            ["--path", self.graph_path, "add-rels", f"@{rels_file}"]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"inserted": 2', out)

    # ---------- find-nodes / find-rels ----------

    def test_find_nodes_with_conditions_or_logic(self):
        self._seed_small_graph()
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-nodes",
                "--label",
                "Person",
                "--conds",
                '{"_logic":"or","name":"Alice","age":{"gt":35}}',
                "--pretty",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        data = json.loads(out)
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(any(d.get("name") == "Alice" for d in data))

    def test_find_nodes_projection_limit_offset(self):
        self._seed_small_graph()
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-nodes",
                "--label",
                "Person",
                "--conds",
                "{}",
                "--fields",
                "id",
                "name",
                "--limit",
                "1",
                "--offset",
                "1",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(len(data), 1)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertNotIn("age", data[0])

    def test_find_rels_by_type_and_cond(self):
        self._seed_small_graph(directed=True)
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "--directed",
                "find-rels",
                "--type",
                "WORKS_AT",
                "--conds",
                '{"title":"Engineer"}',
                "--fields",
                "source",
                "target",
                "title",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        rows = json.loads(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "B")
        self.assertEqual(rows[0]["target"], "C")
        self.assertEqual(rows[0]["title"], "Engineer")

    # ---------- neighbors / degree ----------

    def test_neighbors_and_degree(self):
        self._seed_small_graph(directed=False)
        # neighbors of A should include B and possibly C after add-rels test, but here just B
        code, out, err = self._run(
            ["--path", self.graph_path, "neighbors", "--id", "A"]
        )
        self.assertEqual(code, 0, msg=err)
        nbrs = json.loads(out)
        self.assertIn("B", nbrs)
        # degree
        code, out, err = self._run(["--path", self.graph_path, "degree", "--id", "A"])
        self.assertEqual(code, 0, msg=err)
        d = json.loads(out)
        self.assertEqual(d["id"], "A")
        self.assertGreaterEqual(d["degree"], 1)

    # ---------- matchers ----------

    def test_match_node_path_and_full_and_structured(self):
        self._seed_small_graph(directed=True)
        # Node path: Alice -[KNOWS]-> Bob
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "--directed",
                "match-node-path",
                "--start",
                '{"name":"Alice"}',
                "--pattern",
                '[{"rel_type":"KNOWS","node":{"name":"Bob"}}]',
                "--node-fields",
                "id",
                "name",
                "--pretty",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        seqs = json.loads(out)
        self.assertGreaterEqual(len(seqs), 1)
        # Full path includes nodes and rels
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "--directed",
                "match-full-path",
                "--start",
                '{"name":"Alice"}',
                "--pattern",
                '[{"rel_type":"KNOWS","node":{"name":"Bob"}}]',
                "--node-fields",
                "id",
                "name",
                "--rel-fields",
                "type",
                "since",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        full = json.loads(out)
        self.assertGreaterEqual(len(full), 1)
        # Structured
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "--directed",
                "match-structured",
                "--start",
                '{"name":"Alice"}',
                "--pattern",
                '[{"rel_type":"KNOWS","node":{"name":"Bob"}}]',
            ]
        )
        self.assertEqual(code, 0, msg=err)
        structured = json.loads(out)
        self.assertGreaterEqual(len(structured), 1)

    # ---------- export / clear / remove ----------

    def test_export_nodes_relationships_graph_and_clear(self):
        self._seed_small_graph()
        # export nodes
        code, out, err = self._run(["--path", self.graph_path, "export", "nodes"])
        self.assertEqual(code, 0, msg=err)
        nodes = json.loads(out)
        self.assertGreaterEqual(len(nodes), 3)
        # export relationships
        code, out, err = self._run(
            ["--path", self.graph_path, "export", "relationships"]
        )
        self.assertEqual(code, 0, msg=err)
        rels = json.loads(out)
        self.assertGreaterEqual(len(rels), 2)
        # export graph
        code, out, err = self._run(["--path", self.graph_path, "export", "graph"])
        self.assertEqual(code, 0, msg=err)
        g = json.loads(out)
        self.assertIn("nodes", g)
        self.assertIn("relationships", g)
        # clear
        code, out, err = self._run(["--path", self.graph_path, "clear"])
        self.assertEqual(code, 0, msg=err)
        res = json.loads(out)
        self.assertTrue(res.get("cleared"))

    def test_remove_node_and_relationship(self):
        self._seed_small_graph()
        # remove relationship A->B
        code, out, err = self._run(
            ["--path", self.graph_path, "remove-rel", "--source", "A", "--target", "B"]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"removed"', out)
        # remove node B
        code, out, err = self._run(
            ["--path", self.graph_path, "remove-node", "--id", "B"]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"removed_node": "B"', out)

    # ---------- out to file ----------

    def test_find_nodes_out_creates_parent(self):
        self._seed_small_graph()
        out_file = os.path.join(self.tmpdir.name, "sub", "dir", "nodes.json")
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-nodes",
                "--label",
                "Person",
                "--conds",
                "{}",
                "--out",
                out_file,
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(out_file))
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertGreaterEqual(len(data), 2)

    # ---------- failures and edge cases ----------

    def test_reject_in_memory_and_wrong_extension(self):
        code, out, err = self._run(["--path", ":memory:", "init"], expect_exit=True)
        self.assertNotEqual(code, 0)
        self.assertIn("in-memory graphs are not allowed", err.lower())
        bad = os.path.join(self.tmpdir.name, "g.txt")
        code, out, err = self._run(["--path", bad, "init"], expect_exit=True)
        self.assertNotEqual(code, 0)
        self.assertIn("must end with .json", err.lower())

    def test_add_nodes_requires_array(self):
        self._init_directed()
        code, out, err = self._run(
            ["--path", self.graph_path, "add-nodes", '{"id":"X"}'], expect_exit=True
        )
        self.assertNotEqual(code, 0)
        self.assertIn("json array of node dicts", err.lower())

    def test_add_rels_requires_array(self):
        self._init_directed()
        code, out, err = self._run(
            ["--path", self.graph_path, "add-rels", '{"source":"A","target":"B"}'],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("json array of relationship dicts", err.lower())

    def test_find_nodes_conds_must_be_object(self):
        self._seed_small_graph()
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-nodes",
                "--label",
                "Person",
                "--conds",
                "[]",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("must be a json object", err.lower())

    def test_matchers_require_object_and_array(self):
        self._seed_small_graph()
        # start must be object
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "match-node-path",
                "--start",
                "[]",
                "--pattern",
                "[]",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--start must be a json object", err.lower())
        # pattern must be array
        code, out, err = self._run(
            [
                "--path",
                self.graph_path,
                "match-full-path",
                "--start",
                "{}",
                "--pattern",
                "{}",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--pattern must be a json array", err.lower())

    def test_pretty_flag_changes_size(self):
        self._seed_small_graph()
        code, out1, err = self._run(
            ["--path", self.graph_path, "find-rels", "--type", "KNOWS", "--conds", "{}"]
        )
        code, out2, err = self._run(
            [
                "--path",
                self.graph_path,
                "find-rels",
                "--type",
                "KNOWS",
                "--conds",
                "{}",
                "--pretty",
            ]
        )
        self.assertTrue(len(out2) > len(out1))


print("Graph CLI tests...")
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestGraphCli))
