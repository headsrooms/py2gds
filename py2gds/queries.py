from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable, List

from py2gds.query import Query
from py2gds.utils import to_json_without_quotes, match_clause


@dataclass(frozen=True)
class Node:
    label: str
    properties: Optional[Dict[str, Any]] = None
    reference: Optional[str] = None

    def __str__(self):
        properties = to_json_without_quotes(self.properties) if self.properties else ""
        return f"({self.reference or ''}:{self.label} {properties})"


@dataclass(frozen=True)
class Relationship:
    from_node: Node
    type: str
    properties: Dict[str, Any]
    to_node: Node

    def __str__(self):
        return (
            f"({self.from_node.reference})-[:{self.type} "
            f"{to_json_without_quotes(self.properties)}]->({self.to_node.reference})"
        )


@dataclass(frozen=True)
class CreateNode(Query):
    node: Node

    @property
    def cypher(self) -> str:
        return f"""CREATE
        (:{self.node.label} {to_json_without_quotes(self.node.properties)})"""


@dataclass(frozen=True)
class CreateNodes(Query):
    nodes: Iterable[Node]
    relationships: Optional[Iterable[Relationship]]

    @property
    def cypher(self) -> str:
        nodes_composition = ",\n".join((str(node) for node in self.nodes))
        relationships_composition = (
            ",\n".join((str(relationship) for relationship in self.relationships))
            if self.relationships
            else ""
        )
        nodes_and_relationships = ",\n".join(
            [nodes_composition, relationships_composition]
        )
        return f"""CREATE
        {nodes_and_relationships};
        """


@dataclass(frozen=True)
class MatchNode(Query):
    node: Node

    @property
    def cypher(self) -> str:
        return f"""{match_clause(self.node.reference, self.node.label, self.node.properties)}
        RETURN {self.node.reference}"""


@dataclass(frozen=True)
class DeleteNode(Query):
    node: Node
    force: bool = False

    @property
    def cypher(self) -> str:
        delete_verb = "DETACH DELETE" if self.force else "DELETE"

        return f"""{match_clause(self.node.reference, self.node.label, self.node.properties)}
        {delete_verb} {self.node.reference}"""


@dataclass(frozen=True)
class CreateRelationShip(Query):
    relationship: Relationship

    @property
    def cypher(self) -> str:
        return (
            f"MATCH {str(self.relationship.from_node)}, {str(self.relationship.to_node)} \n"
            f"CREATE ({self.relationship.from_node.reference})"
            f"-[r:{self.relationship.name} {to_json_without_quotes(self.relationship.properties)}]->"
            f"({self.relationship.to_node.reference}) \n"
            f"RETURN type(r)"
        )


@dataclass(frozen=True)
class DeleteRelationship(Query):
    relationship: Relationship

    @property
    def cypher(self) -> str:
        return (
            f"MATCH {str(self.relationship.from_node)}"
            f"-[r:{self.relationship.name}]->{str(self.relationship.to_node)}"
            f" DELETE r"
        )


@dataclass(frozen=True)
class CheckProperty(Query):
    label: str
    property_name: str

    @property
    def cypher(self) -> str:
        return f"""MATCH (n:{self.label})
        WHERE EXISTS (n.{self.property_name})
        RETURN n LIMIT 1
        """

    def run(self, log: bool = True) -> bool:
        results = super().run(log)
        return len(results.data()) == 0


@dataclass(frozen=True)
class RemoveProperty(Query):
    name: str

    @property
    def cypher(self) -> str:
        return f"""MATCH (n)
        REMOVE n.{self.name}"""


@dataclass(frozen=True)
class CheckLabel(Query):
    label: str

    @property
    def cypher(self) -> str:
        return f"MATCH (n:{self.label}) WITH count(n)>0 as exists RETURN exists"

    def run(self, log: bool = True) -> bool:
        results = super().run(log)
        return results.data()[0]["exists"]


@dataclass(frozen=True)
class CreateIndex(Query):
    label: str
    properties: List[str]
    index_name: str

    @property
    def cypher(self) -> str:
        properties_part = ", ".join([f"n.{property}" for property in self.properties])

        return f"""CREATE INDEX {self.index_name or f"{self.label}_index"} FOR (n:{self.label}) 
        ON ({properties_part})"""


@dataclass(frozen=True)
class DropIndex(Query):
    index_name: str

    @property
    def cypher(self) -> str:
        return f"""DROP INDEX {self.index_name}"""
