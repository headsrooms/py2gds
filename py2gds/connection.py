from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List

from neo4j import Neo4jDriver, GraphDatabase


class Connection(ABC):
    def execute(self, query: str) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Neo4JDriverConnection(Connection):
    driver: Neo4jDriver

    @classmethod
    def create(cls, uri: str, user: str, password: str) -> "Neo4JDriverConnection":
        return cls(GraphDatabase.driver(uri, auth=(user, password)))

    def execute(self, query: str) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            return session.run(query).data()
