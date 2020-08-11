from py2gds.algorithm import AlgorithmType
from py2gds.connection import Connection
from py2gds.dsl import Query
from py2gds.projection import Projection
from py2gds.rank import (
    WriteArticleRank,
    StreamArticleRank,
    StreamPageRank,
    WritePageRank,
    RankConfiguration,
)


def test_stream_articlerank(
    graph_connection: Connection, pages_and_links_projection: Projection
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
    graph_connection: Connection, pages_and_links_projection: Projection
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
    graph_connection: Connection, pages_and_links_projection: Projection
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
    graph_connection: Connection, pages_and_links_projection: Projection
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


def test_query_order(graph_connection: Connection):
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


def test_sort_by_score_ascending(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .order_by("score")
    )

    results = query.run()
    previous_score = None
    for result in results:
        if previous_score:
            assert result["score"] >= previous_score
        previous_score = result["score"]


def test_sort_by_score_descending(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .order_by("score", descending=True)
    )

    results = query.run()
    previous_score = None
    for result in results:
        if previous_score:
            assert result["score"] <= previous_score
        previous_score = result["score"]


def test_limit(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .order_by("score", descending=True)
        .limit(2)
    )

    results = query.run()
    assert len(results) == 2


def test_skip(
    graph_connection: Connection, pages_and_links_projection: Projection
):
    normal_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .order_by("score", descending=True)
        .limit(4)
    )

    skipped_query = (
        Query.using(graph_connection)
        .rank(algorithm=AlgorithmType.ArticleRank)
        .projected_by(labels=("Page",), relationships=("LINKS",))
        .order_by("score", descending=True)
        .skip(3)
        .limit(4)
    )

    normal_results = normal_query.run(log=True)
    skipped_results = skipped_query.run(log=True)
    assert normal_results[3]["score"] == skipped_results[0]["score"]