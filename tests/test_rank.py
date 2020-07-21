from py2gds.algorithms.rank import (
    StreamPageRank,
    StreamArticleRank,
    WritePageRank,
    WriteArticleRank,
)
from py2gds.algorithms.rank_configuration import RankConfiguration
from py2gds.connection import Connection
from py2gds.projection import Projection
from py2gds.queries import RemoveProperty


def test_stream_pagerank(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    results = StreamPageRank(
        graph_connection, pages_and_links_projection, RankConfiguration()
    ).run()
    assert results


def test_write_pagerank(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    results = WritePageRank(
        graph_connection,
        pages_and_links_projection,
        RankConfiguration(write_property="test_1"),
    ).run()
    assert results
    RemoveProperty(graph_connection, "test_1").run()


def test_stream_articlerank(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    results = StreamArticleRank(
        graph_connection, pages_and_links_projection, RankConfiguration()
    ).run()
    assert results


def test_write_articlerank(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    results = WriteArticleRank(
        graph_connection,
        pages_and_links_projection,
        RankConfiguration(write_property="test_2"),
    ).run()
    assert results
    RemoveProperty(graph_connection, "test_2").run()
