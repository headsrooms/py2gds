from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional, Dict, List

from py2neo import Graph


class Connection(ABC):
    def execute(self, query: str) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class GraphConnection(Connection):
    graph: Graph

    @classmethod
    def to_py2neo(
        cls,
        uri: Optional[str] = None,
        name: Optional[str] = None,
        **settings: Dict[str, Any],
    ) -> "GraphConnection":
        return cls(Graph(uri, name, **settings))

    def execute(self, query: str) -> List[Dict[str, Any]]:
        return self.graph.run(query).data()
