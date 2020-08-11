import os

import pytest
from configclasses import configclass

from py2gds.connection import Neo4JDriverConnection, Connection
from py2gds.projection import ProjectionIdentity, NativeProjection
from py2gds.queries import (
    CreateNode,
    DeleteNode,
    CreateNodes,
    Node,
    Relationship,
    DeleteRelationships,
    DeleteNodes,
)


@configclass
class Neo4j:
    host: str
    port: str
    scheme: str
    password: str


@configclass
class AppConfig:
    neo4j: Neo4j


@pytest.fixture(scope="session")
def app_config():
    env_path = os.getenv("ENV_PATH", "tests/.env")
    return AppConfig.from_path(env_path)


@pytest.fixture(scope="session")
def graph_connection(app_config) -> Connection:
    return Neo4JDriverConnection.create(
        uri=f"{app_config.neo4j.scheme}://{app_config.neo4j.host}:{app_config.neo4j.port}",
        user="neo4j",
        password=app_config.neo4j.password,
    )


@pytest.fixture
def home_page(app_config, graph_connection: Connection):
    new_home = Node("Page", {"name": "New Home"})
    CreateNode(graph_connection, new_home).run()

    yield new_home

    DeleteNode(graph_connection, new_home).run()


@pytest.fixture(scope="session")
def pages_and_links(app_config, graph_connection: Connection):
    home = Node("Page", {"name": "Home"}, "home")
    about = Node("Page", {"name": "About"}, "about")
    product = Node("Page", {"name": "Product"}, "product")
    links = Node("Page", {"name": "Links"}, "links")
    site_a = Node("Page", {"name": "Site A"}, "a")
    site_b = Node("Page", {"name": "Site B"}, "b")
    site_c = Node("Page", {"name": "Site C"}, "c")
    site_d = Node("Page", {"name": "Site D"}, "d")
    nodes = [home, about, product, links, site_a, site_b, site_c, site_d]
    relationships = [
        Relationship(home, "LINKS", {"weight": 0.2}, about),
        Relationship(home, "LINKS", {"weight": 0.2}, links),
        Relationship(home, "LINKS", {"weight": 0.6}, product),
        Relationship(about, "LINKS", {"weight": 1.0}, home),
        Relationship(product, "LINKS", {"weight": 1.0}, home),
        Relationship(site_a, "LINKS", {"weight": 1.0}, home),
        Relationship(site_b, "LINKS", {"weight": 1.0}, home),
        Relationship(site_c, "LINKS", {"weight": 1.0}, home),
        Relationship(site_d, "LINKS", {"weight": 1.0}, home),
        Relationship(links, "LINKS", {"weight": 0.8}, home),
        Relationship(links, "LINKS", {"weight": 0.05}, site_a),
        Relationship(links, "LINKS", {"weight": 0.05}, site_b),
        Relationship(links, "LINKS", {"weight": 0.05}, site_c),
        Relationship(links, "LINKS", {"weight": 0.05}, site_d),
    ]
    CreateNodes(graph_connection, nodes, relationships).run()

    yield

    DeleteRelationships(graph_connection, relationships).run()
    DeleteNodes(graph_connection, nodes).run()


@pytest.fixture(scope="session")
def pages_and_links_projection(graph_connection: Connection, pages_and_links):
    projection = NativeProjection(
        graph_connection, ProjectionIdentity(labels=("Page",), relationships=("LINKS",))
    )
    if not projection.exists():
        projection.create()
    yield projection

    projection.delete()
