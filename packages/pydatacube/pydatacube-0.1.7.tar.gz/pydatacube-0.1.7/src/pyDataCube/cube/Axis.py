from __future__ import annotations

from typing import List, TYPE_CHECKING

from .Attribute import Attribute
from .Dimension import Dimension
from .Hierarchy import Hierarchy
from .LevelMemberType import LevelMemberType

if TYPE_CHECKING:
    from .NonTopLevel import NonTopLevel
    from .LevelMember import LevelMember


class Axis:
    def __init__(self, dimension: Dimension = None, hierarchy: Hierarchy = None, level: NonTopLevel = None,
                 attribute: Attribute = None, level_member: List[LevelMember] = None) -> None:
        self.dimension = dimension
        self.hierarchy = hierarchy
        self.level: NonTopLevel = level
        self.attribute = attribute
        if level_member:
            self.level_members: List[LevelMember] = level_member
            self.type: LevelMemberType = LevelMemberType.STR if type(level_member[0].name) is str else LevelMemberType.INT
        else:
            self.level_members = []

    def __repr__(self) -> str:
        return f"Axis(Dimension: {self.dimension}, Level: {self.level}, Attribute: {self.attribute}, Level Members: {self.level_members})"