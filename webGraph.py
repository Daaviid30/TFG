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

    # Adding all the nodes to the graph
    for node in report:
        type = node["nodeType"]
        if type == "apiCall":
            graph.add_node(node["apiCall"], color = "#FF002E")
        elif type == "domElement":
            graph.add_node(node["elementID"], color = "#FFC500")
        elif type == "eventListener":
            graph.add_node(node["type"], color = "#CDFF00")
        elif type == "executionContext":
            graph.add_node(node["executionContextID"], color = "#00FF00")
        elif type == "extension":
            graph.add_node(node["extensionID"], color = "#0000FF")
        elif type == "network":
            graph.add_node(node["requestID"], color = "#00FFBD")
        elif type == "page":
            graph.add_node(node["pageID"], color = "#00D1FF")
        elif type == "script":
            graph.add_node(node["scriptID"], color = "#FF008F")
        elif type == "target":
            if node["event"] == "create":
                graph.add_node(node["targetID"], color = "#909090")

    # Export the graph to a gexf file (for Gephi visualitation)
    nx.write_gexf(graph, "webGraph.gexf")
