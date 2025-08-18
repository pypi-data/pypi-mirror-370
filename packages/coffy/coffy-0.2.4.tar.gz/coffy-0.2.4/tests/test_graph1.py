# coffy/tests/test_graph1.py
# author: nsarathy

from coffy.graph import GraphDB
import os
import tempfile
import unittest


class TestGraphDB1(unittest.TestCase):

    def setUp(self):
        self.temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        self.db = GraphDB(path=self.temp_path)
        self.db.add_node("A", labels="Person", name="Alice", age=30)
        self.db.add_node("B", labels="Person", name="Bob", age=25)
        self.db.add_node("C", labels="Person", name="Carol", age=40)
        self.db.add_relationship("A", "B", rel_type="KNOWS", since=2010)
        self.db.add_relationship("B", "C", rel_type="KNOWS", since=2015)

        # Create directed graph
        self.temp_path_directed = tempfile.NamedTemporaryFile(
            delete=False, suffix="_directed.json"
        ).name
        self.directed_db = GraphDB(directed=True, path=self.temp_path_directed)
        self.directed_db.add_node("A")
        self.directed_db.add_node("B")
        self.directed_db.add_node("C")
        self.directed_db.add_relationship("A", "B", _type="KNOWS")
        self.directed_db.add_relationship("B", "C", _type="KNOWS")

    def tearDown(self):
        os.remove(self.temp_path)

    def test_sanity(self):
        self.assertIsNotNone(self.db)
        self.assertIsNotNone(self.directed_db)


print("Graph tests 1:")

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestGraphDB1))
