import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import os

st.set_page_config(layout="wide")
st.title("Network Graph Explorer with Label Search")

# --- Load CSVs from disk ---
nodes = pd.read_csv("nodes.csv")   # Replace with your actual file path
edges = pd.read_csv("edges.csv")   # Replace with your actual file path

# --- Ensure IDs are strings for compatibility ---
nodes["ID"] = nodes["ID"].astype(str)
edges["Source"] = edges["Source"].astype(str)
edges["Target"] = edges["Target"].astype(str)

# --- Build the graph ---
G = nx.from_pandas_edgelist(edges, source="Source", target="Target")

# Add node attributes (optional)
for _, row in nodes.iterrows():
    node_id = row["ID"]
    attr = row.drop("ID").to_dict()
    nx.set_node_attributes(G, {node_id: attr})

# --- Build label ↔ ID maps ---
label_to_id = {row["Label"]: row["ID"] for _, row in nodes.iterrows()}
id_to_label = {row["ID"]: row["Label"] for _, row in nodes.iterrows()}

# --- Filter dropdown labels (exclude certain keywords) ---
exclude_keywords = ["Overall", "Trade"]
dropdown_labels = sorted(
    nodes[~nodes["Label"].str.contains("|".join(exclude_keywords), case=False, na=False)]["Label"].unique()
)

# --- User selects source/target via label ---
col1, col2 = st.columns(2)
with col1:
    source_label = st.selectbox("Select Start Node (Label)", dropdown_labels)
with col2:
    target_label = st.selectbox("Select End Node (Label)", dropdown_labels, index=1 if len(dropdown_labels) > 1 else 0)

# Convert labels to string node IDs
source = str(label_to_id[source_label])
target = str(label_to_id[target_label])

# --- Show shortest path if button clicked ---
if st.button("Show Connection"):
    if source == target:
        st.warning("Please select two different nodes.")
    elif source not in G.nodes or target not in G.nodes:
        st.error("Selected node(s) not found in the current graph.")
    elif nx.has_path(G, source, target):
        path = nx.shortest_path(G, source=source, target=target)
        path_edges = [(str(path[i]), str(path[i + 1])) for i in range(len(path) - 1)]

        # Create a subgraph of the shortest path
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(path)
        subgraph.add_edges_from(path_edges)

        # Create and style the Pyvis network
        net = Network(height="600px", width="100%", directed=True)
        net.from_nx(subgraph)

        for node in path:
            net_node = net.get_node(str(node))
            net_node["label"] = id_to_label.get(str(node), str(node))
            net_node["title"] = f"Node: {id_to_label.get(str(node), str(node))}"

        # Render HTML and show in Streamlit
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, 'r', encoding='utf-8') as f:
            html = f.read()
            st.components.v1.html(html, height=600, scrolling=True)

        os.remove(tmp_path)
    else:
        st.error(f"No connection found between **{source_label}** and **{target_label}**.")
