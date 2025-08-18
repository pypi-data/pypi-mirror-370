# coffy/nosql/engine.py
# author: nsarathy

"""
A simple NoSQL database engine.
This engine supports basic CRUD operations, querying with filters, and aggregation functions.
"""

from .atomicity import _atomic_save
from .index_engine import IndexManager
from .nosql_view import _view_nosql_collection
from .query_builder import QueryBuilder
import json
import os


_collection_registry = {}


class CollectionManager:
    """
    Manage a NoSQL collection, providing methods for querying and manipulating documents.
    """

    def __init__(self, name: str, path: str = None):
        """
        Initialize a collection manager for a NoSQL collection.
        name -- The name of the collection.
        path -- Optional path to a JSON file where the collection data is stored.
        """
        self.name = name
        self.in_memory = False

        if path:
            if path == ":memory:":
                self.in_memory = True
                self.path = None
            elif not path.endswith(".json"):
                raise ValueError("Path must be to a .json file")
            self.path = path
        else:
            self.in_memory = True

        self.documents = []
        self.index_manager = IndexManager()
        self._load()

        for doc in self.documents:
            self.index_manager.index(doc)

        _collection_registry[name] = self

    def _load(self):
        """
        Load the collection data from the JSON file.
        If the file does not exist, create an empty collection.
        If in_memory is True, initialize an empty collection.
        """
        if self.in_memory:
            self.documents = []
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                self.index_manager.clear()
                for doc in self.documents:
                    self.index_manager.index(doc)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                self.documents = []

    def _save(self):
        """
        Save the collection data to the JSON file.
        If in_memory is True, this method does nothing.
        """
        if not self.in_memory:
            _atomic_save(self.documents, self.path)

    def add(self, document: dict):
        """
        Add a document to the collection.
        document -- The document to add, must be a dictionary.
        Returns a dictionary with the count of inserted documents.
        """
        self.documents.append(document)
        self.index_manager.index(document)
        self._save()
        return {"inserted": 1}

    def add_many(self, docs: list[dict]):
        """
        Add multiple documents to the collection.
        docs -- A list of documents to add, each must be a dictionary.
        Returns a dictionary with the count of inserted documents.
        """
        self.documents.extend(docs)
        for doc in docs:
            self.index_manager.index(doc)
        self._save()
        return {"inserted": len(docs)}

    def where(self, field):
        """
        Start a query to filter documents based on a field.
        field -- The field to filter on.
        Returns a QueryBuilder instance to build the query.
        """
        return QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        ).where(field)

    def match_any(self, *conditions):
        """
        Start a query to match any of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the combined conditions.
        """
        q = QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        )
        return q._or(*conditions)

    def match_all(self, *conditions):
        """
        Start a query to match all of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the combined conditions.
        """
        q = QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        )
        return q._and(*conditions)

    def not_any(self, *conditions):
        """
        Start a query to negate any of the specified conditions.
        conditions -- Functions that take a QueryBuilder instance and modify its filters.
        Returns a QueryBuilder instance with the negated conditions.
        """
        q = QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        )
        return q._not(lambda nq: nq._or(*conditions))

    def lookup(self, *args, **kwargs):
        """
        Perform a lookup to enrich documents with related data from another collection.
        args -- Positional arguments for the lookup.
        kwargs -- Keyword arguments for the lookup.
        Returns a QueryBuilder instance with the lookup applied.
        """
        return QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        ).lookup(*args, **kwargs)

    def merge(self, *args, **kwargs):
        """
        Merge documents from another collection into this collection.
        args -- Positional arguments for the merge.
        kwargs -- Keyword arguments for the merge.
        Returns a QueryBuilder instance with the merge applied.
        """
        return QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        ).merge(*args, **kwargs)

    def sum(self, field):
        """
        Calculate the sum of a numeric field across all documents.
        field -- The field to sum.
        Returns the sum of the field values.
        """
        return QueryBuilder(self.documents).sum(field)

    def avg(self, field):
        """
        Calculate the average of a numeric field across all documents.
        field -- The field to average.
        Returns the average of the field values.
        """
        return QueryBuilder(self.documents).avg(field)

    def min(self, field):
        """
        Calculate the minimum of a numeric field across all documents.
        field -- The field to find the minimum.
        Returns the minimum of the field values.
        """
        return QueryBuilder(self.documents).min(field)

    def max(self, field):
        """
        Calculate the maximum of a numeric field across all documents.
        field -- The field to find the maximum.
        Returns the maximum of the field values.
        """
        return QueryBuilder(self.documents).max(field)

    def count(self):
        """
        Count the number of documents in the collection.
        Returns the count of documents.
        """
        return QueryBuilder(self.documents).count()

    def distinct(self, field):
        """
        Get a sorted list of unique values for a specified field across all documents.
        field -- The field to get distinct values for, can be a dotted path like "a.b.c".
        Returns a sorted list of unique values.
        """
        return QueryBuilder(self.documents).distinct(field)

    def first(self):
        """
        Get the first document in the collection.
        Returns the first document or None if the collection is empty.
        """
        return QueryBuilder(self.documents).first()

    def clear(self):
        """
        Clear all documents from the collection.
        Returns a dictionary with the count of cleared documents.
        """
        count = len(self.documents)
        self.documents = []
        self.index_manager.clear()
        self._save()
        return {"cleared": count}

    def export(self, path):
        """
        Export the collection to a JSON file.
        path -- The file path to export the collection.
        """
        if not path.endswith(".json"):
            raise ValueError("Invalid file format. Please use a .json file.")
        _atomic_save(self.documents, path)

    def import_(self, path):
        """
        Import documents from a JSON file into the collection.
        path -- The file path to import the collection from.
        If the file does not exist, it raises a FileNotFoundError.
        """
        with open(path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        self.index_manager.clear()
        for doc in self.documents:
            self.index_manager.index(doc)
        self._save()

    def all(self):
        """
        Get all documents in the collection.
        Returns a list of all documents.
        """
        return self.documents

    def save(self, path: str):
        """
        Save the current state of the collection to a JSON file.
        path -- The file path to save the collection.
        If the path does not end with .json, it raises a ValueError.
        """
        if not path.endswith(".json"):
            raise ValueError("Invalid file format. Please use a .json file.")
        _atomic_save(self.documents, path)

    def all_docs(self):
        """
        Get all documents in the collection.
        Returns a list of all documents.
        """
        return self.documents

    def remove_field(self, field):
        """
        Remove the specified field from all documents in the collection.
        field -- The field to remove, can be a dotted path like "a.b.c".
        Returns a dictionary with the count of documents actually modified.
        """
        return QueryBuilder(
            self.documents,
            all_collections=_collection_registry,
            collection_name=self.name,
        ).remove_field(field)

    def view(self):
        """
        View the collection in a user-friendly HTML format.
        Opens the collection viewer in the default web browser.
        """
        _view_nosql_collection(self.documents, self.name)
