# coffy/nosql/index_engine.py
# author: nsarathy

from collections import defaultdict


class IndexManager:
    """
    Automatically maintains in-memory indexes for fast lookup.
    """

    def __init__(self):
        """
        Initialize the IndexManager with empty indexes and document map.
        """
        self.indexes = defaultdict(lambda: defaultdict(set))
        self.doc_map = {}  # doc_id -> doc

    def index(self, doc):
        """
        Index a document by adding it to the document map and updating the indexes.
        doc -- The document to index, should be a dictionary.
        """
        doc_id = id(doc)  # Use object ID as fallback if no 'id' field
        self.doc_map[doc_id] = doc

        for field, value in doc.items():
            if isinstance(value, (str, int, float, bool)):
                self.indexes[field][value].add(doc_id)

    def remove(self, doc):
        """
        Remove a document from the index.
        doc -- The document to remove, should be a dictionary.
        """
        doc_id = id(doc)
        for field, value in doc.items():
            if field in self.indexes and value in self.indexes[field]:
                self.indexes[field][value].discard(doc_id)
                if not self.indexes[field][value]:
                    del self.indexes[field][value]
        self.doc_map.pop(doc_id, None)

    def reindex(self, old_doc, new_doc):
        """
        Reindex a document by removing the old document and adding the new one.
        old_doc -- The document to remove from the index.
        new_doc -- The document to add to the index.
        """
        self.remove(old_doc)
        self.index(new_doc)

    def query(self, field, value):
        """
        Query the index for documents matching a specific field and value.
        field -- The field to query.
        value -- The value to match in the field.
        Returns a list of documents that match the query.
        """
        ids = self.indexes.get(field, {}).get(value, set())
        return [self.doc_map[i] for i in ids]

    def query_in(self, field, values):
        """
        Query the index for documents matching a specific field and a list of values.
        field -- The field to query.
        values -- The list of values to match in the field.
        Returns a list of documents that match the query.
        """
        out = set()
        for val in values:
            out.update(self.indexes.get(field, {}).get(val, set()))
        return [self.doc_map[i] for i in out]

    def clear(self):
        """
        Clear all indexes and the document map.
        """
        self.indexes.clear()
        self.doc_map.clear()
