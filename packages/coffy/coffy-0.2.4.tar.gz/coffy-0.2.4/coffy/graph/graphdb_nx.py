# coffy/graph/graphdb_nx.py
# author: nsarathy

"""
A simple graph database using NetworkX.
"""

from .atomicity import _atomic_save
from .graph_result import GraphResult
from .graph_view import _view_graph
import json
import networkx as nx
import os


class GraphDB:
    """
    A class to represent a graph database.
    """

    def __init__(self, directed=False, path=None):
        """
        Initialize a GraphDB instance.
        directed -- Whether the graph is directed or not.
        path -- Path to the JSON file where the graph will be stored.
            If path is ":memory:" or None, the graph will be in-memory only.
            If path is provided, it must end with ".json".
        """
        self.g = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed
        self.in_memory = path == ":memory:"

        if path and not self.in_memory:
            if path.endswith(".json"):
                self.path = path
        else:
            self.in_memory = True
        if not self.in_memory and os.path.exists(self.path):
            self.load(self.path)
        elif not self.in_memory:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.save(self.path)

    # Node operations

    def add_node(self, node_id, labels=None, **attrs):
        """
        Add a node to the graph.
        node_id -- Unique identifier for the node.
        labels -- Optional list of labels for the node.
        attrs -- Additional attributes for the node.
        """
        if self.has_node(node_id):
            raise KeyError(
                f"Node '{node_id}' already exists. Use update_node to modify it."
            )
        if labels is not None:
            attrs["_labels"] = labels if isinstance(labels, list) else [labels]
        self.g.add_node(node_id, **attrs)
        self._persist()

    def add_nodes(self, nodes):
        """
        Add multiple nodes to the graph.
        nodes -- List of dictionaries, each representing a node.
        """
        for node in nodes:
            node_id = node["id"]
            labels = node.get("labels") or node.get("_labels")  # Accept either form
            attrs = {
                k: v for k, v in node.items() if k not in ["id", "labels", "_labels"]
            }
            self.add_node(node_id, labels=labels, **attrs)

    def get_node(self, node_id):
        """
        Get a node from the graph.
        node_id -- Unique identifier for the node.
        Returns the node's attributes as a dictionary.
        """
        return self.g.nodes[node_id]

    def _get_neighbors(self, node_id, direction):
        """
        Get the neighbors of a node in the graph.
        node_id -- Unique identifier for the node.
        direction -- Direction of the neighbors to retrieve ('in', 'out', or 'any').
        Returns a set of neighbor node IDs.
        """
        if self.directed:
            if direction == "out":
                return self.g.successors(node_id)
            elif direction == "in":
                return self.g.predecessors(node_id)
            elif direction == "any":
                return set(self.g.successors(node_id)).union(
                    self.g.predecessors(node_id)
                )
            else:
                raise ValueError("Direction must be 'in', 'out', or 'any'")
        else:
            return self.g.neighbors(node_id)

    def remove_node(self, node_id):
        """
        Remove a node from the graph.
        node_id -- Unique identifier for the node.
        """
        self.g.remove_node(node_id)
        self._persist()

    def remove_nodes_by_label(self, label):
        """
        Remove all nodes with a specific label.
        label -- The label of the nodes to remove.
        """
        nodes_to_remove = [
            n for n, a in self.g.nodes(data=True) if label in a.get("_labels", [])
        ]
        self.g.remove_nodes_from(nodes_to_remove)
        self._persist()

    # Relationship (edge) operations
    def add_relationship(self, source, target, rel_type=None, **attrs):
        """
        Add a relationship (edge) to the graph.
        source -- Unique identifier for the source node.
        target -- Unique identifier for the target node.
        rel_type -- Optional type of the relationship.
        attrs -- Additional attributes for the relationship.
        """
        if rel_type:
            attrs["_type"] = rel_type
        self.g.add_edge(source, target, **attrs)
        self._persist()

    def add_relationships(self, relationships):
        """
        Add multiple relationships to the graph.
        relationships -- List of dictionaries, each representing a relationship.
        """
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            rel_type = rel.get("type") or rel.get("_type")
            attrs = {
                k: v
                for k, v in rel.items()
                if k not in ["source", "target", "type", "_type"]
            }
            self.add_relationship(source, target, rel_type=rel_type, **attrs)

    def get_relationship(self, source, target):
        """
        Get a relationship (edge) from the graph.
        source -- Unique identifier for the source node.
        target -- Unique identifier for the target node.
        Returns the relationship's attributes as a dictionary.
        """
        return self.g.get_edge_data(source, target)

    def remove_relationship(self, source, target):
        """
        Remove a relationship (edge) from the graph.
        source -- Unique identifier for the source node.
        target -- Unique identifier for the target node.
        """
        self.g.remove_edge(source, target)
        self._persist()

    def remove_relationships_by_type(self, type):
        """
        Remove all relationships of a specific type.
        type -- Type of the relationship to remove.
        """
        edges_to_remove = [
            (u, v) for u, v, a in self.g.edges(data=True) if a.get("_type") == type
        ]
        self.g.remove_edges_from(edges_to_remove)
        self._persist()

    # Basic queries
    def neighbors(self, node_id):
        """
        Get the neighbors of a node.
        node_id -- Unique identifier for the node.
        Returns a list of neighbor node IDs.
        """
        return list(self.g.neighbors(node_id))

    def degree(self, node_id):
        """
        Get the degree of a node.
        node_id -- Unique identifier for the node.
        Returns the degree of the node (number of edges connected to it).
        """
        return self.g.degree[node_id]

    def has_node(self, node_id):
        """
        Check if a node exists in the graph.
        node_id -- Unique identifier for the node.
        Returns True if the node exists, False otherwise.
        """
        return self.g.has_node(node_id)

    def has_relationship(self, u, v):
        """
        Check if a relationship (edge) exists in the graph.
        u -- Unique identifier for the source node.
        v -- Unique identifier for the target node.
        Returns True if the relationship exists, False otherwise.
        """
        return self.g.has_edge(u, v)

    def update_node(self, node_id, **attrs):
        """
        Update attributes of a node.
        node_id -- Unique identifier for the node.
        attrs -- Attributes to update.
        """
        if not self.has_node(node_id):
            raise KeyError(f"Node '{node_id}' does not exist.")
        self.g.nodes[node_id].update(attrs)
        self._persist()

    def update_relationship(self, source, target, **attrs):
        """
        Update attributes of a relationship (edge).
        source -- Unique identifier for the source node.
        target -- Unique identifier for the target node.
        attrs -- Attributes to update.
        """
        if not self.has_relationship(source, target):
            raise KeyError(f"Relationship '{source}->{target}' does not exist.")
        self.g.edges[source, target].update(attrs)
        self._persist()

    def set_node(self, node_id, labels=None, **attrs):
        """
        Set or update a node in the graph.
        node_id -- Unique identifier for the node.
        labels -- Optional list of labels for the node.
        attrs -- Attributes to set or update.
        """
        if self.has_node(node_id):
            self.update_node(node_id, **attrs)
        else:
            self.add_node(node_id, labels=labels, **attrs)
        self._persist()

    # Advanced node search
    def project_node(self, node_id, fields=None):
        """
        Project a node's attributes.
        node_id -- Unique identifier for the node.
        fields -- Optional list of fields to include in the projection.
        Returns the node's attributes as a dictionary.
            If fields is None, all attributes are included.
        """
        if not self.has_node(node_id):
            return None
        node = self.get_node(node_id).copy()
        node["id"] = node_id
        if fields is None:
            return node
        return {k: node[k] for k in fields if k in node}

    def project_relationship(self, source, target, fields=None):
        """
        Project a relationship's attributes.
        source -- Unique identifier for the source node.
        target -- Unique identifier for the target node.
        fields -- Optional list of fields to include in the projection.
        Returns the relationship's attributes as a dictionary.
            If fields is None, all attributes are included.
        """
        if not self.has_relationship(source, target):
            return None
        rel = self.get_relationship(source, target).copy()
        rel.update({"source": source, "target": target, "type": rel.get("_type")})
        if fields is None:
            return rel
        return {k: rel[k] for k in fields if k in rel}

    def find_nodes(self, label=None, fields=None, limit=None, offset=0, **conditions):
        """
        Find nodes in the graph based on conditions.
        label -- Optional label to filter nodes by.
        fields -- Optional list of fields to include in the projection.
        limit -- Optional limit on the number of results.
        offset -- Optional offset for pagination.
        conditions -- Conditions to filter nodes by.
        Returns a list of nodes that match the conditions.
            Each node is projected using the specified fields.
        """
        return GraphResult(
            [
                self.project_node(n, fields)
                for n, a in self.g.nodes(data=True)
                if (label is None or label in a.get("_labels", []))
                and self._match_conditions(a, conditions)
            ][offset : offset + limit if limit is not None else None]
        )

    def find_by_label(self, label, fields=None, limit=None, offset=0):
        """
        Find nodes by label.
        label -- Label to filter nodes by.
        fields -- Optional list of fields to include in the projection.
        limit -- Optional limit on the number of results.
        offset -- Optional offset for pagination.
        Returns a list of nodes that have the specified label.
            Each node is projected using the specified fields.
        """
        return GraphResult(
            [
                self.project_node(n, fields)
                for n, a in self.g.nodes(data=True)
                if label in a.get("_labels", [])
            ][offset : offset + limit if limit is not None else None]
        )

    def find_relationships(
        self, rel_type=None, fields=None, limit=None, offset=0, **conditions
    ):
        """
        Find relationships in the graph based on conditions.
        rel_type -- Optional type of the relationship to filter by.
        fields -- Optional list of fields to include in the projection.
        limit -- Optional limit on the number of results.
        offset -- Optional offset for pagination.
        conditions -- Conditions to filter relationships by.
        Returns a list of relationships that match the conditions.
            Each relationship is projected using the specified fields.
        """
        return GraphResult(
            [
                self.project_relationship(u, v, fields)
                for u, v, a in self.g.edges(data=True)
                if (rel_type is None or a.get("_type") == rel_type)
                and self._match_conditions(a, conditions)
            ][offset : offset + limit if limit is not None else None]
        )

    def find_by_relationship_type(self, rel_type, fields=None, limit=None, offset=0):
        """
        Find relationships by type.
        rel_type -- Type of the relationship to filter by.
        fields -- Optional list of fields to include in the projection.
        limit -- Optional limit on the number of results.
        offset -- Optional offset for pagination.
        Returns a list of relationships that have the specified type.
            Each relationship is projected using the specified fields.
        """
        return GraphResult(
            [
                self.project_relationship(u, v, fields)
                for u, v, a in self.g.edges(data=True)
                if a.get("_type") == rel_type
            ][offset : offset + limit if limit is not None else None]
        )

    def _match_conditions(self, attrs, conditions):
        """
        Check if the attributes match the given conditions.
        attrs -- Attributes of the node or relationship.
        conditions -- Conditions to match against.
        Returns True if all conditions are met, False otherwise.
        """
        if not conditions:
            return True
        logic = conditions.get("_logic", "and")
        conditions = {k: v for k, v in conditions.items() if k != "_logic"}
        results = []

        for key, expected in conditions.items():
            actual = attrs.get(key)
            if isinstance(expected, dict):
                for op, val in expected.items():
                    if op == "gt":
                        results.append(actual > val)
                    elif op == "lt":
                        results.append(actual < val)
                    elif op == "gte":
                        results.append(actual >= val)
                    elif op == "lte":
                        results.append(actual <= val)
                    elif op == "ne":
                        results.append(actual != val)
                    elif op == "eq":
                        results.append(actual == val)
                    else:
                        results.append(False)
            else:
                results.append(actual == expected)

        if logic == "or":
            return any(results)
        elif logic == "not":
            return not all(results)
        return all(results)

    def match_node_path(
        self, start, pattern, return_nodes=True, node_fields=None, direction="out"
    ):
        """
        Match a path in the graph starting from a node.
        start -- Starting node conditions (e.g., {"name": "Alice"}).
        pattern -- Pattern to match, a list of dictionaries with "rel_type" and "node" keys.
        return_nodes -- Whether to return the nodes in the path.
        node_fields -- Optional list of fields to include in the projected nodes.
        direction -- Direction of the search ('in', 'out', or 'any').
        Returns a list of paths, where each path is a list of node IDs.
        """
        start_nodes = self.find_nodes(**start)
        node_paths = []

        for s in start_nodes:
            self._match_node_path(
                current_id=s["id"],
                pattern=pattern,
                node_path=[s["id"]],
                node_paths=node_paths,
                direction=direction,
            )

        unique_paths = list({tuple(p) for p in node_paths})

        if return_nodes:
            return [
                [self.project_node(n, node_fields) for n in path]
                for path in unique_paths
            ]
        return unique_paths

    def _match_node_path(self, current_id, pattern, node_path, node_paths, direction):
        """
        Recursive helper function to match a node path.
        current_id -- Current node ID.
        pattern -- Pattern to match.
        node_path -- Current path of node IDs.
        node_paths -- List to collect all matching node paths.
        direction -- Direction of the search ('in', 'out', or 'any').
        """
        if not pattern:
            node_paths.append(node_path)
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            node_attrs = self.get_node(neighbor)
            if not self._match_conditions(node_attrs, next_node_cond):
                continue
            if neighbor in node_path:  # avoid cycles
                continue
            self._match_node_path(
                neighbor, pattern[1:], node_path + [neighbor], node_paths, direction
            )

    def match_full_path(
        self, start, pattern, node_fields=None, rel_fields=None, direction="out"
    ):
        """
        Match a full path in the graph starting from a node.
        start -- Starting node conditions (e.g., {"name": "Alice"}).
        pattern -- Pattern to match, a list of dictionaries with "rel_type" and "node" keys.
        node_fields -- Optional list of fields to include in the projected nodes.
        rel_fields -- Optional list of fields to include in the projected relationships.
        direction -- Direction of the search ('in', 'out', or 'any').
        """
        start_nodes = self.find_nodes(**start)
        matched_paths = []

        for s in start_nodes:
            self._match_full_path(
                current_id=s["id"],
                pattern=pattern,
                relationship_path=[],
                node_path=[s["id"]],
                matched_paths=matched_paths,
                direction=direction,
            )

        return [
            {
                "nodes": [self.project_node(n, node_fields) for n in nodes],
                "relationships": [
                    self.project_relationship(u, v, rel_fields) for u, v in path
                ],
            }
            for path, nodes in matched_paths
        ]

    def _match_full_path(
        self,
        current_id,
        pattern,
        relationship_path,
        node_path,
        matched_paths,
        direction,
    ):
        """
        Recursive helper function to match a full path.
        current_id -- Current node ID.
        pattern -- Pattern to match.
        relationship_path -- Current path of relationships.
        node_path -- Current path of node IDs.
        matched_paths -- List to collect all matching paths.
        direction -- Direction of the search ('in', 'out', or 'any').
        """
        if not pattern:
            matched_paths.append((relationship_path, node_path))
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            if neighbor in node_path:
                continue
            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            if not self._match_conditions(self.get_node(neighbor), next_node_cond):
                continue

            self._match_full_path(
                neighbor,
                pattern[1:],
                relationship_path + [(current_id, neighbor)],
                node_path + [neighbor],
                matched_paths,
                direction,
            )

    def match_path_structured(
        self, start, pattern, node_fields=None, rel_fields=None, direction="out"
    ):
        """
        Match a structured path in the graph starting from a node.
        start -- Starting node conditions (e.g., {"name": "Alice"}).
        pattern -- Pattern to match, a list of dictionaries with "rel_type" and "node" keys.
        node_fields -- Optional list of fields to include in the projected nodes.
        rel_fields -- Optional list of fields to include in the projected relationships.
        direction -- Direction of the search ('in', 'out', or 'any').
        """
        start_nodes = self.find_nodes(**start)
        structured_paths = []

        for s in start_nodes:
            self._match_structured_path(
                current_id=s["id"],
                pattern=pattern,
                path=[{"node": self.project_node(s["id"], node_fields)}],
                structured_paths=structured_paths,
                direction=direction,
            )

        return structured_paths

    def _match_structured_path(
        self, current_id, pattern, path, structured_paths, direction
    ):
        """
        Recursive helper function to match a structured path.
        current_id -- Current node ID.
        pattern -- Pattern to match.
        path -- Current structured path.
        structured_paths -- List to collect all matching structured paths.
        direction -- Direction of the search ('in', 'out', or 'any').
        """
        if not pattern:
            structured_paths.append({"path": path})
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            if any(e.get("node", {}).get("id") == neighbor for e in path):
                continue  # Avoid cycles

            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            if not self._match_conditions(self.get_node(neighbor), next_node_cond):
                continue

            extended_path = path + [
                {"relationship": self.project_relationship(current_id, neighbor)},
                {"node": self.project_node(neighbor)},
            ]

            self._match_structured_path(
                neighbor, pattern[1:], extended_path, structured_paths, direction
            )

    # Aggregation methods

    def count_nodes(self):
        """
        Count the number of nodes in the graph.
        """
        return self.g.number_of_nodes()

    def count_nodes_by_label(self, label):
        """
        Count the number of nodes with a specific label.
        label -- The label to count.
        """
        return sum(
            1 for n, a in self.g.nodes(data=True) if label in a.get("_labels", [])
        )

    def count_relationships(self):
        """
        Count the number of relationships (edges) in the graph.
        """
        return self.g.number_of_edges()

    def count_relationships_by_type(self, type):
        """
        Count the number of relationships of a specific type.
        type -- Type of the relationship to count.
        """
        return sum(1 for _, _, a in self.g.edges(data=True) if a.get("_type") == type)

    def avg_degree(self):
        """
        Calculate the average degree of the nodes.
        """
        n = self.g.number_of_nodes()
        return sum(dict(self.g.degree()).values()) / n if n > 0 else 0

    def min_degree(self):
        """
        Find the minimum node degree in the graph.
        """
        degrees = list(dict(self.g.degree()).values())
        return min(degrees) if degrees else 0

    def max_degree(self):
        """
        Find the maximum node degree in the graph.
        """
        degrees = list(dict(self.g.degree()).values())
        return max(degrees) if degrees else 0

    def total_degree(self):
        """
        Return the sum of degrees of all nodes.
        Equivalent to 2x number of edges in undirected graphs.
        """
        return sum(dict(self.g.degree()).values())

    # Directed Graph Aggregations

    def total_in_degree(self):
        """
        Return the total in-degree of all nodes (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        return sum(dict(self.g.in_degree()).values())

    def total_out_degree(self):
        """
        Return the total out-degree of all nodes (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        return sum(dict(self.g.out_degree()).values())

    def avg_in_degree(self):
        """
        Average in-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        n = self.g.number_of_nodes()
        return sum(dict(self.g.in_degree()).values()) / n if n > 0 else 0

    def min_in_degree(self):
        """
        Minimum in-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        degrees = list(dict(self.g.in_degree()).values())
        return min(degrees) if degrees else 0

    def max_in_degree(self):
        """
        Maximum in-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        degrees = list(dict(self.g.in_degree()).values())
        return max(degrees) if degrees else 0

    def avg_out_degree(self):
        """
        Average out-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        n = self.g.number_of_nodes()
        return sum(dict(self.g.out_degree()).values()) / n if n > 0 else 0

    def min_out_degree(self):
        """
        Minimum out-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        degrees = list(dict(self.g.out_degree()).values())
        return min(degrees) if degrees else 0

    def max_out_degree(self):
        """
        Maximum out-degree (only for directed graphs).
        """
        if not self.g.is_directed():
            raise ValueError("Graph is not directed")
        degrees = list(dict(self.g.out_degree()).values())
        return max(degrees) if degrees else 0

    # Export
    def nodes(self):
        """
        Get all nodes in the graph.
        Returns a list of dictionaries with node IDs, labels, and attributes.
        """
        return [
            {
                "id": n,
                "labels": a.get("_labels", []),
                **{k: v for k, v in a.items() if k != "_labels"},
            }
            for n, a in self.g.nodes(data=True)
        ]

    def relationships(self):
        """
        Get all relationships in the graph.
        Returns a list of dictionaries with source, target, type, and attributes.
        """
        return [
            {
                "source": u,
                "target": v,
                "type": a.get("_type"),
                **{k: v for k, v in a.items() if k != "_type"},
            }
            for u, v, a in self.g.edges(data=True)
        ]

    def to_dict(self):
        """
        Convert the graph to a dictionary representation.
        Returns a dictionary with "nodes" and "relationships" keys.
            Each key contains a list of nodes or relationships, respectively.
        """
        return {"nodes": self.nodes(), "relationships": self.relationships()}

    def save(self, path=None):
        """
        Save the graph to a file.
        path -- Path to the file where the graph will be saved.
            If path is None, it will use the instance's path.
            If path is not specified, it will raise a ValueError.
        """
        path = path or self.path
        if not path:
            raise ValueError("No path specified to save the graph.")
        _atomic_save(self.to_dict(), path)

    def load(self, path=None):
        """
        Load the graph from a file.
        path -- Path to the file from which the graph will be loaded.
            If path is None, it will use the instance's path.
            If path is not specified, it will raise a ValueError.
        """
        path = path or self.path
        if not path:
            raise ValueError("No path specified to load the graph.")
        if os.path.getsize(path) == 0:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.g.clear()
        for node in data.get("nodes", []):
            self.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
        for rel in data.get("relationships", []):
            self.add_relationship(
                rel["source"],
                rel["target"],
                rel_type=rel.get("type") or rel.get("_type"),
                **{
                    k: v
                    for k, v in rel.items()
                    if k not in ["source", "target", "type", "_type"]
                },
            )

    def save_query_result(self, result, path=None):
        """
        Save the result of a query to a file.
        result -- Result of the query, typically a list of nodes or relationships.
        path -- Path to the file where the result will be saved.
            If path is None, it will raise a ValueError.
        """
        result = result.as_list() if hasattr(result, "as_list") else result
        if path is None:
            raise ValueError("No path specified to save the query result.")
        _atomic_save(result, path)

    def _persist(self):
        """
        Persist changes to the graph to the file if not in memory.
        """
        if not self.in_memory:
            self.save(self.path)

    def clear(self):
        """
        Clear the graph, removing all nodes and relationships.
        """
        self.g.clear()
        self._persist()

    def view(self):
        """
        Visualize the graph in a GUI window.
        """
        _view_graph(self.to_dict(), directed=self.directed)
