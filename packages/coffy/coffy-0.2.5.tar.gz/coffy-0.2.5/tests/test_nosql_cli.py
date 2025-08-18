# tests/test_nosql_cli.py
# author: nsarathy

import io
import os
import re
import sys
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

# Under test
from coffy.cli.nosql_cli import main as cli_main


class TestNoSQLCli(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.db_path = os.path.join(self.tmpdir.name, "users.json")
        self.collection = "users"

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

    def _seed(self):
        # init
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        # add one
        self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add",
                '{"id":1,"name":"Neel","age":30,"address":{"city":"Indy"}}',
            ]
        )
        # add-many
        self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add-many",
                '[{"id":2,"name":"Bea","age":25},{"id":3,"name":"Carl","age":40}]',
            ]
        )

    # ---------- init ----------

    def test_init_creates_file(self):
        code, out, err = self._run(
            ["--collection", self.collection, "--path", self.db_path, "init"]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(self.db_path))
        self.assertIn("initialized collection", out.lower())

    # ---------- add / add-many ----------

    def test_add_one_json_string(self):
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add",
                '{"id":10,"name":"Ada","age":28}',
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"inserted": 1', out)

    def test_add_many_array_string(self):
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add-many",
                '[{"id":20,"name":"Bob"},{"id":21,"name":"Cam"}]',
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertRegex(out, r'{"inserted":\s*2}')

    def test_add_via_stdin(self):
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        code, out, err = self._run(
            ["--collection", self.collection, "--path", self.db_path, "add", "-"],
            stdin_data='{"id":30,"name":"Eve"}',
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"inserted": 1', out)

    def test_add_many_via_file(self):
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        many_path = os.path.join(self.tmpdir.name, "many.json")
        with open(many_path, "w", encoding="utf-8") as f:
            json.dump([{"id": 41, "name": "Drew"}, {"id": 42, "name": "Elle"}], f)
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add-many",
                f"@{many_path}",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertIn('"inserted": 2', out)

    # ---------- query, happy paths ----------

    def test_query_count_numeric_parsing(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gt",
                "--value",
                "29",
                "--count",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(out.strip().isdigit())
        self.assertEqual(int(out.strip()), 2)  # 30 and 40

    def test_query_first_eq(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "name",
                "--op",
                "eq",
                "--value",
                "Neel",
                "--first",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        doc = json.loads(out)
        self.assertEqual(doc["id"], 1)

    def test_query_in_and_nin(self):
        self._seed()
        # in
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "in",
                "--value",
                "[25,40]",
                "--count",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 2)
        # nin
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "nin",
                "--value",
                "[25,40]",
                "--count",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 1)

    def test_query_matches_regex(self):
        self._seed()
        # names starting with B or C
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "name",
                "--op",
                "matches",
                "--value",
                "^(B|C)",
                "--count",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 2)

    def test_query_exists_nested(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "address.city",
                "--op",
                "exists",
                "--count",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 1)

    def test_query_projection_and_outfile(self):
        self._seed()
        out_dir = os.path.join(self.tmpdir.name, "out")
        out_file = os.path.join(out_dir, "proj.json")
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gte",
                "--value",
                "25",
                "--fields",
                "id",
                "name",
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
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertNotIn("age", data[0])

    def test_query_pretty_flag_changes_format(self):
        self._seed()
        # pretty off
        code, out_compact, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gte",
                "--value",
                "25",
            ]
        )
        # pretty on
        code, out_pretty, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gte",
                "--value",
                "25",
                "--pretty",
            ]
        )
        self.assertTrue(len(out_pretty) > len(out_compact))
        self.assertIn("\n", out_pretty)

    # ---------- agg and clear ----------

    def test_agg_count_sum_avg_min_max(self):
        self._seed()
        # count
        code, out, err = self._run(
            ["--collection", self.collection, "--path", self.db_path, "agg", "count"]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 3)
        # sum
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "agg",
                "sum",
                "--field",
                "age",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(float(out.strip())), 95)
        # avg
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "agg",
                "avg",
                "--field",
                "age",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(re.match(r"3[0-9]\.\d+", out.strip()))  # ~31.6
        # min
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "agg",
                "min",
                "--field",
                "age",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 25)
        # max
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "agg",
                "max",
                "--field",
                "age",
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(int(out.strip()), 40)

    def test_clear_then_count_zero(self):
        self._seed()
        code, out, err = self._run(
            ["--collection", self.collection, "--path", self.db_path, "clear"]
        )
        self.assertEqual(code, 0, msg=err)
        res = json.loads(out)
        self.assertIn("cleared", res)
        code, out, err = self._run(
            ["--collection", self.collection, "--path", self.db_path, "agg", "count"]
        )
        self.assertEqual(int(out.strip()), 0)

    # ---------- failures and edge cases ----------

    def test_reject_in_memory_path(self):
        code, out, err = self._run(
            ["--collection", self.collection, "--path", ":memory:", "init"],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("in-memory", err.lower())

    def test_reject_wrong_extension(self):
        bad_path = os.path.join(self.tmpdir.name, "store.txt")
        code, out, err = self._run(
            ["--collection", self.collection, "--path", bad_path, "init"],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("must end with .json", err.lower())

    def test_add_many_requires_array(self):
        self._run(["--collection", self.collection, "--path", self.db_path, "init"])
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "add-many",
                '{"id":1}',
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("requires a json array", err.lower())

    def test_query_missing_value_for_gt(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gt",
                "--count",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--value is required for op 'gt'", err.lower())

    def test_query_value_provided_for_exists(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "exists",
                "--value",
                "1",
                "--count",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("must not be provided for op 'exists'", err.lower())

    def test_query_conflicting_flags_blocked_by_parser(self):
        # argparse mutually exclusive group should raise SystemExit automatically
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gt",
                "--value",
                "0",
                "--count",
                "--first",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)

    def test_in_nin_value_must_be_array(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "in",
                "--value",
                "30",
                "--count",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("must be a json array", err.lower())

    def test_query_out_creates_parent_dir(self):
        self._seed()
        out_file = os.path.join(self.tmpdir.name, "nested", "dir", "out.json")
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "gte",
                "--value",
                "25",
                "--out",
                out_file,
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(out_file))

    def test_query_unsupported_op(self):
        self._seed()
        code, out, err = self._run(
            [
                "--collection",
                self.collection,
                "--path",
                self.db_path,
                "query",
                "--field",
                "age",
                "--op",
                "weirdop",
                "--value",
                "1",
                "--count",
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("unsupported operator", err.lower())


print("NoSQL CLI tests...")
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestNoSQLCli))
