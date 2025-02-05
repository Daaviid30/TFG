import networkx as nx
import matplotlib.pyplot as plt

def crear_grafo(informacion_json):
    """
    Crea y visualiza un grafo con mejor disposición de nodos para reducir cruces de aristas.
    """
    G = nx.DiGraph()  # Grafo dirigido
    
    nodos_trafico = []
    nodos_script = []
    
    ultimo_trafico = None  

    # Agregar nodos y clasificar por tipo
    for nodo in informacion_json:
        nodo_id = nodo.get("request_ID", nodo.get("script_ID"))
        
        if "request_ID" in nodo:  # Nodo de tráfico
            G.add_node(nodo_id, tipo="trafico", label=f"{nodo['url']}")
            nodos_trafico.append(nodo_id)
            
            # Conectar con la solicitud anterior (secuencia de navegación)
            if ultimo_trafico:
                G.add_edge(ultimo_trafico, nodo_id, tipo="navegacion", label="Siguiente")
            ultimo_trafico = nodo_id

        elif "script_ID" in nodo:  # Nodo de script
            G.add_node(nodo_id, tipo="script", label=f"Script {nodo['script_ID']}")
            nodos_script.append(nodo_id)
            
            # Relacionamos el script con la URL que lo cargó
            initiator = nodo.get("initiator")
            if initiator and initiator in G.nodes:
                G.add_edge(initiator, nodo_id, tipo="carga_script", label="Carga")

    # Conectar initiators que no sean nodos de tráfico o scripts ya registrados
    for nodo in informacion_json:
        source = nodo.get("initiator")
        target = nodo.get("request_ID", nodo.get("script_ID"))

        if source:
            if source not in G.nodes:
                G.add_node(source, tipo="initiator", label=f"Iniciador {source}")  # Nodo genérico
            G.add_edge(source, target, tipo="relacion", label="Inicia")

    # 📌 Disposición mejorada de nodos
    pos = nx.kamada_kawai_layout(G)  # Distribuye los nodos minimizando solapamientos

    # Dibujamos nodos con diferentes estilos
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_trafico, node_color="skyblue", node_shape="o", node_size=700)
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_script, node_color="lightcoral", node_shape="s", node_size=700)
    
    # Dibujamos conexiones
    edges = G.edges(data=True)
    edge_labels = { (u, v): d["label"] for u, v, d in edges }
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    
    # Añadimos etiquetas a los nodos
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color="black")

    # Mostramos el grafo
    plt.title("Grafo de Navegación y Scripts (Optimizado)")
    plt.show()
