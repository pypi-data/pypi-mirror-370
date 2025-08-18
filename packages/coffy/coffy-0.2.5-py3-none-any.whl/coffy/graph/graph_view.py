import networkx as nx
import random
import tempfile
import webbrowser


def _view_graph(data, directed=False):
    try:
        from pyvis.network import Network
    except ImportError:
        raise ImportError(
            "\nPlease install pyvis to view graphs. Use:\npip install pyvis"
        )

    G = nx.DiGraph() if directed else nx.Graph()

    def get_random_color(multiple):
        if multiple % 3 == 0:
            return "#{:06x}".format(random.randint(0, 0xAAFF77))
        elif multiple % 3 == 1:
            return "#{:06x}".format(random.randint(0, 0x77AAFF))
        else:
            return "#{:06x}".format(random.randint(0, 0xFF77AA))

    label_colors = {}
    rel_type_colors = {}

    for node in data["nodes"]:
        i = 0
        for label in node.get("labels", ["Unknown"]):
            if label not in label_colors:
                temp_color = get_random_color(i)
                while (
                    temp_color in label_colors.values()
                    or temp_color in rel_type_colors.values()
                ):
                    temp_color = get_random_color(i)
                label_colors[label] = temp_color
            i += 1

    for rel in data["relationships"]:
        i = 0
        r_type = rel.get("type", "UNKNOWN")
        if r_type not in rel_type_colors:
            temp_color = get_random_color(i)
            while (
                temp_color in rel_type_colors.values()
                or temp_color in label_colors.values()
            ):
                temp_color = get_random_color(i)
            rel_type_colors[r_type] = temp_color
        i += 1

    for node in data["nodes"]:
        node_id = node["id"]
        label = node.get("labels", ["Unknown"])[0]  # fallback if no labels
        name = node.get("name", node_id)  # fallback if no name
        extra_info = {
            k: v for k, v in node.items() if k not in {"id", "labels", "name"}
        }
        # Build title dynamically from all extra attributes
        title = f"{name}" + (
            "\n" + "\n".join(f"{k}: {v}" for k, v in extra_info.items())
            if extra_info
            else ""
        )
        G.add_node(
            node_id, title=title, label=label, color=label_colors.get(label, "#DDDDDD")
        )

    for rel in data["relationships"]:
        src = rel["source"]
        tgt = rel["target"]
        rel_type = rel.get("type", "UNKNOWN")
        extra_info = {
            k: v for k, v in rel.items() if k not in {"source", "target", "type"}
        }
        # Relationship tooltip with all extra attributes
        rel_title = rel_type + (
            "\n" + "\n".join(f"{k}: {v}" for k, v in extra_info.items())
            if extra_info
            else ""
        )
        G.add_edge(
            src, tgt, title=rel_title, color=rel_type_colors.get(rel_type, "#DDDDDD")
        )

    # Visualize
    net = Network(height="1080px", width="100%", bgcolor="#222", font_color="white")
    net.from_nx(G)
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        net.write_html(tmp.name, notebook=False)
        webbrowser.open("file://" + tmp.name)
