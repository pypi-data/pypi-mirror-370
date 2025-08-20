from __future__ import annotations

from typing import Tuple, List, TYPE_CHECKING

import psycopg2
from psycopg2.extensions import connection as psyconn
from psycopg2.extensions import cursor as psycur

if TYPE_CHECKING:
    from ..cube import Measure
from ..cube.BaseCube import BaseCube
from ..cube.View import View
from ..cube.Dimension import Dimension
from ..engines.postgres import Postgres
from rdflib import Graph
from .cube_metadata import create_cube_metadata
from .infer_cube import get_fact_table, create_levels, create_dimensions, get_measures, \
    create_measures, get_lowest_levels, LowestLevelDTO, HierarchyDTO, check_table_exists


class Session:
    def __init__(self, views: List[View], engine: Postgres):
        self._views: List[View] = views
        self._engine: Postgres = engine
        for view in views:
            setattr(self, view.name, view)

    @property
    def views(self) -> List[str]:
        return list(map(lambda v: str(v), self._views))

    def load_view(self, view_name: str) -> View | str:
        view_candidate: List[View] = list(filter(lambda x: x.cube.name == view_name, self._views))
        ## Do something here which isn't as idiotic as returning a string in the case of exception
        return view_candidate[0] if len(view_candidate) == 1 else f"No view found with name: {view_name}"


def attach_metadata_to_dimensions(dimensions: List[Dimension], metadata: Graph) -> None:
    for dimension in dimensions:
        if isinstance(dimension, Dimension):
            dimension.metadata = metadata


def create_session(engine: Postgres, ud_fact_table: str = "") -> Session:
    conn: psyconn
    cursor: psycur
    with get_db_connection(engine) as conn:
        with conn.cursor() as cursor:
            if ud_fact_table:
                if not check_table_exists(cursor, ud_fact_table):
                    raise RuntimeError(f"Undefined fact table: '{ud_fact_table}'")
                fact_table: str = ud_fact_table
            else:
                fact_table: str = get_fact_table(cursor)
            lowest_levels: List[LowestLevelDTO] = get_lowest_levels(cursor, fact_table)
            hierarchyDTOs: List[List[HierarchyDTO]] = create_levels(cursor, lowest_levels, engine)

            # Renaming role playing dimensions
            rel_names: List[str] = [x[0].dimension_name for x in hierarchyDTOs]
            counter: int = 1
            for i, rel_name in enumerate(rel_names):
                if rel_name in rel_names[i + 1:]:
                    for hierarchy in hierarchyDTOs[i]:
                        hierarchy.dimension_name = hierarchy.dimension_name + str(counter)
                    counter += 1

            dimensions: List[Dimension] = create_dimensions(hierarchyDTOs)
            measures: List[Measure] = create_measures(get_measures(cursor, fact_table), fact_table)
            metadata: Graph = create_cube_metadata(fact_table, dimensions, measures)
            attach_metadata_to_dimensions(dimensions, metadata)
            cube: BaseCube = create_cube(fact_table, dimensions, measures, metadata, engine)
            view: View = View(cube=cube, name=cube.name)
            return Session([view], engine)

def get_db_connection_and_cursor(engine: Postgres) -> Tuple[psyconn, psycur]:
    conn = psycopg2.connect(user=engine.user,
                            password=engine.password,
                            host=engine.host,
                            port=engine.port,
                            database=engine.dbname)
    return conn, conn.cursor()

def get_db_connection(engine: Postgres) -> psyconn:
    conn = psycopg2.connect(user=engine.user,
                            password=engine.password,
                            host=engine.host,
                            port=engine.port,
                            database=engine.dbname)
    return conn

def create_cube(fact_table_name: str,
                dimensions: List[Dimension],
                measures: List[Measure],
                metadata: Graph,
                engine: Postgres) -> BaseCube:
    cube: BaseCube = BaseCube(fact_table_name, dimensions, measures, fact_table_name, metadata, engine)
    cube.base_cube = cube
    return cube
