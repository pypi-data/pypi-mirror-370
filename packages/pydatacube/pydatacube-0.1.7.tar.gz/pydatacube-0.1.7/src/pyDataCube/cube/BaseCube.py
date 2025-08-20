from __future__ import annotations

from typing import List, TypeVar, Any, Tuple, Deque

from rdflib import Graph

from .Cube import Cube
from .Level import Level
from .LevelMember import LevelMember
from .Measure import Measure
from .Dimension import Dimension
from .NonTopLevel import NonTopLevel
from .TopLevel import TopLevel
from ..engines.postgres import Postgres

DataFrame = TypeVar("DataFrame")


def construct_query(select_stmt: str, from_stmt: str, where_stmt: str, group_by_stmt: str,
                    order_by_stmt: str = "") -> str:
    stmt_list: List[str] = [select_stmt, from_stmt, where_stmt, group_by_stmt, order_by_stmt]
    return " ".join(stmt_list) + ";"


def go_to_parent(current_level):
    return current_level.parent


def go_to_child(current_level):
    return current_level.child


def get_hierarchy_up_to_current_level(dimension, level):
    hierarchy = dimension.hierarchies()
    return hierarchy[:hierarchy.index(level) + 1]


def get_fact_table_join_stmt(fact_table_name: str, lowest_level: NonTopLevel) -> str:
    return f"{fact_table_name}.{lowest_level.dimension.fact_table_fk} = {lowest_level.name}.{lowest_level.key}"


def get_hierarchy_table_join_stmt(fact_table_name: str, join_tables: List[NonTopLevel]) -> str:
    hierarchy_table_join: List[str] = [get_fact_table_join_stmt(fact_table_name, join_tables[0])]
    for i in range(0, len(join_tables) - 1):
        hierarchy_table_join.append(
            f"{join_tables[i].name}.{join_tables[i].fk_name} = {join_tables[i + 1].name}.{join_tables[i + 1].key}")

    return " AND ".join(hierarchy_table_join)


def get_list_of_values(lms: List[LevelMember]) -> List[str]:
    value_list: List[str] = []
    if type(lms[0].name) is int:
        for column in lms:
            value_list.append(f"{column.name}")
    else:
        for column in lms:
            value_list.append(f"'{column.name}'")
    return value_list


def get_table_and_column_name(column_level: NonTopLevel) -> str:
    return f"{column_level.name}.{column_level.column_name}"


def _fill_in_missing_values_for_df(values: Deque[Tuple[Any, ...]],
                                   columns: List[str | int],
                                   rows: List[str | int],
                                   length: int) -> List[List[float]]:
    values_with_missing: List[List[float]] = []
    for row in rows:
        row_value = []
        for column in columns:
            if values and (column and row in values[0]):
                row_value.append(values.popleft()[length])
            else:
                row_value.append(None)
        values_with_missing.append(row_value)
    return values_with_missing


def get_tables_above(level: Level) -> List[NonTopLevel]:
    result: List[NonTopLevel] = []
    while level != level.parent:
        level = level.parent
        if isinstance(level, NonTopLevel):
            result.append(level)
    return list(result)


def get_tables_below_including(level: Level) -> List[NonTopLevel]:
    result: List[NonTopLevel] = [level]
    while level != level.child:
        level: NonTopLevel = level.child
        result.append(level)
    return list(reversed(result))


def get_ancestor_lm_and_values(lm_list: List[LevelMember]) -> List[Tuple[NonTopLevel, List[LevelMember], bool]]:
    result: List[Tuple[NonTopLevel, List[LevelMember], bool]] = []
    anc_amount: int = 0
    parent_lm: LevelMember = lm_list[0].parent
    while parent_lm is not None:
        anc_amount += 1
        parent_lm: LevelMember = parent_lm.parent
    for i in range(0, anc_amount):
        lms: List[LevelMember] = []
        level: NonTopLevel | None = None
        for lm in lm_list:
            lm: LevelMember = lm.parent
            level: NonTopLevel = lm.level
            is_int: bool = True if type(lm.name) is int else False
            lms.append(lm)
        result.append((level, lms, is_int))
    return result


def get_ancestor_value_stmt(level_member: List[LevelMember]) -> str:
    lm_value_list: List[Tuple[NonTopLevel, List[LevelMember], bool]] = get_ancestor_lm_and_values(level_member)
    result: List[str] = []
    for k, v, is_int in lm_value_list:
        values = ", ".join(list(map(lambda x: str(x.name), v)))
        if is_int:
            result.append(f"{k.name}.{k.column_name} IN ({values})")
        else:
            result.append(f"{k.name}.{k.column_name} IN ('{values}')")
    if result:
        return " AND ".join(result)
    else:
        return ""


def get_current_value_stmt(value_list: List[LevelMember]) -> str:
    column_level: str = get_table_and_column_name(value_list[0].level)
    value_list: List[str] = get_list_of_values(value_list)
    values: str = "(" + ", ".join(value_list) + ")"
    return f" {column_level} IN {values}"


def _get_all_value_list(value_list: List[LevelMember]) -> List[LevelMember]:
    if value_list[0].level.all_lm_loaded:
        return value_list
    result: List[List[LevelMember]] = []
    for value in value_list:
        original_value = value
        while value.parent:
            value = value.parent
        if isinstance(value.level.parent, TopLevel):
            result.append([original_value])
        else:
            tmp: List[LevelMember] = []
            parents: List[NonTopLevel] = []
            level = value.level.parent
            while not isinstance(level, TopLevel):
                parents.append(level)
                level = level.parent
            parents = list(reversed(parents))
            parent_lms: List[LevelMember] = parents[0].members()
            for i in range(1, len(parents)):
                tmp: List[List[LevelMember]] = list(map(lambda x: x.children, parent_lms))
                parent_lms = [item for sublist in tmp for item in sublist]

            for lm in parent_lms:
                try:
                    level_member: LevelMember = lm[value.name]
                    tmp.append(level_member)
                except AttributeError:
                    continue
            result.append(tmp)

    return [x for value in result for x in value]


class BaseCube(Cube):
    def __init__(
            self,
            fact_table_name: str,
            dimension_list: List[Dimension],
            measure_list: List[Measure],
            name: str,
            metadata: Graph,
            engine: Postgres,
    ):
        super().__init__(dimension_list, measure_list, engine, base_cube=None, next_cube=None)
        self.fact_table_name: str = fact_table_name
        self._dimension_list: List[Dimension] = dimension_list
        self._name: str = name
        self._metadata: Graph = metadata
        self._condition = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def measures(self):
        return self._measure_list

    @property
    def dimensions(self):
        return self._dimension_list

    def delete_measure(self, measure: Measure):
        if measure in self.measure_list:
            self.measure_list.remove(measure)
            del self.__dict__[measure.name]
        else:
            raise AttributeError(f"Measure {measure.name} does not exist in the measure list of cube {self.name}")

    def __repr__(self):
        return self.name

