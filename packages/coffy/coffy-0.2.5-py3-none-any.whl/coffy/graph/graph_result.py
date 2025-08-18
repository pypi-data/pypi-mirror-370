# coffy/graph/graph_result.py
# author: nsarathy


class GraphResult:
    """
    A class to represent the result of a graph query.
    """

    def __init__(self, docs):
        """
        Initializes the GraphResult with a list of node/relationships.
        docs -- List of dictionaries representing the node/relationships returned by the graph query.
        """
        self._docs = docs

    def __iter__(self):
        """
        Returns an iterator over the node/relationships in the result.
        """
        return iter(self._docs)

    def __getitem__(self, index):
        """
        Returns the node/relationship at the specified index.
        index -- The index of the node/relationship to retrieve.
        """
        return self._docs[index]

    def __len__(self):
        """
        Returns the number of node/relationships in the result.
        """
        return len(self._docs)

    def as_list(self):
        """
        Returns the node/relationships as a list.
        """
        return self._docs

    def sum(self, field):
        """
        Returns the sum of the specified field across all node/relationships.
        field -- The field to sum across the node/relationships.
        """
        return sum(
            d.get(field, 0)
            for d in self._docs
            if isinstance(d.get(field), (int, float))
        )

    def avg(self, field):
        """
        Returns the average of the specified field across all node/relationships.
        field -- The field to average across the node/relationships.
        """
        values = [
            d.get(field) for d in self._docs if isinstance(d.get(field), (int, float))
        ]
        return sum(values) / len(values) if values else 0

    def min(self, field):
        """
        Returns the minimum of the specified field across all node/relationships.
        field -- The field to find the minimum of across the node/relationships.
        """
        values = [
            d.get(field) for d in self._docs if isinstance(d.get(field), (int, float))
        ]
        return min(values) if values else None

    def max(self, field):
        """
        Returns the maximum of the specified field across all node/relationships.
        field -- The field to find the maximum of across the node/relationships.
        """
        values = [
            d.get(field) for d in self._docs if isinstance(d.get(field), (int, float))
        ]
        return max(values) if values else None

    def count(self):
        """
        Returns the number of node/relationships in the result.
        """
        return len(self._docs)

    def first(self):
        """
        Returns the first node/relationship in the result.
        """
        return self._docs[0] if self._docs else None
