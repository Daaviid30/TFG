"""
AUTOR: David Martín Castro
This script create the WG (Web Graph) from the report.json created based on the navigation
events captured by CDP (Chrome DevTools Protocol).
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import networkx as nx

#--------------------------- GRAPH CREATION ------------------------------

def create_graph(report: dict):
    # Create a directed graph
    graph = nx.DiGraph()
    # Create a dict for create edges in the future
    related_nodes = {}
    # Adding all the nodes to the graph
    for node in report:
        type = node["nodeType"]
        if type == "apiCall":
            related_nodes[node["apiCall"]] = []
            graph.add_node(node["apiCall"], viz={"color": {"r": 255, "g": 0, "b": 46}})
        elif type == "domElement":
            related_nodes[node["elementID"]] = []
            graph.add_node(node["elementID"], viz={"color": {"r": 255, "g": 197, "b": 0}})
        elif type == "eventListener":
            related_nodes[node["type"]] = []
            graph.add_node(node["type"], viz={"color": {"r": 205, "g": 255, "b": 0}})
        elif type == "executionContext":
            related_nodes[node["executionContextID"]] = []
            graph.add_node(node["executionContextID"], viz={"color": {"r": 0, "g": 255, "b": 0}})
        elif type == "extension":
            related_nodes[node["extensionID"]] = []
            graph.add_node(node["extensionID"], viz={"color": {"r": 0, "g": 0, "b": 255}})
        elif type == "network":
            related_nodes[node["requestID"]] = []
            graph.add_node(node["requestID"], viz={"color": {"r": 0, "g": 255, "b": 189}})
        elif type == "page":
            related_nodes[node["pageID"]] = []
            graph.add_node(node["pageID"], viz={"color": {"r": 0, "g": 209, "b": 255}})
        elif type == "script":
            related_nodes[node["scriptID"]] = []
            graph.add_node(node["scriptID"], viz={"color": {"r": 255, "g": 0, "b": 143}})
        elif type == "target":
            if node["event"] == "create":
                related_nodes[node["targetID"]] = []
                graph.add_node(node["targetID"], viz={"color": {"r": 144, "g": 144, "b": 144}})

    # Adding all the edges to the graph
    for node in report:
        type = node["nodeType"]
        if type == "page":
            try:
                graph.add_edge(node["frameID"], node["pageID"])
            except:
                pass
        elif type == "executionContext":
            try:
                graph.add_edge(node["pageID"], node["executionContextID"])
            except:
                pass
        elif type == "extension":
            try:
                graph.add_edge(node["executionContextID"], node["extensionID"])
            except:
                pass
        elif type == "script":
            try:
                graph.add_edge(node["executionContextID"], node["scriptID"])
            except:
                pass
        elif type == "domElement":
            try:
                graph.add_edge(node["initiator"], node["elementID"])
            except:
                pass
        elif type == "apiCall":
            try:
                graph.add_edge(node["scriptID"], node["apiCall"])
            except:
                pass
        elif type == "eventListener":
            try:
                graph.add_edge(node["scriptID"], node["type"])
            except:
                pass
            

    # Export the graph to a gexf file (for Gephi visualitation)
    nx.write_gexf(graph, "webGraph.gexf")
