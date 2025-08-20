from rdflib import Graph, Namespace
from pyshacl import validate

from .qb_integrity_constraints import constraints


class Validator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    # def validate_qb(self) -> bool:
    #     for constraint in constraints[1:]:
    #         result = self.graph.query(constraint)
    #         if result:
    #             return False

    #     return True

    def validate_qb(self) -> bool:
        QB = Namespace("http://purl.org/linked-data/cube#")
        QB4O = Namespace("http://purl.org/qb4olap#")

        for constraint in constraints[1:]:
            result = self.graph.query(constraint)
            if result:
                return True
        hej = 1
        return False
