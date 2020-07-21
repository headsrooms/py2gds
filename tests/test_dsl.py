from py2gds.algorithms.algorithm import AlgorithmType
from py2gds.algorithms.rank import (
    WriteArticleRank,
    StreamArticleRank,
    StreamPageRank,
    WritePageRank,
)
from py2gds.algorithms.rank_configuration import RankConfiguration
from py2gds.connection import GraphConnection
from py2gds.dsl import Query
from py2gds.projection import Projection


def test_stream_articlerank(
    graph_connection: GraphConnection, pages_and_links_projection: Projection
):
    manual_query = StreamArticleRank(
        graph_connection, pages_and_links_projection, RankConfiguration(),
    ).cypher

    dsl_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
    )

    assert manual_query == str(dsl_query)


def test_write_articlerank(
    graph_connection: GraphConnection, pages_and_links_projection: Projection
):
    manual_query = WriteArticleRank(
        graph_connection,
        pages_and_links_projection,
        RankConfiguration(write_property="test_property"),
    ).cypher

    dsl_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .write("test_property")
    )

    assert manual_query == str(dsl_query)


def test_stream_pagerank(
    graph_connection: GraphConnection, pages_and_links_projection: Projection
):
    manual_query = StreamPageRank(
        graph_connection, pages_and_links_projection, RankConfiguration(),
    ).cypher

    dsl_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.PageRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
    )

    assert manual_query == str(dsl_query)


def test_write_pagerank(
    graph_connection: GraphConnection, pages_and_links_projection: Projection
):
    manual_query = WritePageRank(
        graph_connection,
        pages_and_links_projection,
        RankConfiguration(write_property="test_property"),
    ).cypher

    dsl_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.PageRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .write("test_property")
    )

    assert manual_query == str(dsl_query)


def test_query_order(graph_connection: GraphConnection,):
    dsl_query_1 = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.PageRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .write("test_property")
    )

    dsl_query_2 = (
        Query.using(graph_connection)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .rank(algorithm=AlgorithmType.PageRank)
        .write("test_property")
    )

    dsl_query_3 = (
        Query.using(graph_connection)
        .write("test_property")
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .rank(algorithm=AlgorithmType.PageRank)
    )

    dsl_query_4 = (
        Query.rank(algorithm=AlgorithmType.PageRank)
        .using(graph_connection)
        .write("test_property")
        .projected_by(labels=("Page",), relationships=("LINKS",))
    )

    dsl_query_5 = (
        Query.projected_by(labels=("Page",), relationships=("LINKS",))
        .rank(algorithm=AlgorithmType.PageRank)
        .using(graph_connection)
        .write("test_property")
    )

    dsl_query_6 = (
        Query.write("test_property")
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .rank(algorithm=AlgorithmType.PageRank)
        .using(graph_connection)
    )

    assert (
        str(dsl_query_1)
        == str(dsl_query_2)
        == str(dsl_query_3)
        == str(dsl_query_4)
        == str(dsl_query_5)
        == str(dsl_query_6)
    )
