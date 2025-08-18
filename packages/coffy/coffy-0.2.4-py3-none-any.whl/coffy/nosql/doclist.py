# coffy/nosql/doclist.py
# author: nsarathy

from .atomicity import _atomic_save


class DocList:
    """
    A class to represent a list of documents with additional utility methods.
    Provides methods to iterate, access by index, get length, and convert to JSON.
    """

    def __init__(self, docs: list[dict]):
        """
        Initialize the DocList with a list of documents.
        docs -- A list of documents (dictionaries) to store in the DocList.
        """
        self._docs = docs

    def __iter__(self):
        """
        Return an iterator over the documents in the DocList.
        """
        return iter(self._docs)

    def __getitem__(self, index):
        """
        Get a document by index.
        index -- The index of the document to retrieve.
        Returns the document at the specified index.
        """
        return self._docs[index]

    def __len__(self):
        """
        Get the number of documents in the DocList.
        Returns the count of documents.
        """
        return len(self._docs)

    def __repr__(self):
        """
        Return a string representation of the DocList.
        If the DocList is empty, it returns "<empty result>".
        Otherwise, it formats the documents as a table with headers.
        """
        if not self._docs:
            return "<empty result>"
        keys = list(self._docs[0].keys())
        header = " | ".join(keys)
        line = "-+-".join("-" * len(k) for k in keys)
        rows = []
        for doc in self._docs:
            row = " | ".join(str(doc.get(k, "")) for k in keys)
            rows.append(row)
        return f"{header}\n{line}\n" + "\n".join(rows)

    def to_json(self, path: str):
        """
        Save the documents in the DocList to a JSON file.
        path -- The file path to save the documents.
        """
        _atomic_save(self._docs, path)

    def as_list(self):
        """
        Convert the DocList to a regular list of documents.
        """
        return self._docs
