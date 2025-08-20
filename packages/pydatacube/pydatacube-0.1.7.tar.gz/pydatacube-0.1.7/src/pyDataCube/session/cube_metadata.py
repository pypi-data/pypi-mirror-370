from typing import List

from rdflib import Graph, Namespace, BNode, URIRef
from rdflib.namespace import RDF, QB

from ..cube.AggregateFunction import AggregateFunction
from ..cube.Hierarchy import Hierarchy
from ..cube.Measure import Measure
from ..cube.Dimension import Dimension
from ..cube.TopLevel import TopLevel

EG = Namespace("http://example.org#")
QB4O = Namespace("http://purl.org/qb4olap/cubes#")


def create_cube_metadata(dsd_name: str,
                         dimensions: List[Dimension],
                         measures: List[Measure]) -> Graph:
    ## TODO: Generate proper URIs (or use proper prefix)
    metadata = initialize_rdf_graph()
    dsd_node = create_dsd_node(dsd_name)
    add_data_structure_definition(metadata, dsd_node)
    create_metadata_for_dimensions(dimensions, metadata, dsd_node)
    create_metadata_for_level_attributes(metadata, dimensions)
    create_metadata_for_measures(measures, metadata, dsd_node)
    # metadata.serialize(destination="session/output_test_1.ttl", format="turtle") # Temp code
    return metadata


def initialize_rdf_graph() -> Graph:
    g: Graph = Graph()
    g.bind("eg", EG)
    g.bind("qb4o", QB4O)
    return g


def create_dsd_node(dbname: str):
    # dsd_name = dbname + "_dsd"
    dsd_name = dbname
    return EG[dsd_name]


def add_data_structure_definition(metadata, dsd_node):
    metadata.add((dsd_node, RDF.type, QB.DataStructureDefinition))


def create_metadata_for_dimensions(dimensions, metadata, dsd_node):
    list(map(lambda x: create_metadata_for_dimension(x, metadata, dsd_node), dimensions))


def create_metadata_for_dimension(dimension, metadata, dsd_node):
    blank_node = BNode()
    dimension_node = EG[dimension.name]

    metadata.add((dsd_node, QB.component, blank_node))
    metadata.add((blank_node, QB4O.level, EG[dimension.lowest_level().name]))

    metadata.add((dimension_node, RDF.type, QB.DimensionProperty))

    for hierarchy in dimension.hierarchies:
        level = hierarchy.lowest_level
        while not isinstance(level.parent, TopLevel):
            level_node = EG[level.name]
            parent_level_node = EG[level.parent.name]
            metadata.add((level_node, RDF.type, QB4O.LevelProperty))
            metadata.add((level_node, QB4O.inDimension, dimension_node))
            metadata.add((level_node, QB4O.parentLevel, parent_level_node))
            level = level.parent

    level_node = EG[level.name]
    metadata.add((level_node, RDF.type, QB4O.LevelProperty))
    metadata.add((level_node, QB4O.inDimension, dimension_node))


def create_metadata_for_level_attributes(metadata: Graph, dimensions: List[Dimension]) -> None:
    list(map(lambda x: create_metadata_for_level_attribute(metadata, x.hierarchies), dimensions))


def create_metadata_for_level_attribute(metadata: Graph, hierarchies: List[Hierarchy]) -> None:
    for hierarchy in hierarchies:
        for level in hierarchy._levels:
            if type(level) is not TopLevel:
                for attribute in level.attributes:
                    metadata.add((EG[attribute], RDF.type, QB.AttributeProperty))
                    metadata.add((EG[level.name], QB4O.hasAttribute, EG[attribute]))


def create_metadata_for_measures(measures, metadata, dsd_node):
    list(map(lambda x: create_metadata_for_measure(x, metadata, dsd_node), measures))


def create_metadata_for_measure(measure, metadata, dsd_node):
    def map_agg_func_names(agg: AggregateFunction) -> URIRef:
        match agg.name:
            case "SUM":
                return QB4O.sum
            case "COUNT":
                return QB4O.count
            case "AVG":
                return QB4O.avg
            case "MIN":
                return QB4O.min
            case "MAX":
                return QB4O.max
    component_specification = BNode()
    metadata.add((dsd_node, QB.component, component_specification))
    metadata.add((component_specification, QB4O.hasAggregateFunction, map_agg_func_names(measure.aggregate_function)))
    metadata.add((component_specification, QB.measure, EG[measure.name]))
    metadata.add((EG[measure.name], RDF.type, QB.MeasureProperty))


