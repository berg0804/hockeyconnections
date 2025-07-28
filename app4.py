import streamlit as st
import pandas as pd
import networkx as nx
import json

# --------------------
# 📥 Load CSV Data
# --------------------
@st.cache_data
def load_graph_data():
    nodes = pd.read_csv("nodes.csv")
    edges = pd.read_csv("edges.csv")
    nodes["Label"] = nodes["Label"].str.strip()
    return nodes, edges

nodes_df, edges_df = load_graph_data()

# Build main graph
G = nx.Graph()
for _, row in nodes_df.iterrows():
    G.add_node(row["ID"], label=row["Label"])
for _, row in edges_df.iterrows():
    G.add_edge(row["Source"], row["Target"])

# --------------------
# 🔎 Search Function
# --------------------
def get_connections_as_dataframe(graph, search_name, max_degree=3, exclude_words=None):
    search_name_clean = search_name.strip().lower()

    # Find node id
    node_id = None
    for n, data in graph.nodes(data=True):
        if data.get("label", "").lower() == search_name_clean:
            node_id = n
            break

    if node_id is None:
        return pd.DataFrame()  # No results

    # Search deeper
    deeper_cutoff = max_degree * 3
    all_paths = nx.single_source_shortest_path(graph, node_id, cutoff=deeper_cutoff)

    seen_pairs = set()
    rows = []

    for target_node, path in all_paths.items():
        if target_node == node_id:
            continue  # skip self

        target_label = graph.nodes[target_node].get("label", str(target_node))

        if exclude_words and any(word.lower() in target_label.lower() for word in exclude_words):
            continue

        adjusted_path = []
        for node in path:
            label = graph.nodes[node].get("label", str(node))
            if node == node_id or not any(word.lower() in label.lower() for word in (exclude_words or [])):
                adjusted_path.append(node)

        adjusted_degree = len(adjusted_path) - 1
        if adjusted_degree > max_degree or adjusted_degree < 1:
            continue

        for parent, child in zip(adjusted_path[:-1], adjusted_path[1:]):
            pair = (graph.nodes[parent].get("label", str(parent)),
                    graph.nodes[child].get("label", str(child)))
            if pair not in seen_pairs:
                rows.append({
                    "Parent": pair[0],
                    "Child": pair[1],
                    "Degree": adjusted_degree
                })
                seen_pairs.add(pair)

    return pd.DataFrame(rows)

# --------------------
# 🚀 Streamlit UI
# --------------------
st.title("🌳 Interactive Family Tree (Zoomable + Collapsible)")

search_name = st.text_input("🔎 Search for a person:", "Wayne Gretzky")
exclude_words = st.text_input("❌ Exclude nodes containing (comma-separated):", "Trade, Overall")
max_degree = st.slider("📏 Max degree of separation:", 1, 5, 3)

if st.button("Generate Tree"):
    exclude_list = [word.strip() for word in exclude_words.split(",") if word.strip()]
    df_connections = get_connections_as_dataframe(G, search_name, max_degree, exclude_list)

    if df_connections.empty:
        st.warning(f"⚠️ No connections found for '{search_name}'.")
    else:
        st.success(f"✅ Found {len(df_connections)} connections for '{search_name}'.")

        # Preview connection table
        st.dataframe(df_connections)

        # --------------------
        # 🌳 Build nested JSON for D3
        # --------------------
        def build_tree(df, root):
            tree = {"name": root, "children": []}
            child_df = df[df["Parent"] == root]
            for _, row in child_df.iterrows():
                subtree = build_tree(df, row["Child"])
                tree["children"].append(subtree)
            return tree

        tree_data = build_tree(df_connections, search_name)

        # --------------------
        # 📡 Embed D3 tree with fixed node sizes
        # --------------------
        d3_html = """
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                html, body {
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    overflow: hidden;
                    background-color: white;
                }
                #tree-container {
                    width: 100%;
                    height: 100%;
                    overflow: scroll;
                }
                .node circle {
                    fill: #ADD8E6;
                    stroke: steelblue;
                    stroke-width: 1.5px;
                    cursor: pointer;
                }
                .node text {
                    font: 14px sans-serif;
                    fill: #333;
                    paint-order: stroke;
                }
                .link {
                    fill: none;
                    stroke: #ccc;
                    stroke-width: 1.5px;
                }
            </style>
        </head>
        <body>
        <div id="tree-container">
            <svg width="4000" height="4000">
                <g id="main-group" transform="translate(50,50)"></g>
            </svg>
        </div>

        <script src="https://d3js.org/d3.v6.min.js"></script>
        <script>
            var data = """ + json.dumps(tree_data) + """;
            var svg = d3.select("svg");
            var g = svg.select("#main-group");

            var i = 0;
            var duration = 750;

            var root = d3.hierarchy(data, function(d) { return d.children; });
            root.x0 = 300;
            root.y0 = 0;

            const treeLayout = d3.tree().nodeSize([50, 250]); // spacing between nodes
            treeLayout(root);

            svg.call(d3.zoom().on("zoom", function(event) {
                g.attr("transform", event.transform);
            }));

            // Collapse all children initially
            if (root.children) {
                root.children.forEach(collapse);
            }
            update(root);

            function collapse(d) {
                if (d.children) {
                    d._children = d.children;
                    d._children.forEach(collapse);
                    d.children = null;
                }
            }

            function update(source) {
                const nodes = root.descendants();
                const links = root.links();

                nodes.forEach(function(d) {
                    d.y = d.depth * 250; // horizontal spacing
                });

                const node = g.selectAll("g.node")
                    .data(nodes, function(d) { return d.id || (d.id = ++i); });

                const nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .attr("transform", function(d) {
                        return "translate(" + (source.y0 || 0) + "," + (source.x0 || 0) + ")";
                    })
                    .on("click", function(event, d) {
                        if (d.children) {
                            d._children = d.children;
                            d.children = null;
                        } else {
                            d.children = d._children;
                            d._children = null;
                        }
                        update(d);
                    });

                nodeEnter.append("circle")
                    .attr("r", 10) // 🔥 Fixed radius
                    .style("fill", function(d) {
                        return d._children ? "#ADD8E6" : "#fff";
                    });

                nodeEnter.append("text")
                    .attr("dy", ".35em")
                    .attr("x", function(d) {
                        return d.children || d._children ? -16 : 16;
                    })
                    .attr("text-anchor", function(d) {
                        return d.children || d._children ? "end" : "start";
                    })
                    .text(function(d) { return d.data.name; });

                const nodeUpdate = nodeEnter.merge(node);

                nodeUpdate.transition()
                    .duration(duration)
                    .attr("transform", function(d) {
                        return "translate(" + d.y + "," + d.x + ")";
                    });

                const link = g.selectAll("path.link")
                    .data(links, function(d) { return d.target.id; });

                const linkEnter = link.enter().insert("path", "g")
                    .attr("class", "link")
                    .attr("d", function(d) {
                        const o = {x: source.x0, y: source.y0};
                        return diagonal(o, o);
                    });

                linkEnter.merge(link).transition()
                    .duration(duration)
                    .attr("d", function(d) { return diagonal(d.source, d.target); });

                nodes.forEach(function(d) {
                    d.x0 = d.x;
                    d.y0 = d.y;
                });
            }

            function diagonal(s, d) {
                return "M" + s.y + "," + s.x
                    + "C" + (s.y + d.y) / 2 + "," + s.x
                    + " " + (s.y + d.y) / 2 + "," + d.x
                    + " " + d.y + "," + d.x;
            }
        </script>
        </body>
        </html>
        """

        st.components.v1.html(d3_html, height=800, scrolling=True)
