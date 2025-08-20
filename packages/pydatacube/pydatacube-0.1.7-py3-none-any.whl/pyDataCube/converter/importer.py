from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as psyconn
from rdflib import Graph, Namespace, Node

from ..cube.Attribute import Attribute
from ..cube.Axis import Axis
from ..cube.BaseCube import BaseCube
from ..cube.Dimension import Dimension
from ..cube.Hierarchy import Hierarchy
from ..cube.Level import Level
from ..cube.LevelMember import LevelMember
from ..cube.TopLevel import TopLevel
from ..engines.postgres import Postgres
from ..engines.engine import Engine
from ..cube.AggregateFunction import AggregateFunction
from ..cube.Measure import Measure
from ..cube.NonTopLevel import NonTopLevel
from ..cube.View import View
from ..session.session import Session
from ..session.sql_queries import get_non_key_columns_query, get_pk_and_fk_columns_query, lowest_levels_query


class QB4OLAPImporter:
    def __init__(self, filename: str, engine: Engine) -> None:
        self.filename: str = filename
        self.engine: Engine = engine
        self.fact_table: str = ""
        self.measures: list[Measure] = []
        self.dimensions: list[Dimension] = []
        self.views: list[View] = []
        self.QB: Namespace = Namespace("http://purl.org/linked-data/cube#")
        self.RDF: Namespace = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.QB4O: Namespace = Namespace("http://purl.org/qb4olap/cubes#")
        self.processed_dimensions: dict[Node, list[Node]] = {}
        self.processed_keys: list[str] = []

    def importer(self) -> Session:
        g = Graph()
        g.parse(self.filename, format="ttl")

        dsd_nodes: list[Node] = self._find_dsd_nodes(g)
        if not dsd_nodes:
            raise Exception(f"No data structure definition found in {self.filename}")
        else:
            for dsd in dsd_nodes:
                self._process_dsd(g, dsd)

        return Session(self.views, self.engine)

    def _process_dsd(self, g: Graph, dsd: Node) -> None:
        self.fact_table = self._extract_name(dsd)
        for _, _, component_specification in g.triples((dsd, self.QB.component, None)):
            self._process_component_specification(g, component_specification)

        for dimension in self.dimensions:
            dimension.metadata = g

        cube: BaseCube = BaseCube(self.fact_table, self.dimensions, self.measures, self.fact_table, g, self.engine)
        cube.base_cube = cube
        axes: list[Axis] = []
        for dimension in self.dimensions:
            hierarchy: Hierarchy = dimension.hierarchies[0]
            level: NonTopLevel = hierarchy.lowest_level
            attribute: Attribute = level.level_member_attr
            level_members: list[LevelMember] = attribute.members()
            axes.append(Axis(dimension, hierarchy, level, attribute, level_members))

        measures: list[Measure] = cube.measure_list[0] if cube.measure_list else []
        predicates: None = None
        self.views.append(View(cube=cube, name=cube.name))

    def _process_component_specification(self, g: Graph, comp_spec: Node) -> None:
        for _, comp_prop, Comp_Prop in g.triples((comp_spec, None, None)):
            match comp_prop:
                case self.QB.measure:
                    self.measures.append(self._process_measure(g, comp_spec))
                case self.QB4O.level:
                    self.dimensions.append(self._process_dimension(g, Comp_Prop))
                case self.QB4O.hasAggregateFunction:
                    continue
                case _:
                    print(f"Only considering {self.QB4O.measure} and {self.QB4O.level} properties in DataStructureDefinition. Found {_}")

    def _process_measure(self, g: Graph, comp_spec: Node) -> Measure:
        name: str = ""
        sql: str = ""
        agg_func: AggregateFunction | None = None
        for _, comp_prop, Comp_Prop in g.triples((comp_spec, None, None)):
            match comp_prop:
                case self.QB.measure:
                    measure_str: str = Comp_Prop.toPython()
                    name = measure_str[measure_str.find("#") + 1:]
                    sql = f"{self.fact_table}.{name}"
                case self.QB4O.hasAggregateFunction:
                    try:
                        agg_func = self._process_aggregate_function(Comp_Prop)
                    except NotImplementedError as e:
                        raise e
                    except Exception as e:
                        raise Exception(f"Unknown triple ({comp_spec, comp_prop, Comp_Prop})") from e
                case _:
                    raise Exception(f"Unknown component property {comp_prop} leading Component Property {Comp_Prop} leading to component specification {comp_spec} (triple ({comp_spec}, {comp_prop}, {Comp_Prop}) is invalid)")
        if not (name and sql and agg_func):
            raise Exception(f"Incomplete measure specification {comp_spec}")
        else:
            return Measure(name, agg_func, sql)

    def _process_aggregate_function(self, agg_func: Node) -> AggregateFunction:
        func: str = agg_func.toPython()
        name: str = func[func.find("#") + 1:]
        match name:
            case "sum":
                return AggregateFunction("SUM", lambda x, y: x + y)
            case "min":
                return AggregateFunction("MIN", lambda x, y: x if x < y else y)
            case "max":
                return AggregateFunction("MAX", lambda x, y: x if x > y else y)
            case "count":
                return AggregateFunction("COUNT", lambda acc, x: acc + 1)
            case "avg":
                return AggregateFunction("AVG", lambda x, y: x)
            case _:
                raise Exception(f"Unknown aggregate function {agg_func}")

    def _get_keys(self, lvl_name: str) -> tuple[str, str]:
        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(get_pk_and_fk_columns_query(lvl_name))
                pk: str
                fk: str
                pk, fk = "", ""
                for t in cur.fetchall():
                    if t[1] == 'PRIMARY KEY':
                        pk = t[0]
                    else:
                        fk = t[0]
        return pk, fk

    def _get_level_member_attribute(self, lvl_name: str, lvl_attrs: list[str]) -> str:
        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(get_non_key_columns_query(lvl_name))
                all_attrs = list(map(lambda x: x[0], cur.fetchall()))

        lvl_member_attrs: list[str] = [x for x in all_attrs if x not in lvl_attrs]
        if len(lvl_member_attrs) > 1:
            raise Exception(f"Found multiple level member attributes: {lvl_member_attrs} for level '{lvl_name}'")
        if len(lvl_member_attrs) == 0:
            raise Exception(f"Found no level member attribute for level '{lvl_name}'")
        return lvl_member_attrs[0]

    def _get_next_level(self, g: Graph, Comp_Prop: Node) -> list[Node]:
        return [x[2] for x in g.triples((Comp_Prop, self.QB4O.parentLevel, None))]

    def _process_dimension(self, g: Graph, Comp_Prop: Node) -> Dimension:
        dim_props: list[Node] = list(g.objects(Comp_Prop, self.QB4O.inDimension))
        if len(dim_props) > 1:
            chosen_dimension: Node = [x for x in dim_props if x not in self.processed_dimensions.setdefault(Comp_Prop, [])][0]
            self.processed_dimensions[Comp_Prop].append(chosen_dimension)
        else:
            chosen_dimension: Node = dim_props[0]
        dimension_name: str = self._extract_name(chosen_dimension)

        hierarchies: list[HierarchyContainer] = []
        hierarchy_counter: int = 0
        def traverse(path: list[Node]) -> None:
            current_node = path[-1]
            next_levels = self._get_next_level(g, current_node)

            if not next_levels:
                hierarchy_container = HierarchyContainer()
                nonlocal hierarchy_counter
                hierarchy_counter += 1
                hierarchy_container.name = f"h{hierarchy_counter}"

                for node in path:
                    container = LevelContainer()
                    container.lvl_name = self._extract_name(node)
                    container.lvl_attrs = list(map(lambda x: self._extract_name(x[2]),
                                                   g.triples((node, self.QB4O.hasAttribute, None))))
                    container.lvl_member_attr = self._get_level_member_attribute(container.lvl_name,
                                                                                 container.lvl_attrs)
                    container.pk, container.fk = self._get_keys(container.lvl_name)
                    hierarchy_container.levels.append(container)

                hierarchies.append(hierarchy_container)
                return

            for next_node in next_levels:
                traverse(path + [next_node])

        traverse([Comp_Prop])

        more_hierarchies: list[Hierarchy] = []
        for hierarchy in hierarchies:
            lvls: list[Level] = []
            for level in hierarchy:
                lvls.append(NonTopLevel(level.lvl_name, self.engine, level.lvl_attrs, level.pk, level.fk, level.lvl_member_attr))
            lvls.append(TopLevel())
            self._attach_relations_to_levels2(lvls)
            more_hierarchies.append(Hierarchy(lvls, hierarchy.name))


        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(lowest_levels_query(self.fact_table))
                result: list[tuple[any, ...]] = cur.fetchall()
                candidate_keys: list[str] = [x[1] for x in result if x[0] == more_hierarchies[0].lowest_level.name]
                fact_table_fk: str = [x for x in candidate_keys if x not in self.processed_keys][0]
                self.processed_keys.append(fact_table_fk)

        return Dimension(dimension_name, more_hierarchies, fact_table_fk)

    def _attach_relations_to_levels2(self, hierarchy: list[Level]) -> list[Level]:
        length: int = len(hierarchy)
        for i, level in enumerate(hierarchy):
            child = max(0, i - 1)
            parent = min(length - 1, i + 1)
            level.child = hierarchy[child]
            level.parent = hierarchy[parent]
        return hierarchy


    def _attach_relations_to_levels(self, hierarchy_levels: list[list[Level]]) -> list[list[Level]]:
        for levels in hierarchy_levels:
            length: int = len(levels)
            for i, level in enumerate(levels):
                child = max(0, i - 1)
                parent = min(length - 1, i + 1)
                level.child = levels[child]
                level.parent = levels[parent]
        return hierarchy_levels

    def _find_dsd_nodes(self, graph: Graph) -> list[Node]:
        return list(graph.subjects(predicate=None, object=self.QB.DataStructureDefinition))

    def _extract_name(self, node: Node) -> str:
        node_str: str = node.toPython()
        return node_str[node_str.find("#") + 1:]

    def _get_db_connection(self) -> psyconn | None:
        engine = self.engine
        if isinstance(engine, Postgres):
            return psycopg2.connect(user=engine.user,
                                    password=engine.password,
                                    host=engine.host,
                                    port=engine.port,
                                    database=engine.dbname)



class LevelContainer:
    def __init__(self) -> None:
        self.lvl_name: str = ""
        self.lvl_attrs: list[str] = []
        self.lvl_member_attr: str = ""
        self.pk: str = ""
        self.fk: str = ""


class HierarchyContainer:
    def __init__(self) -> None:
        self.name: str = ""
        self.levels: list[LevelContainer] = []

    def __iter__(self) -> Iterator[LevelContainer]:
        for i in range(len(self.levels)):
            yield self.levels[i]