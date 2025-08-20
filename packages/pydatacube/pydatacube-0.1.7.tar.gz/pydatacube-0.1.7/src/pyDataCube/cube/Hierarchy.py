from typing import List, TypeVar, Union

from rdflib import Graph

from .Dimension import Dimension
from .Level import Level
from .NonTopLevel import NonTopLevel
from .TopLevel import TopLevel

level = TypeVar("level", bound=Level)

class Hierarchy:
    def __init__(self, levels: List[level], name: str = "", dimension: Dimension = None) -> None:
        self._levels: List[Level] = levels
        self._lowest_level: NonTopLevel = levels[0]
        self.name: str = name
        self.dimension: Dimension = dimension
        self._metadata: Union[Graph, None] = None
        for level in levels:
            if not isinstance(level, TopLevel):
                setattr(self, level.name, level)


    @property
    def levels(self) -> List[Level] | None:
        return self._levels

    @property
    def metadata(self) -> Union[Graph, None]:
        return self._metadata


    @metadata.setter
    def metadata(self, metadata: Graph) -> None:
        self._metadata: Graph = metadata
        for level in self._levels:
            level._metadata = metadata

    @property
    def lowest_level(self) -> NonTopLevel:
        return self._lowest_level

    def rename(self, name: str) -> None:
        setattr(self.dimension, name, self)
        delattr(self.dimension, self.name)
        self.name = name

    def _add_level_dimension(self, dimension: Dimension) -> None:
        for level in self._levels:
            level.dimension = dimension

    def __repr__(self) -> str:
        return self.name