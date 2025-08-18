# coffy/nosql/query_builder.py
# author: nsarathy

import re
from coffy.nosql.doclist import DocList


class QueryBuilder:
    """
    A class to build and execute queries on a collection of documents.
    Supports filtering, aggregation, and lookups.
    """

    def __init__(self, documents, all_collections=None, collection_name=None):
        """
        Initialize the QueryBuilder with a collection of documents.
        documents -- List of documents (dictionaries) to query.
        all_collections -- Optional dictionary of all collections for lookups.
        """
        self.documents = documents
        self.filters = []
        self.current_field = None
        self.all_collections = all_collections or {}
        self._lookup_done = False
        self._lookup_results = None
        self._limit = None
        self._offset = None
        self._sort_key = None
        self._sort_reverse = False

        self.collection_name = collection_name
        self.index_manager = None
        if all_collections and collection_name:
            cm = all_collections.get(collection_name)
            if cm:
                self.index_manager = cm.index_manager
                self.collection = cm

    @staticmethod
    def _get_nested(doc, dotted_key):
        """
        Get a nested value from a document using a dotted key.
        dotted_key -- A string representing the path to the value, e.g., "a.b.c".
        Returns the value if found, otherwise None.
        """
        keys = dotted_key.split(".")
        for k in keys:
            if not isinstance(doc, dict) or k not in doc:
                return None
            doc = doc[k]
        return doc

    @staticmethod
    def _remove_nested(doc, dotted_key):
        """
        Remove a nested field from a document using a dotted key.
        dotted_key -- A string representing the path to the field, e.g., "a.b.c".
        Returns True if the field was removed, False if it didn't exist.
        """
        keys = dotted_key.split(".")
        current = doc

        # Navigate to the parent of the target field
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                return False
            current = current[k]

        # Remove the target field
        target_key = keys[-1]
        if isinstance(current, dict) and target_key in current:
            del current[target_key]
            return True
        return False

    def where(self, field):
        """
        Set the current field for filtering.
        field -- The field to filter on, can be a dotted path like "a.b.c".
        Returns self to allow method chaining.
        """
        self.current_field = field
        return self

    # Comparison
    def eq(self, value):
        """
        Filter documents where the current field equals the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        if self.index_manager:
            docs = self.index_manager.query(self.current_field, value)
            if docs:
                self.documents = docs
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) == value
        )

    def ne(self, value):
        """
        Filter documents where the current field does not equal the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) != value
        )

    def gt(self, value):
        """
        Filter documents where the current field is greater than the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) > value
        )

    def gte(self, value):
        """
        Filter documents where the current field is greater than or equal to the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) >= value
        )

    def lt(self, value):
        """
        Filter documents where the current field is less than the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) < value
        )

    def lte(self, value):
        """
        Filter documents where the current field is less than or equal to the given value.
        value -- The value to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: isinstance(
                QueryBuilder._get_nested(d, self.current_field), (int, float)
            )
            and QueryBuilder._get_nested(d, self.current_field) <= value
        )

    def between(self, a, b):
        """
        Filter documents where the current field is between the given values (inclusive).
        a -- Value to range from.
        b -- Value to range to.
        Returns self to allow method chaining.
        """
        low, high = sorted((a, b))
        return self.gte(low).lte(high)

    def in_(self, values):
        """
        Filter documents where the current field is in the given list of values.
        values -- The list of values to compare against.
        Returns self to allow method chaining.
        """
        if self.index_manager:
            docs = self.index_manager.query_in(self.current_field, values)
            if docs:
                self.documents = docs
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) in values
        )

    def nin(self, values):
        """
        Filter documents where the current field is not in the given list of values.
        values -- The list of values to compare against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) not in values
        )

    def matches(self, regex):
        """
        Filter documents where the current field matches the given regular expression.
        regex -- The regular expression to match against.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: re.search(
                regex, str(QueryBuilder._get_nested(d, self.current_field))
            )
        )

    def exists(self):
        """
        Filter documents where the current field exists.
        Returns self to allow method chaining.
        """
        return self._add_filter(
            lambda d: QueryBuilder._get_nested(d, self.current_field) is not None
        )

    def sort(self, key: str, reverse: bool = False):
        """
        Specifies the sorting order for the query results.
        Args:
            key (str): The document key to sort by. Can be a nested field.
            reverse (bool): If True, sorts in descending order. Defaults to False.
        Returns:
            QueryBuilder: The QueryBuilder instance for chaining.
        """
        self._sort_key = key
        self._sort_reverse = reverse
        return self

    # Logic grouping
    def _and(self, *fns):
        """
        Combine multiple filter functions with logical AND.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: all(f(d) for f in fs))
        return self

    def _not(self, *fns):
        """
        Combine multiple filter functions with logical NOT.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: not all(f(d) for f in fs))
        return self

    def _or(self, *fns):
        """
        Combine multiple filter functions with logical OR.
        fns -- Functions that take a QueryBuilder instance and modify its filters.
        Returns self to allow method chaining.
        """
        chains = []
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            chains.append(sub.filters)
        self.filters.append(lambda d: any(all(f(d) for f in chain) for chain in chains))
        return self

    # Add filter
    def _add_filter(self, fn):
        """
        Add a filter function to the query.
        fn -- A function that takes a document and returns True if it matches the filter.
        Returns self to allow method chaining.
        """
        negate = getattr(self, "_negate", False)
        self._negate = False
        self.filters.append(lambda d: not fn(d) if negate else fn(d))
        return self

    # Core execution
    def run(self, fields=None):
        """
        Execute the query and return the results.
        fields -- Optional list of fields to project in the results.
            If provided, only these fields will be included in the returned documents.
            Otherwise, the full documents will be returned.
        Returns a DocList containing the matching documents.
        """
        results = [doc for doc in self.documents if all(f(doc) for f in self.filters)]

        if self._sort_key:

            def sort_key_func(doc):
                val = self._get_nested(doc, self._sort_key)
                if val is None:
                    return (3, None)
                elif isinstance(val, (int, float)):
                    return (0, val)
                elif isinstance(val, str):
                    return (1, val)
                else:
                    return (2, str(val))

            results.sort(key=sort_key_func, reverse=self._sort_reverse)

        if self._offset:
            results = results[self._offset :]
        if self._limit is not None:
            results = results[: self._limit]
        if self._lookup_done:
            results = self._lookup_results.copy()
            self._lookup_done = False
            self._lookup_results = None

        if fields is not None:
            projected = []
            for doc in results:
                proj = {}
                for f in fields:
                    value = QueryBuilder._get_nested(doc, f)
                    proj[f] = value
                projected.append(proj)
            return DocList(projected)

        return DocList(results)

    def update(self, changes):
        """
        Update documents that match the current filters with the given changes.
        changes -- A dictionary of fields to update in the matching documents.
        Returns a dictionary with the count of updated documents.
        """
        if not self.collection:
            raise RuntimeError("Cannot propagate update without CollectionManager.")

        count = 0
        for doc in self.collection.documents:
            if all(f(doc) for f in self.filters):
                self.index_manager.remove(doc)
                doc.update(changes)
                self.index_manager.index(doc)
                count += 1

        self.collection._save()
        return {"updated": count}

    def delete(self):
        """
        Delete documents that match the current filters.
        Returns a dictionary with the count of deleted documents.
        """
        if not self.collection:
            raise RuntimeError("Cannot propagate delete without CollectionManager.")

        before = len(self.collection.documents)
        to_delete = [
            doc
            for doc in self.collection.documents
            if all(f(doc) for f in self.filters)
        ]

        for doc in to_delete:
            self.index_manager.remove(doc)

        self.collection.documents[:] = [
            doc for doc in self.collection.documents if doc not in to_delete
        ]
        self.collection._save()

        return {"deleted": before - len(self.collection.documents)}

    def replace(self, new_doc):
        """
        Replace documents that match the current filters with a new document.
        new_doc -- The new document to replace matching documents with.
        Returns a dictionary with the count of replaced documents.
        """
        if not self.collection:
            raise RuntimeError("Cannot propagate replace without CollectionManager.")

        replaced = 0
        for i, doc in enumerate(self.collection.documents):
            if all(f(doc) for f in self.filters):
                self.index_manager.reindex(doc, new_doc)
                self.collection.documents[i] = new_doc
                replaced += 1

        self.collection._save()
        return {"replaced": replaced}

    def remove_field(self, field):
        """
        Remove the specified field from documents that match the current filters.
        field -- The field to remove, can be a dotted path like "a.b.c".
        Returns a dictionary with the count of documents actually modified.
        """
        if not self.collection:
            raise RuntimeError(
                "Cannot propagate remove_field without CollectionManager."
            )

        removed_count = 0
        for doc in self.collection.documents:
            if all(f(doc) for f in self.filters):
                # Remove old index before modifying the document
                self.index_manager.remove(doc)

                # Remove the field and check if it was actually removed
                if QueryBuilder._remove_nested(doc, field):
                    removed_count += 1

                # Re-index the modified document
                self.index_manager.index(doc)

        self.collection._save()
        return {"removed": removed_count}

    def count(self):
        """
        Count the number of documents that match the current filters.
        Returns the count of matching documents.
        """
        return len(self.run())

    def first(self):
        """
        Get the first document that matches the current filters.
        Returns the first matching document, or None if no documents match.
        """
        return next(iter(self.run()), None)

    # Aggregates
    def sum(self, field):
        """
        Calculate the sum of a numeric field across all matching documents.
        field -- The field to sum.
        Returns the total sum of the field values.
            If no documents match or the field is not numeric, returns 0.
        """
        return sum(
            doc.get(field, 0)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        )

    def avg(self, field):
        """
        Calculate the average of a numeric field across all matching documents.
        field -- The field to average.
        Returns the average of the field values.
            If no documents match or the field is not numeric, returns 0.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return sum(values) / len(values) if values else 0

    def min(self, field):
        """
        Find the minimum value of a numeric field across all matching documents.
        field -- The field to find the minimum of.
        Returns the minimum value of the field.
            If no documents match or the field is not numeric, returns None.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return min(values) if values else None

    def max(self, field):
        """
        Find the maximum value of a numeric field across all matching documents.
        field -- The field to find the maximum of.
        Returns the maximum value of the field.
            If no documents match or the field is not numeric, returns None.
        """
        values = [
            doc.get(field)
            for doc in self.run()
            if isinstance(doc.get(field), (int, float))
        ]
        return max(values) if values else None

    def distinct(self, field):
        """
        Get a sorted list of unique values for a specified field across all matching documents.
        field -- The field to get distinct values for, can be a dotted path like "a.b.c".
        Returns a sorted list of unique values as strings.
            Missing fields are ignored. Mixed data types are coerced to strings.
        """
        values = set()
        for doc in self.run():
            value = QueryBuilder._get_nested(doc, field)
            if value is not None:
                values.add(str(value))
        return sorted(list(values))

    # Lookup
    def lookup(
        self, foreign_collection_name, local_key, foreign_key, as_field, many=True
    ):
        """
        Perform a lookup to join related documents from another collection.
        foreign_collection_name -- Name of the collection to join from.
        local_key -- Field in the local documents to match on.
        foreign_key -- Field in the foreign documents to match on.
        as_field -- Name of the field to store the joined data.
        many -- If True, stores a list of matches. If False, stores only the first match.
        """
        if self._lookup_done:
            raise RuntimeError("Cannot perform another lookup after a previous one")

        foreign_col = self.all_collections.get(foreign_collection_name)
        if not foreign_col:
            raise ValueError(
                f"Collection '{foreign_collection_name}' not found in registry"
            )
        foreign_docs = foreign_col.documents

        fk_map = {}
        for doc in foreign_docs:
            key = doc.get(foreign_key)
            if key is not None:
                fk_map.setdefault(key, []).append(doc)

        enriched = []
        for doc in self.run():
            joined = fk_map.get(doc.get(local_key), [])
            doc = dict(doc)  # shallow copy
            if many:
                doc[as_field] = joined
            else:
                doc[as_field] = joined[0] if joined else None
            enriched.append(doc)

        self._lookup_done = True
        self._lookup_results = enriched
        return self

    # Merge
    def merge(self, fn):
        """
        Merge documents with additional computed fields.

        fn -- A function that takes a document and returns a dict to merge in.
        """
        docs = self._lookup_results if self._lookup_done else self.run()
        merged = []
        for doc in docs:
            new_doc = dict(doc)
            new_doc.update(fn(doc))
            merged.append(new_doc)
        self._lookup_done = True
        self._lookup_results = merged
        return self

    # Pagination
    def limit(self, n):
        """
        Limit the number of results returned by the query.
        n -- Maximum number of documents to return.
        Returns self to allow method chaining.
        """
        self._limit = n
        return self

    def offset(self, n):
        """
        Skip the first n results returned by the query.
        n -- Number of documents to skip.
        Returns self to allow method chaining.
        """
        self._offset = n
        return self
