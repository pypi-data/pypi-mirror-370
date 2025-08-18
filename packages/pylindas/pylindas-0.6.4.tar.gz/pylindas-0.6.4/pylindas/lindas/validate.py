from pyshacl import validate
from rdflib import Graph

def validate(data_graph: Graph, shacl_graph: Graph) -> tuple:
    conforms, results_graph, text = validate(data_graph, shacl_graph=shacl_graph, abort_on_first=True, inference="none", advanced=True)
    return conforms, text