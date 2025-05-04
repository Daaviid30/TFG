import networkx as nx
import torch
from torch_geometric.data import Data
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

def process_attributes(df):
    numeric_cols = []
    categorical_cols = []
    for col in df.columns:
        try:
            df[col].astype(float)
            numeric_cols.append(col)
        except:
            categorical_cols.append(col)

    # numeric ➔ normalization 0-1
    scaler = MinMaxScaler()
    if numeric_cols:
        numeric_feats = scaler.fit_transform(df[numeric_cols].fillna(0))
    else:
        numeric_feats = np.zeros((len(df), 0))

    # categorical ➔ one-hot encoding
    ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
    if categorical_cols:
        cat_feats = ohe.fit_transform(df[categorical_cols].fillna('missing'))
    else:
        cat_feats = np.zeros((len(df), 0))

    # union
    features = np.hstack([numeric_feats, cat_feats])
    return features

def graph_to_data_full(G, label):
    # Nodes processing
    node_attrs_list = []
    for node, attrs in G.nodes(data=True):
        row = attrs.copy()
        row['node_id'] = node
        node_attrs_list.append(row)
    df_nodes = pd.DataFrame(node_attrs_list)

    node_features = process_attributes(df_nodes.drop(columns=['node_id']))
    x = torch.tensor(node_features, dtype=torch.float)

    # Edge processing
    edge_list = []
    edge_attrs_list = []
    for src, dst, attrs in G.edges(data=True):
        edge_list.append((src, dst))
        edge_attrs_list.append(attrs)

    df_edges = pd.DataFrame(edge_attrs_list)

    if not df_edges.empty:
        edge_features = process_attributes(df_edges)
        edge_attr = torch.tensor(edge_features, dtype=torch.float)
    else:
        # Void tensor if the edge has no attributes
        edge_attr = torch.zeros((len(edge_list), 0), dtype=torch.float)

    # Create edge_index
    node_idx_map = {node: idx for idx, node in enumerate(df_nodes['node_id'])}
    edges_idx = [[node_idx_map[src], node_idx_map[dst]] for src, dst in edge_list]
    edge_index = torch.tensor(edges_idx, dtype=torch.long).t().contiguous()

    # Label
    y = torch.tensor([label], dtype=torch.long)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=y)

# Ejemplo de uso con tus grafos
paths_labels = [
    ("/mnt/data/webGraphWithoutExtension.gexf", 0),  # Benigno
    ("/mnt/data/webGraph.gexf", 1),                 # Malicioso
    ("/mnt/data/graph_diff.gexf", 1),               # Malicioso (solo diff)
]

dataset = []
for path, label in paths_labels:
    G = nx.read_gexf(path)
    data = graph_to_data_full(G, label)
    dataset.append(data)

print(f"{len(dataset)} grafos convertidos con nodos+aristas ✅")
