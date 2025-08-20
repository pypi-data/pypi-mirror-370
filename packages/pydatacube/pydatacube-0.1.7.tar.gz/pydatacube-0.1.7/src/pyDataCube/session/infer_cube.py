from __future__ import annotations

import copy
from functools import reduce
from typing import List, Tuple, Any

from psycopg2.extensions import cursor as psycur
from Levenshtein import distance as levenshtein_distance

from ..cube import Level
from ..cube.AggregateFunction import AggregateFunction
from ..cube.Dimension import Dimension
from ..cube.Hierarchy import Hierarchy
from ..cube.Measure import Measure
from ..cube.NonTopLevel import NonTopLevel
from ..cube.TopLevel import TopLevel
from ..engines.postgres import Postgres
from ..session.sql_queries import ALL_USER_TABLES_QUERY, table_cardinality_query, lowest_levels_query, \
    get_non_key_columns_query, get_next_level_query, get_all_measures_query, get_pk_and_fk_columns_query, \
    check_table_existance_query


def get_fact_table(db_cursor: psycur) -> str:
    all_table_names: List[str] = get_all_table_names(db_cursor)
    result_tuple: List[Tuple[str, int]] = []
    for table_name in all_table_names:
        db_cursor.execute(table_cardinality_query(table_name))
        result_tuple.append((table_name, db_cursor.fetchall()[0][0]))

    return list(reduce(lambda x, y: x if x[1] >= y[1] else y, result_tuple))[0]

def check_table_exists(cursor: psycur, fact_table: str) -> bool:
    cursor.execute(check_table_existance_query(fact_table))
    return cursor.fetchall()[0][0]

def get_all_table_names(db_cursor: psycur) -> List[str]:
    db_cursor.execute(ALL_USER_TABLES_QUERY)
    return list(map(lambda x: x[0], db_cursor.fetchall()))


# Function assumes list to be in ascending order
def attach_relations_to_levels(hierarchy_levels: List[List[Level]]) -> List[List[Level]]:
    for levels in hierarchy_levels:
        length: int = len(levels)
        for i, level in enumerate(levels):
            child = max(0, i - 1)
            parent = min(length - 1, i + 1)
            level.child = levels[child]
            level.parent = levels[parent]
    return hierarchy_levels


def attach_levels_to_dto_list(hierarchies: List[HierarchyDTO], hierarchy_levels: List[List[Level]]) -> List[HierarchyDTO]:
    for hierarchy, levels in zip(hierarchies, hierarchy_levels):
        for k, v in zip(hierarchy.levels, levels):
            k.level = v
    return hierarchies


def create_levels_in_hierarchy(db_cursor: psycur, lowest_level: LowestLevelDTO, engine: Postgres) -> List[HierarchyDTO]:
    hierarchies: List[HierarchyDTO] = create_hierarchies(db_cursor, lowest_level.level_name, lowest_level.fact_table_fk, HierarchyDTO())
    for i, hierarchy in enumerate(hierarchies):
        hierarchy.name = f"h{i + 1}"
        hierarchy.dimension_name = lowest_level.level_name
        hierarchy.fact_table_fk = lowest_level.fact_table_fk
    hierarchy_levels: List[List[Level]] = []
    for hierarchy in hierarchies:
        levels = []
        for lv in hierarchy.levels[:-1]:
            levels.append(
                NonTopLevel(lv.name, engine, lv.attributes, lv.pk_name, lv.fk_name, level_member_attr=lv.level_member))
        levels.append(TopLevel())
        hierarchy_levels.append(levels)

    hierarchy_levels = attach_relations_to_levels(hierarchy_levels)
    hierarchies: List[HierarchyDTO] = attach_levels_to_dto_list(hierarchies, hierarchy_levels)

    return hierarchies

def create_levels(db_cursor: psycur, lowest_levels: List[LowestLevelDTO], engine: Postgres) -> List[List[HierarchyDTO]]:
    return list(map(lambda x: create_levels_in_hierarchy(db_cursor, x, engine), lowest_levels))


def get_lowest_levels(db_cursor: psycur, fact_table_name: str) -> List[LowestLevelDTO]:
    db_cursor.execute(lowest_levels_query(fact_table_name))
    result: List[Tuple[str, str]] = db_cursor.fetchall()

    return list(map(lambda x: LowestLevelDTO(x[0], x[1]), result))

