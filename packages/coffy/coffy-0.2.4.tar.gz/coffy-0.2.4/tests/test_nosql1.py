# coffy/tests/test_nosql1.py
# author: nsarathy

from coffy.nosql import db
import unittest


class TestNoSQLDB(unittest.TestCase):

    def setUp(self):
        self.col = db(collection_name="test_collection")
        self.col.clear()
        self.col.add_many(
            [
                {"name": "Alice", "age": 30, "tags": ["x", "y"]},
                {"name": "Bob", "age": 25, "tags": ["y", "z"]},
                {"name": "Carol", "age": 40, "nested": {"score": 100}},
            ]
        )

    def test_sanity(self):
        self.assertIsNotNone(self.col)


print("NoSQL tests 1:")

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestNoSQLDB))
