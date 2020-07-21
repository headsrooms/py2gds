from abc import ABC
from dataclasses import dataclass, field
from hashlib import blake2b
from itertools import product
from typing import Union, List, Tuple, Dict

from py2gds.connection import Connection
from py2gds.query import Query


@dataclass(frozen=True)
class ProjectionIdentity:
    labels: Union[Tuple[str, ...], str] = '"*"'
    relationships: Union[Tuple[str, ...], str] = '"*"'

    def __hash__(self):
        h = blake2b()
        identity = {
            "labels": tuple(sorted(set(self.labels))),
            "relationships": tuple(sorted(set(self.relationships))),
        }
        h.update(str(identity.values()).encode())
        return h.hexdigest()


@dataclass(frozen=True)
class Projection(ABC):
    connection: Connection
    identity: ProjectionIdentity

    @property
    def name(self):
        return self.identity.__hash__()

    @property
    def create_query(self) -> Query:
        raise NotImplementedError

    @property
    def exists_query(self) -> Query:
        return ExistsProjectionQuery(self.connection, self.name)

    @property
    def delete_query(self) -> Query:
        return DeleteProjectionQuery(self.connection, self.name)

    def create(self, log: bool = True):
        return self.create_query.run(log)

    def exists(self, log: bool = True):
        return self.exists_query.run(log)[0]["exists"]

    def delete(self, log: bool = True):
        return self.delete_query.run(log)


@dataclass(frozen=True)
class NativeProjection(Projection):
    @classmethod
    def consolidate(
        cls, connection: Connection, **projection_parameters: Dict[str, List[str]]
    ) -> List[Projection]:
        raise NotImplementedError

    @property
    def create_query(self) -> Query:
        return CreateProjectionQuery(
            self.connection,
            self.name,
            self.identity.labels,
            self.identity.relationships,
        )


@dataclass(frozen=True)
class TaggedProjection(NativeProjection):
    tags: List[str] = field(default_factory=list)

    @classmethod
    def consolidate(
        cls, connection: Connection, **projection_parameters: Dict[str, List[str]]
    ) -> List["TaggedProjection"]:
        if modifiers := projection_parameters.pop("modifiers", False):
            combinations = list(product(*modifiers.values()))
            formatters = [
                {k: v for k, v in zip(modifiers.keys(), combination)}
                for combination in list(combinations)
            ]

            projections_parameters = [
                {
                    k: tuple(map(lambda x: x.format(**formatter), v))
                    for k, v in projection_parameters.items()
                }
                for formatter in formatters
            ]
            return [
                TaggedProjection(connection, **projection_parameters)
                for projection_parameters in projections_parameters
            ]

        else:
            return [TaggedProjection(connection, **projection_parameters)]


@dataclass(frozen=True)
class CreateProjectionQuery(Query):
    name: str
    labels: Union[Tuple[str, ...], str] = '"*"'
    relationships: Union[Tuple[str, ...], str] = '"*"'

    @property
    def cypher(self) -> str:
        relationships = self.relationships
        if relationships != '"*"':
            relationships = ",".join(
                [
                    f"{relationship}:{{type:'{relationship}', orientation:'UNDIRECTED'}}"
                    for relationship in self.relationships
                ]
            )
            relationships = f"{{{relationships}}}"

        query = f"""CALL gds.graph.create(
        '{self.name}',
        {list(self.labels)},
        {relationships}
        )
        YIELD graphName, nodeCount, relationshipCount, createMillis;"""

        return query


@dataclass(frozen=True)
class ExistsProjectionQuery(Query):
    name: str

    @property
    def cypher(self) -> str:
        return f"CALL gds.graph.exists('{self.name}') YIELD exists;"


@dataclass(frozen=True)
class DeleteProjectionQuery(Query):
    name: str

    @property
    def cypher(self) -> str:
        return f"CALL gds.graph.drop('{self.name}')"
