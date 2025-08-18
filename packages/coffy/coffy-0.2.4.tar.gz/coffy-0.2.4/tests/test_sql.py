# tests/test_sql.py
# author: nsarathy

from coffy.sql import init, query, close
import os
import tempfile
import unittest


class TestSQLModule(unittest.TestCase):
    def setUp(self):
        self.temp_db_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".sqlite"
        ).name
        init(self.temp_db_path)
        query("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        query("INSERT INTO users VALUES (1, 'Neel', 30)")
        query("INSERT INTO users VALUES (2, 'Tanaya', 25)")
        query("INSERT INTO users VALUES (3, 'Bea', 40)")

    def tearDown(self):
        close()
        os.remove(self.temp_db_path)

    def test_select_all(self):
        result = query("SELECT * FROM users")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "Neel")

    def test_select_where(self):
        result = query("SELECT * FROM users WHERE age > 30")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bea")

    def test_insert_and_count(self):
        query("INSERT INTO users VALUES (4, 'Carl', 22)")
        result = query("SELECT COUNT(*) as total FROM users")
        self.assertEqual(result[0]["total"], 4)

    def test_update_and_verify(self):
        query("UPDATE users SET age = 35 WHERE name = 'Neel'")
        result = query("SELECT age FROM users WHERE name = 'Neel'")
        self.assertEqual(result[0]["age"], 35)

    def test_delete(self):
        query("DELETE FROM users WHERE name = 'Tanaya'")
        result = query("SELECT * FROM users WHERE name = 'Tanaya'")
        self.assertEqual(len(result), 0)

    def test_error_handling(self):
        result = query("SELECT * FROM nonexistent")
        self.assertEqual(result["status"], "error")
        self.assertIn("no such table", result["message"])

    def test_repr_output(self):
        result = query("SELECT * FROM users WHERE id = 1")
        output = str(result)
        self.assertIn("Neel", output)
        self.assertIn("1 rows x 3 cols", output)

    def test_repr_output_empty(self):
        result = query("SELECT * FROM users WHERE id = 0")
        output = str(result)
        self.assertIn("<empty result>", output)
        self.assertIn("0 rows x 0 cols", output)

    def test_export_json_and_csv(self):
        result = query("SELECT * FROM users")
        temp_json = self.temp_db_path.replace(".sqlite", ".json")
        temp_csv = self.temp_db_path.replace(".sqlite", ".csv")
        result.to_json(temp_json)
        result.to_csv(temp_csv)
        self.assertTrue(os.path.exists(temp_json))
        self.assertTrue(os.path.exists(temp_csv))
        os.remove(temp_json)
        os.remove(temp_csv)

    def test_column_property(self):
        result = query("SELECT * FROM users WHERE id = 1")
        self.assertEqual(result.columns, ["id", "name", "age"])

    def test_column_property_empty(self):
        result = query("SELECT * FROM users WHERE 1=0")
        self.assertEqual(result.columns, [])

    def test_column_property_out_of_order(self):
        result = query("SELECT * FROM users ORDER BY age DESC")
        self.assertNotEqual(result.columns, ["id", "age", "name"])


print("SQL tests:")

unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestSQLModule)
)
