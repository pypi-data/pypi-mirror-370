# coffy/nosql/nosql_tests.py
# author: nsarathy

from coffy.nosql import db
import json
import os
import tempfile
import unittest


class TestCollectionManager(unittest.TestCase):

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

    def test_add_and_all_docs(self):
        result = self.col.all_docs()
        self.assertEqual(len(result), 3)

    def test_add_list(self):
        self.col.add({"name": "Dave", "age": 35, "tags": ["x", "z"]})
        result = self.col.all_docs()
        self.assertEqual(len(result), 4)

    def test_where_eq(self):
        q = self.col.where("name").eq("Alice")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["age"], 30)

    def test_where_gt_and_lt(self):
        gt_q = self.col.where("age").gt(26)
        lt_q = self.col.where("age").lt(40)
        self.assertEqual(gt_q.count(), 2)
        self.assertEqual(lt_q.count(), 2)

    def test_between(self):
        q = self.col.where("age").between(25, 35)
        self.assertEqual(q.count(), 2)
        self.assertEqual(q.first()["name"], "Alice")

        q = self.col.where("age").between(30, 25)
        self.assertEqual(q.count(), 2)
        self.assertEqual(q.first()["name"], "Alice")

        q = self.col.where("age").between(27, 35)
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_exists(self):
        q = self.col.where("nested").exists()
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_in_and_nin(self):
        q1 = self.col.where("name").in_(["Alice", "Bob"])
        q2 = self.col.where("name").nin(["Carol"])
        self.assertEqual(q1.count(), 2)
        self.assertEqual(q2.count(), 2)

    def test_matches(self):
        q = self.col.where("name").matches("^A")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_nested_field_access(self):
        q = self.col.where("nested.score").eq(100)
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_logic_and_or_not(self):
        q = self.col.match_all(
            lambda q: q.where("age").gte(25), lambda q: q.where("age").lt(40)
        )
        self.assertEqual(q.count(), 2)

        q = self.col.match_any(
            lambda q: q.where("name").eq("Alice"), lambda q: q.where("name").eq("Bob")
        )
        self.assertEqual(q.count(), 2)

        q = self.col.not_any(
            lambda q: q.where("name").eq("Bob"), lambda q: q.where("age").eq(40)
        )
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_run_with_projection(self):
        q = self.col.where("age").gte(25)
        result = q.run(fields=["name"])
        self.assertEqual(len(result), 3)
        for doc in result:
            self.assertEqual(list(doc.keys()), ["name"])

    def test_update_and_delete_and_replace(self):
        self.col.where("name").eq("Alice").update({"updated": True})
        updated = self.col.where("updated").eq(True).first()
        self.assertEqual(updated["name"], "Alice")

        self.col.where("name").eq("Bob").delete()
        self.assertEqual(self.col.where("name").eq("Bob").count(), 0)

        self.col.where("name").eq("Carol").replace({"name": "New", "age": 99})
        new_doc = self.col.where("name").eq("New").first()
        self.assertEqual(new_doc["age"], 99)

    def test_aggregates(self):
        self.assertEqual(self.col.sum("age"), 95)
        self.assertEqual(self.col.avg("age"), 95 / 3)
        self.assertEqual(self.col.min("age"), 25)
        self.assertEqual(self.col.max("age"), 40)

    def test_merge(self):
        q = self.col.where("name").eq("Alice")
        merged = q.merge(lambda d: {"new": d["age"] + 10}).run()
        self.assertEqual(merged[0]["new"], 40)

    def test_sort_ascending(self):
        """Test sorting in ascending order."""
        sorter_db = db("sorter_asc", path=":memory:")
        sorter_db.add_many(
            [
                {"name": "Carol", "age": 40},
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        )
        result = sorter_db.where("age").exists().sort("age").run().as_list()
        ages = [doc["age"] for doc in result]
        self.assertEqual(ages, [25, 30, 40])

    def test_sort_descending(self):
        """Test sorting in descending order."""
        sorter_db = db("sorter_desc", path=":memory:")
        sorter_db.add_many(
            [
                {"name": "Carol", "age": 40},
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        )
        result = (
            sorter_db.where("age").exists().sort("age", reverse=True).run().as_list()
        )
        ages = [doc["age"] for doc in result]
        self.assertEqual(ages, [40, 30, 25])

    def test_sort_with_missing_and_mixed_fields(self):
        """Test that documents with missing and mixed sort keys are at the end."""
        sorter_db = db("sorter_mixed", path=":memory:")
        sorter_db.add_many(
            [
                {"name": "David", "tags": ["z"]},
                {"name": "Carol", "age": 40},
                {"name": "Kevin", "age": "twenty"},
                {"name": "Bob", "age": 25},
            ]
        )
        result = sorter_db.where("name").exists().sort("age").run().as_list()
        names = [doc["name"] for doc in result]
        self.assertEqual(names, ["Bob", "Carol", "Kevin", "David"])

    def test_sort_on_nested_field(self):
        """Test sorting on a nested field."""
        self.col.add({"name": "Zane", "nested": {"score": 50}})
        result = (
            self.col.where("nested.score").exists().sort("nested.score").run().as_list()
        )
        scores = [doc["nested"]["score"] for doc in result]
        self.assertEqual(scores, [50, 100])

    def test_sort_empty_result(self):
        """Test sorting on a query with no results."""
        result = self.col.where("name").eq("NoSuchName").sort("age").run()
        self.assertEqual(len(result), 0)

    def test_sort_stability(self):
        """Test that the sort is stable."""
        sorter_db = db("sorter_stable", path=":memory:")
        sorter_db.add_many(
            [
                {"name": "Alice", "age": 30, "order": 1},
                {"name": "Adam", "age": 30, "order": 2},
            ]
        )
        result = sorter_db.where("age").eq(30).sort("age").run().as_list()
        names = [doc["name"] for doc in result]
        self.assertEqual(names, ["Alice", "Adam"], "Sort should be stable")

    def test_lookup_and_merge_pipeline(self):
        users = db("users")
        orders = db("orders")
        users.clear()
        orders.clear()
        users.add_many([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        orders.add_many(
            [
                {"order_id": 101, "user_id": 1, "total": 50},
                {"order_id": 102, "user_id": 1, "total": 70},
                {"order_id": 103, "user_id": 2, "total": 20},
            ]
        )

        # Only simulate one-to-one (latest order per user) manually
        latest_by_user = {
            103: {"user_id": 2, "total": 20},
            102: {"user_id": 1, "total": 70},
        }
        db("latest_orders").clear()
        db("latest_orders").add_many(list(latest_by_user.values()))

        result = (
            users.lookup(
                "latest_orders",
                local_key="id",
                foreign_key="user_id",
                as_field="latest",
                many=False,
            )
            .merge(lambda d: {"latest_total": d.get("latest", {}).get("total", 0)})
            .run()
            .as_list()
        )
        totals = {d["name"]: d["latest_total"] for d in result}
        self.assertEqual(totals["Alice"], 70)
        self.assertEqual(totals["Bob"], 20)

    def test_doclist_to_json(self):
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        result = self.col.where("name").eq("Alice").run(fields=["name", "age"])
        result.to_json(path)

        with open(path) as f:
            data = json.load(f)
        self.assertEqual(data[0]["name"], "Alice")
        os.remove(path)

    def test_import_collection(self):
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        with open(path, "w", encoding="utf-8") as f:
            json.dump([{"name": "Imported", "age": 99}], f)

        self.col.import_(path)
        self.assertEqual(len(self.col.all()), 1)
        self.assertEqual(self.col.first()["name"], "Imported")
        os.remove(path)

    def test_import_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.col.import_("nonexistent.json")

    def test_replace_multiple_with_empty_doc(self):
        result = self.col.where("age").gte(25).replace({})
        self.assertEqual(result["replaced"], 3)
        all_docs = self.col.all()
        self.assertTrue(all(isinstance(d, dict) and not d for d in all_docs))

    def test_limit_only(self):
        result = self.col.where("age").gte(0).limit(2).run(fields=["name"])
        self.assertEqual(len(result), 2)

    def test_offset_only(self):
        result = self.col.where("age").gte(0).offset(1).run(fields=["name"])
        self.assertEqual(len(result), 2)

    def test_limit_and_offset(self):
        result = self.col.where("age").gte(0).offset(1).limit(1).run(fields=["name"])
        self.assertEqual(len(result), 1)

    def test_offset_out_of_range(self):
        result = self.col.where("age").gte(0).offset(100).run()
        self.assertEqual(len(result), 0)

    def test_limit_zero(self):
        result = self.col.where("age").gte(0).limit(0).run()
        self.assertEqual(len(result), 0)

    def test_lookup_many_orders_and_merge_total(self):
        users = db("multi_users")
        orders = db("multi_orders")
        users.clear()
        orders.clear()

        users.add_many(
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Carol"},
            ]
        )
        orders.add_many(
            [
                {"order_id": 101, "user_id": 1, "total": 10},
                {"order_id": 102, "user_id": 1, "total": 15},
                {"order_id": 103, "user_id": 2, "total": 20},
                {"order_id": 104, "user_id": 2, "total": 30},
                {"order_id": 105, "user_id": 2, "total": 25},
                # Carol has no orders
            ]
        )

        result = (
            users.lookup("multi_orders", "id", "user_id", "orders", many=True)
            .merge(lambda u: {"total_spent": sum(o["total"] for o in u["orders"])})
            .run()
            .as_list()
        )

        totals = {u["name"]: u["total_spent"] for u in result}
        self.assertEqual(totals["Alice"], 25)  # 10 + 15
        self.assertEqual(totals["Bob"], 75)  # 20 + 30 + 25
        self.assertEqual(totals["Carol"], 0)  # no orders

    def test_chained_query_with_logic_aggregate_and_find(self):
        users = db("logic_users")
        orders = db("logic_orders")
        users.clear()
        orders.clear()

        users.add_many(
            [
                {"id": 1, "name": "Neel", "vip": True, "age": 30},
                {"id": 2, "name": "Bea", "vip": False, "age": 25},
                {"id": 3, "name": "Tanaya", "vip": True, "age": 22},
            ]
        )
        orders.add_many(
            [
                {"order_id": 1, "user_id": 1, "total": 100},
                {"order_id": 2, "user_id": 1, "total": 50},
                {"order_id": 3, "user_id": 2, "total": 30},
                {"order_id": 4, "user_id": 3, "total": 25},
                {"order_id": 5, "user_id": 3, "total": 10},
            ]
        )

        result = (
            users.match_any(
                lambda q: q.where("vip").eq(True), lambda q: q.where("age").gt(23)
            )
            .lookup("logic_orders", "id", "user_id", "orders", many=True)
            .merge(
                lambda u: {"total_spent": sum(o["total"] for o in u.get("orders", []))}
            )
            .run(fields=["name", "vip", "total_spent"])
            .as_list()
        )

        names = [r["name"] for r in result]
        totals = {r["name"]: r["total_spent"] for r in result}
        self.assertIn("Neel", names)
        self.assertIn("Bea", names)
        self.assertIn("Tanaya", names)

        self.assertEqual(totals["Neel"], 150)
        self.assertEqual(totals["Bea"], 30)
        self.assertEqual(totals["Tanaya"], 35)

        for r in result:
            self.assertIn("vip", r)
            self.assertIn("total_spent", r)
        self.assertNotIn("age", r)  # `find()` excludes age

    def test_remove_field_top_level(self):
        """Test removing top-level fields from documents."""
        self.col.clear()
        self.col.add_many(
            [
                {"id": 1, "name": "Alice", "age": 30, "city": "Indy"},
                {"id": 2, "name": "Bob", "age": 25, "city": "NYC"},
                {"id": 3, "name": "Carl", "age": 35},
            ]
        )

        # Remove 'city' field from all documents
        result = self.col.remove_field("city")
        self.assertEqual(result["removed"], 2)  # Only 2 docs had 'city' field

        # Verify the field was removed
        docs = self.col.all_docs()
        self.assertEqual(len(docs), 3)
        for doc in docs:
            self.assertNotIn("city", doc)
            self.assertIn("name", doc)  # Other fields should remain
            self.assertIn("age", doc)

    def test_remove_field_nested(self):
        """Test removing nested fields using dot-notation."""
        self.col.clear()
        self.col.add_many(
            [
                {"id": 1, "name": "Alice", "profile": {"age": 30, "city": "Indy"}},
                {"id": 2, "name": "Bob", "profile": {"age": 25}},
                {"id": 3, "name": "Carl"},
            ]
        )

        # Remove only the nested 'city' field from profiles
        result = self.col.remove_field("profile.city")
        self.assertEqual(result["removed"], 1)  # Only 1 doc had 'profile.city'

        # Verify the nested field was removed
        docs = self.col.all_docs()
        self.assertEqual(len(docs), 3)

        # Check Alice's document
        alice = next(doc for doc in docs if doc["name"] == "Alice")
        self.assertIn("profile", alice)
        self.assertIn("age", alice["profile"])
        self.assertNotIn("city", alice["profile"])

        # Check Bob's document
        bob = next(doc for doc in docs if doc["name"] == "Bob")
        self.assertIn("profile", bob)
        self.assertIn("age", bob["profile"])

        # Check Carl's document (no profile)
        carl = next(doc for doc in docs if doc["name"] == "Carl")
        self.assertNotIn("profile", carl)

    def test_remove_field_deeply_nested(self):
        """Test removing deeply nested fields."""
        self.col.clear()
        self.col.add_many(
            [
                {
                    "id": 1,
                    "data": {"user": {"preferences": {"theme": "dark", "lang": "en"}}},
                },
                {"id": 2, "data": {"user": {"preferences": {"theme": "light"}}}},
                {"id": 3, "data": {"user": {"name": "John"}}},
            ]
        )

        # Remove deeply nested field
        result = self.col.remove_field("data.user.preferences.theme")
        self.assertEqual(result["removed"], 2)  # 2 docs had this field

        # Verify the field was removed
        docs = self.col.all_docs()
        doc1 = next(doc for doc in docs if doc["id"] == 1)
        doc2 = next(doc for doc in docs if doc["id"] == 2)
        doc3 = next(doc for doc in docs if doc["id"] == 3)

        self.assertNotIn("theme", doc1["data"]["user"]["preferences"])
        self.assertIn("lang", doc1["data"]["user"]["preferences"])
        self.assertNotIn("theme", doc2["data"]["user"]["preferences"])
        self.assertIn("name", doc3["data"]["user"])

    def test_remove_field_missing_field(self):
        """Test removing fields that don't exist (should not error)."""
        self.col.clear()
        self.col.add_many([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])

        # Try to remove non-existent fields
        result1 = self.col.remove_field("nonexistent")
        result2 = self.col.remove_field("deeply.nested.nonexistent")

        self.assertEqual(result1["removed"], 0)
        self.assertEqual(result2["removed"], 0)

        # Documents should remain unchanged
        docs = self.col.all_docs()
        self.assertEqual(len(docs), 2)
        for doc in docs:
            self.assertIn("name", doc)

    def test_remove_field_with_filter(self):
        """Test removing fields only from documents matching a filter."""
        self.col.clear()
        self.col.add_many(
            [
                {"id": 1, "name": "Alice", "age": 30, "city": "Indy"},
                {"id": 2, "name": "Bob", "age": 25, "city": "NYC"},
                {"id": 3, "name": "Carl", "age": 35, "city": "LA"},
            ]
        )

        # Remove 'city' only from documents where age > 28
        result = self.col.where("age").gt(28).remove_field("city")
        self.assertEqual(result["removed"], 2)  # Alice and Carl

        # Verify the results
        docs = self.col.all_docs()
        alice = next(doc for doc in docs if doc["name"] == "Alice")
        bob = next(doc for doc in docs if doc["name"] == "Bob")
        carl = next(doc for doc in docs if doc["name"] == "Carl")

        self.assertNotIn("city", alice)  # Removed (age 30)
        self.assertIn("city", bob)  # Not removed (age 25)
        self.assertNotIn("city", carl)  # Removed (age 35)

    def test_remove_field_count_accuracy(self):
        """Test that the returned count accurately reflects documents modified."""
        self.col.clear()
        self.col.add_many(
            [
                {"id": 1, "name": "Alice", "profile": {"age": 30, "city": "Indy"}},
                {"id": 2, "name": "Bob", "profile": {"age": 25}},
                {"id": 3, "name": "Carl"},
                {"id": 4, "name": "Dave", "profile": {"age": 40, "city": "NYC"}},
            ]
        )

        # Remove 'profile.city' - should affect 2 documents
        result = self.col.remove_field("profile.city")
        self.assertEqual(result["removed"], 2)

        # Remove 'profile.age' - should affect 3 documents
        result = self.col.remove_field("profile.age")
        self.assertEqual(result["removed"], 3)

        # Remove 'name' - should affect all 4 documents
        result = self.col.remove_field("name")
        self.assertEqual(result["removed"], 4)

        # Try to remove non-existent field - should affect 0 documents
        result = self.col.remove_field("nonexistent")
        self.assertEqual(result["removed"], 0)

    def test_distinct_basic_functionality(self):
        users = db("distinct_users")
        users.clear()
        users.add_many(
            [
                {"name": "Alice", "city": "Austin"},
                {"name": "Bob", "city": "Seattle"},
                {"name": "Carol", "city": "Austin"},
                {"name": "Dave", "city": "Indy"},
                {"name": "Eve", "city": "Seattle"},
            ]
        )

        distinct_cities = users.distinct("city")
        self.assertEqual(distinct_cities, ["Austin", "Indy", "Seattle"])
        self.assertEqual(len(distinct_cities), 3)

    def test_distinct_with_missing_fields(self):
        users = db("distinct_missing")
        users.clear()
        users.add_many(
            [
                {"name": "Alice", "city": "Austin"},
                {"name": "Bob"},  # No city field
                {"name": "Carol", "city": "Austin"},
                {"name": "Dave", "city": None},  # Explicit None
                {"name": "Eve", "city": "Seattle"},
            ]
        )

        distinct_cities = users.distinct("city")
        self.assertEqual(distinct_cities, ["Austin", "Seattle"])

    def test_distinct_with_nested_fields(self):
        users = db("distinct_nested")
        users.clear()
        users.add_many(
            [
                {"name": "Alice", "address": {"city": "Austin", "state": "TX"}},
                {"name": "Bob", "address": {"city": "Seattle", "state": "WA"}},
                {"name": "Carol", "address": {"city": "Austin", "state": "TX"}},
                {"name": "Dave", "address": {"city": "Indy", "state": "IN"}},
            ]
        )

        distinct_cities = users.distinct("address.city")
        self.assertEqual(distinct_cities, ["Austin", "Indy", "Seattle"])

    def test_distinct_with_mixed_data_types(self):
        data = db("distinct_mixed")
        data.clear()
        data.add_many(
            [
                {"value": "hello"},
                {"value": 42},
                {"value": "hello"},  # duplicate string
                {"value": 42.0},  # will be "42.0" as string
                {"value": True},  # will be "True" as string
                {"value": "world"},
            ]
        )

        distinct_values = data.distinct("value")
        expected = ["42", "42.0", "True", "hello", "world"]
        self.assertEqual(distinct_values, expected)

    def test_distinct_empty_result(self):
        users = db("distinct_empty")
        users.clear()
        users.add_many(
            [
                {"name": "Alice"},
                {"name": "Bob"},
            ]
        )

        distinct_cities = users.distinct("city")
        self.assertEqual(distinct_cities, [])

    def test_distinct_with_filters(self):
        users = db("distinct_filtered")
        users.clear()
        users.add_many(
            [
                {"name": "Alice", "city": "Austin", "age": 30},
                {"name": "Bob", "city": "Seattle", "age": 25},
                {"name": "Carol", "city": "Austin", "age": 35},
                {"name": "Dave", "city": "Indy", "age": 20},
            ]
        )

        # Get distinct cities for users over 24
        distinct_cities = users.where("age").gt(24).distinct("city")
        self.assertEqual(distinct_cities, ["Austin", "Seattle"])


print("NoSQL tests:")

unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestCollectionManager)
)
