from py2gds.connection import Connection
from py2gds.queries import MatchNode


def test_create_node(graph_connection: Connection, home_page):
    assert MatchNode(graph_connection, home_page).run()
