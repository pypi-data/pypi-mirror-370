# tests/test_sql_cli.py
# author: nsarathy

import io
import os
import csv
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

# Import the CLI entrypoint
from coffy.cli.sql_cli import main as cli_main


class TestSQLCli(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.db_path = os.path.join(self.tmpdir.name, "test.sqlite")

    def _run(self, argv, expect_exit=False):
        """
        Run cli_main with argv, capture stdout and stderr.
        If expect_exit is True, catches SystemExit and returns its code.
        Returns (code, stdout, stderr).
        """
        out = io.StringIO()
        err = io.StringIO()
        code = 0
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = cli_main(argv)
                # Some implementations return None, normalize to 0
                if code is None:
                    code = 0
            except SystemExit as e:
                if expect_exit:
                    code = int(e.code) if isinstance(e.code, int) else 1
                else:
                    # Unexpected hard exit, re-raise to fail the test
                    raise
        return code, out.getvalue(), err.getvalue()

    def test_init_creates_db(self):
        code, out, err = self._run(["--db", self.db_path, "init"])
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(self.db_path))
        self.assertIn("initialized", out.lower())

    def _seed_users_table(self):
        # Ensure DB exists
        self._run(["--db", self.db_path, "init"])

        # Create table and insert rows using a single run with multiple statements
        sql = (
            "CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT);"
            "DELETE FROM users;"
            "INSERT INTO users VALUES (1,'Neel');"
            "INSERT INTO users VALUES (2,'Tanaya');"
        )
        code, out, err = self._run(["--db", self.db_path, "run", sql])
        self.assertEqual(code, 0, msg=err)

    def test_run_select_as_json(self):
        self._seed_users_table()
        code, out, err = self._run(
            ["--db", self.db_path, "run", "SELECT * FROM users ORDER BY id", "--json"]
        )
        self.assertEqual(code, 0, msg=err)
        rows = json.loads(out)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["id"], 1)
        self.assertEqual(rows[0]["name"], "Neel")
        self.assertEqual(rows[1]["id"], 2)
        self.assertEqual(rows[1]["name"], "Tanaya")

    def test_run_from_file_and_pretty_json(self):
        self._seed_users_table()
        sql_path = os.path.join(self.tmpdir.name, "q.sql")
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("SELECT name FROM users WHERE id > 1")
        code, out, err = self._run(
            ["--db", self.db_path, "run", f"@{sql_path}", "--json", "--pretty"]
        )
        self.assertEqual(code, 0, msg=err)
        # Pretty JSON should contain newlines and spaces, but most importantly it must be valid
        data = json.loads(out)
        self.assertEqual(data, [{"name": "Tanaya"}])
        self.assertIn("\n", out)

    def test_export_json(self):
        self._seed_users_table()
        out_path = os.path.join(self.tmpdir.name, "users.json")
        code, out, err = self._run(
            [
                "--db",
                self.db_path,
                "export",
                "SELECT * FROM users ORDER BY id",
                "--out",
                out_path,
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Neel")

    def test_export_csv(self):
        self._seed_users_table()
        out_path = os.path.join(self.tmpdir.name, "users.csv")
        code, out, err = self._run(
            [
                "--db",
                self.db_path,
                "export",
                "SELECT * FROM users ORDER BY id",
                "--out",
                out_path,
            ]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8", newline="") as f:
            reader = list(csv.reader(f))
        # Header + 2 rows
        self.assertGreaterEqual(len(reader), 3)
        header = [h.strip().lower() for h in reader[0]]
        self.assertIn("id", header)
        self.assertIn("name", header)

    def test_run_with_out_exports_last_select(self):
        self._seed_users_table()
        out_path = os.path.join(self.tmpdir.name, "last.csv")
        # Mixed statements, last one is SELECT and should be exported
        sql = (
            "CREATE TABLE IF NOT EXISTS t(a INT);"
            "INSERT INTO t VALUES(1);"
            "SELECT * FROM users ORDER BY id"
        )
        code, out, err = self._run(
            ["--db", self.db_path, "run", sql, "--out", out_path]
        )
        self.assertEqual(code, 0, msg=err)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Neel", content)
        self.assertIn("Tanaya", content)

    def test_reject_in_memory_db(self):
        # Using :memory: should be rejected, the CLI is expected to sys.exit(1)
        code, out, err = self._run(["--db", ":memory:", "init"], expect_exit=True)
        self.assertNotEqual(code, 0)
        self.assertIn("in-memory", err.lower())

    def test_export_requires_select(self):
        # Non-SELECT for export should error
        self._run(["--db", self.db_path, "init"])
        code, out, err = self._run(
            [
                "--db",
                self.db_path,
                "export",
                "CREATE TABLE x(y INT)",
                "--out",
                os.path.join(self.tmpdir.name, "x.csv"),
            ],
            expect_exit=True,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("requires a select", err.lower())

    def test_run_errors_on_missing_sql(self):
        # Empty SQL string should error
        self._run(["--db", self.db_path, "init"])
        code, out, err = self._run(
            ["--db", self.db_path, "run", "   "], expect_exit=True
        )
        self.assertNotEqual(code, 0)
        self.assertIn("no sql to execute", err.lower())


print("SQL CLI tests...")
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestSQLCli))
