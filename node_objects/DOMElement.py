"""
AUTOR: David Martín Castro
This script contains the DOMElementNode class, which is used to represent a DOM element node in the graph.
"""

#------------------------------------ CLASS DEFINITION ------------------------------------

class DOMElementNode:

    # Constructor definition
    def __init__(self, elementID: str, type, name: str, initiator, timestamp: int) -> None:

        self.nodeType = "domElement"
        self.elementID = elementID
        self.type = type
        self.name = name
        self.initiator = initiator
        self.timestamp = timestamp

    # str method definition, used to print the node
    def __str__(self) -> str:

        domElement_str = f"Node {self.nodeType}:\n"\
            f"\t- elementID: {self.elementID}\n"\
            f"\t- type: {self.type}\n"\
            f"\t- name: {self.name}\n"\
            f"\t- initiator: {self.initiator}\n"\
            f"\t- timestamp: {self.timestamp}\n"
        
        return domElement_str
    
    # method used to convert the node to a dictionary
    def to_dict(self) -> dict:

        dict = {
            "nodeType": self.nodeType,
            "elementID": self.elementID,
            "type": self.type,
            "name": self.name,
            "initiator": self.initiator,
            "timestamp": self.timestamp
        }

        return dict