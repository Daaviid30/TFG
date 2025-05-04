import networkx as nx
import torch
from torch_geometric.data import Data
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler


#---------------------- PRE-PROCESSING ------------------------------

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


# Carga de grafos
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


#------------------------- MODELO ------------------------------------
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import NNConv, global_mean_pool

class GNNMalwareDetector(nn.Module):
    def __init__(self, node_feat_dim, edge_feat_dim, hidden_dim=64):
        super(GNNMalwareDetector, self).__init__()

        # Red pequeña para transformar edge_attr ➔ weights para NNConv
        self.edge_mlp = nn.Sequential(
            nn.Linear(edge_feat_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_feat_dim * hidden_dim)
        )

        # NNConv usa edge_attr para pesar la agregación
        self.conv1 = NNConv(node_feat_dim, hidden_dim, self.edge_mlp, aggr='mean')
        self.conv2 = NNConv(hidden_dim, hidden_dim, self.edge_mlp, aggr='mean')

        # Clasificador final
        self.lin = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2)  # 2 clases: benigno o malicioso
        )

    def forward(self, data):
        x, edge_index, edge_attr, batch = data.x, data.edge_index, data.edge_attr, data.batch

        x = F.relu(self.conv1(x, edge_index, edge_attr))
        x = F.relu(self.conv2(x, edge_index, edge_attr))

        x = global_mean_pool(x, batch)  # Pooling global por grafo

        out = self.lin(x)
        return out

#----------------------------- TRAINING -----------------------------
from torch_geometric.loader import DataLoader
from sklearn.metrics import classification_report

def train(model, loader, optimizer, criterion):
    model.train()
    total_loss = 0
    for data in loader:
        optimizer.zero_grad()
        out = model(data)
        loss = criterion(out, data.y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)

def evaluate(model, loader):
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for data in loader:
            out = model(data)
            preds = out.argmax(dim=1).cpu().numpy()
            labels = data.y.cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels)
    return all_labels, all_preds


#------------------------- PRECISION --------------------------------
# Dataset: ya lo tienes cargado como `dataset` ✅
# OJO: si quieres más datos, añade más grafos a `dataset`

from sklearn.model_selection import train_test_split

# Split train/test (80% train, 20% test)
train_dataset, test_dataset = train_test_split(dataset, test_size=0.2, random_state=42)

train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=2)

# Modelo
node_feat_dim = dataset[0].x.shape[1]
edge_feat_dim = dataset[0].edge_attr.shape[1]

model = GNNMalwareDetector(node_feat_dim, edge_feat_dim)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Entrenamiento
for epoch in range(20):  # 20 epochs
    loss = train(model, train_loader, optimizer, criterion)
    print(f"Epoch {epoch+1}, Loss: {loss:.4f}")

# Evaluación
labels, preds = evaluate(model, test_loader)

print("\n📊 Classification Report:")
print(classification_report(labels, preds, target_names=['Benigno', 'Malicioso']))