class HierarchyDTO:
    def __init__(self):
        self.levels: List[LevelDTO] = []
        self.name: str = ""
        self.dimension_name: str = ""
        self.index: int = 0
        self.fact_table_fk: str = ""

    def add_level(self, level: LevelDTO) -> None:
        self.levels.append(level)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result: LevelDTO = self.levels[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return result

class LevelDTO:
    level = []

    def __init__(self,
                 level_name: str = "",
                 level_attributes: List[str] = None,
                 pk: str = "",
                 fk: str = "",
                 fact_table_fk: str = "",
                 top_level: bool = False,
                 level_member: str = ""):
        if level_attributes is None:
            level_attributes = []
        self.level_member_instances = []
        self.attributes = level_attributes
        self.pk_name = pk
        self.fk_name = fk
        self.fact_table_fk = fact_table_fk
        self.name = level_name
        self.top_level = top_level
        self.level_member = level_member

    def __repr__(self):
        return f"LevelDTO: {self.name}"


class LowestLevelDTO:
    def __init__(self, level_name, fact_table_fk):
        self.level_name = level_name
        self.fact_table_fk = fact_table_fk


def get_pk_and_fk_column_names(cursor: psycur, level_name: str) -> Tuple[str, str]:
    cursor.execute(get_pk_and_fk_columns_query(level_name))
    pk: str
    fk: str
    pk, fk = "", ""
    for t in cursor.fetchall():
        if t[1] == 'PRIMARY KEY':
            pk = t[0]
        else:
            fk = t[0]

    return pk, fk


def create_hierarchies(db_cursor: psycur,
                       current_level: str,
                       fact_table_fk: str,
                       hierarchy: HierarchyDTO) -> List[HierarchyDTO]:
    level_attributes, level_member = get_level_attributes(db_cursor, current_level)
    pk: str
    fk: str
    pk, fk = get_pk_and_fk_column_names(db_cursor, current_level)
    hierarchy.add_level(LevelDTO(current_level, level_attributes, pk, fk, fact_table_fk, level_member=level_member))
    next_levels = get_next_level_names(db_cursor, current_level)
    if not next_levels:
        hierarchy.add_level(LevelDTO("ALL", top_level=True))
        return [hierarchy]
    else:
        all_hierarchies: List[HierarchyDTO] = []
        for level in next_levels:
            new_hierarchy = create_hierarchies(db_cursor, level, fact_table_fk, copy.deepcopy(hierarchy))
            all_hierarchies.extend(new_hierarchy)
        return all_hierarchies


def get_level_attributes(db_cursor: psycur, level_name: str) -> Tuple[List[str], str]:
    db_cursor.execute(get_non_key_columns_query(level_name))
    level_attributes = list(map(lambda x: x[0], db_cursor.fetchall()))
    distances = {a: levenshtein_distance(a, level_name) for a in level_attributes}
    level_member = list(distances.keys())[list(distances.values()).index(min(distances.values()))]
    level_attributes.remove(level_member)
    return level_attributes, level_member


def get_next_level_names(db_cursor: psycur, current_level: str) -> [str]:
    db_cursor.execute(get_next_level_query(current_level))
    result: List[Tuple[str, Any]] = db_cursor.fetchall()
    return [x[0] for x in result] if result else []


def create_dimensions(hierarchies: List[List[HierarchyDTO]]) -> List[Dimension]:
    return list(map(lambda x: create_dimension(x[::-1]), hierarchies))


def create_dimension(hierarchyDTOs: List[HierarchyDTO]) -> Dimension:
    dimension_name: str = hierarchyDTOs[0].dimension_name
    hierarchies: List[Hierarchy] = []
    for hierarchy in hierarchyDTOs:
        levels: List[Level] = []
        for dto in hierarchy:
            levels.append(dto.level)
        hierarchies.append(Hierarchy(levels, hierarchy.name))
    dimension = Dimension(dimension_name, hierarchies, hierarchyDTOs[0].fact_table_fk)
    for hierarchy in hierarchies:
        hierarchy.dimension = dimension
    return dimension


def get_measures(db_cursor: psycur, fact_table: str) -> List[str]:
    db_cursor.execute(get_all_measures_query(fact_table))
    return list(map(lambda x: x[0], db_cursor.fetchall()))


def create_measures(measure_list: List[str], fact_table_name: str):
    return list(map(lambda x: create_measure(x, fact_table_name), measure_list))


def create_measure(measure: str, fact_table_name: str) -> Measure:
    sum_agg_func: AggregateFunction = AggregateFunction("SUM", lambda x, y: x + y)
    sql_name: str = f"{fact_table_name}.{measure}"
    return Measure(measure, sum_agg_func, sql_name)
