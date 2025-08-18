# tests/test_sql_cli.py
# author: nsarathy

import unittest
from click.testing import CliRunner
from coffy.cli.sql_cli import sql_cli


class TestSQLCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_init_in_memory_db(self):
        result = self.runner.invoke(sql_cli, ["init"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Initialized SQL engine", result.output)

    def test_init_file_db(self):
        import tempfile

        db_path = tempfile.NamedTemporaryFile(delete=False).name
        result = self.runner.invoke(sql_cli, ["init", "--db", db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(db_path, result.output)

    def test_run_create_and_select(self):
        self.runner.invoke(sql_cli, ["init"])

        # CREATE TABLE
        result = self.runner.invoke(
            sql_cli, ["run", "CREATE TABLE test (id INTEGER, name TEXT)"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("success", result.output)

        # INSERT
        result = self.runner.invoke(
            sql_cli, ["run", "INSERT INTO test VALUES (1, 'Alice')"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("success", result.output)

        # SELECT
        result = self.runner.invoke(sql_cli, ["run", "SELECT * FROM test"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Alice", result.output)

    def test_view_select_opens_browser(self):
        opened = {}

        # Monkeypatch SQLDict.view to simulate browser opening
        import coffy.sql.sqldict

        def fake_view(self, title="SQL Query Results"):
            opened["called"] = True

        coffy.sql.sqldict.SQLDict.view = fake_view

        self.runner.invoke(sql_cli, ["init"])
        self.runner.invoke(
            sql_cli, ["run", "CREATE TABLE test (id INTEGER, name TEXT)"]
        )
        self.runner.invoke(sql_cli, ["run", "INSERT INTO test VALUES (1, 'Bob')"])

        result = self.runner.invoke(sql_cli, ["view", "SELECT * FROM test"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Opened query results in browser.", result.output)
        self.assertTrue(opened.get("called"))

    def test_view_non_select_query(self):
        self.runner.invoke(sql_cli, ["init"])
        result = self.runner.invoke(sql_cli, ["view", "CREATE TABLE test (id INTEGER)"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Not a SELECT query.", result.output)

    def test_close_connection(self):
        self.runner.invoke(sql_cli, ["init"])
        result = self.runner.invoke(sql_cli, ["close"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Closed SQL engine connection.", result.output)


print("SQL CLI tests:")

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestSQLCli))
