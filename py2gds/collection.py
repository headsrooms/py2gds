from dataclasses import dataclass
from typing import List, Tuple, Dict

from py2gds.connection import Connection
from py2gds.exceptions import ProjectionNotFound
from py2gds.projection import TaggedProjection, Projection


@dataclass(frozen=True)
class Collection:
    projections: List[TaggedProjection]

    @classmethod
    def create_from_projections_parameters(
        cls, connection: Connection, projections_parameters: Tuple[Dict[str, List[str]]]
    ):
        projections = [
            projection
            for projection_parameters in projections_parameters
            for projection in TaggedProjection.consolidate(
                connection, **projection_parameters
            )
        ]
        return Collection(projections)

    def get_projection_by_tag(self, tag: str) -> Projection:
        for projection in self.projections:
            if tag in projection.tags:
                return projection
        raise ProjectionNotFound(f"Projection with tag {tag} not found")

    def create(self, log: bool = True):
        for projection in self.projections:
            if not projection.exists(log):
                projection.create(log)
