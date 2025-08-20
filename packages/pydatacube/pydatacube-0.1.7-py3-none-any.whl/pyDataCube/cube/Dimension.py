from __future__ import annotations

from typing import List, Union, TYPE_CHECKING

from rdflib import Graph

if TYPE_CHECKING:
    from .Hierarchy import Hierarchy
from .Level import Level
from .NonTopLevel import NonTopLevel


class Dimension:
    def __init__(self,
                 name: str,
                 hierarchies: List[Hierarchy],
                 fact_table_fk: str):
        self._name: str = name
        self._hierarchies: List[Hierarchy] = hierarchies
        self._metadata: Union[Graph, None] = None
        self.fact_table_fk: str = fact_table_fk
        for hierarchy in hierarchies:
            hierarchy._add_level_dimension(self)
            setattr(self, hierarchy.name, hierarchy)

    def lowest_level(self) -> NonTopLevel:
        return self._lowest_level

    @property
    def name(self) -> str:
        return self._name

    @property
    def metadata(self) -> Union[Graph, None]:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: Graph) -> None:
        self._metadata: Graph = metadata
        for level in self.levels:
            level._metadata = metadata

    @property
    def hierarchies(self) -> List[Hierarchy]:
        return self._hierarchies

    @property
    def default_hierarchy(self) -> Hierarchy:
        return self._hierarchies[0]

    @default_hierarchy.setter
    def default_hierarchy(self, hierarchy: Hierarchy) -> None:
        try:
            self._hierarchies.remove(hierarchy)
        except ValueError:
            raise ValueError(f"Hierarchy {hierarchy} not found.")
        self._hierarchies = [hierarchy] + self._hierarchies

    def __getattr__(self, item) -> Level | None:
        try:
            result = getattr(self.default_hierarchy, item)
        except AttributeError as e:
            raise AttributeError(f"Level {item} not found on default hierarchy {self.default_hierarchy} of dimension {self._name}") from e
        return result


    def __repr__(self):
        return f"{self.name}"
