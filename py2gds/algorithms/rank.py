from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterable

from py2gds.algorithms.algorithm import AlgorithmOperation, Algorithm
from py2gds.algorithms.rank_configuration import RankConfiguration
from py2gds.exceptions import NeededPropertyNameNotSpecified
from py2gds.projection import Projection


@dataclass(frozen=True)
class Rank(Algorithm):
    projection: Projection
    configuration: RankConfiguration
    limit: int = 100
    labels_filter: Optional[Iterable[str]] = None
    _additional_filter: Optional[str] = None
    returned_properties: Optional[Iterable[str]] = None

    @property
    def additional_filter(self) -> str:
        return self._additional_filter

    @property
    @abstractmethod
    def function_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def operation(self) -> str:
        raise NotImplementedError

    @property
    def match_lines(self) -> str:
        return self.configuration.match_lines

    @property
    def call_line(self) -> str:
        return f"CALL {self.function_name}.{self.operation}('{self.projection.name}', {self.configuration})"

    @property
    def yield_line(self) -> str:
        return "YIELD nodeId, score"

    @property
    def with_line(self) -> str:
        return "WITH gds.util.asNode(nodeId) as node, score"

    @property
    def additional_operation(self) -> str:
        return ""

    @property
    def filter_line(self) -> str:
        if self.labels_filter or self.additional_filter:
            if not self.additional_filter:
                labels_filter = " AND ".join(
                    [f"node:{label}" for label in self.labels_filter]
                )
                filter_line = f"WHERE {labels_filter}"
            elif not self.labels_filter:
                filter_line = f"WHERE {self.additional_filter}"
            else:
                labels_filter = " AND ".join(
                    [f"node:{label}" for label in self.labels_filter]
                )
                filter_line = f"WHERE {labels_filter} AND {self.additional_filter}"
        else:
            filter_line = ""
        return filter_line

    @property
    def return_line(self) -> str:
        if self.returned_properties:
            node_properties = ", ".join(
                [
                    f"node.{returned_property} as {returned_property}"
                    for returned_property in self.returned_properties
                ]
            )
            return_line = f"RETURN {node_properties}, score"
        else:
            return_line = "RETURN node, score"
        return return_line

    @property
    def order_line(self) -> str:
        return "ORDER BY score DESC"

    @property
    def limit_line(self) -> str:
        return f"LIMIT {self.limit}" if self.limit else ""


@dataclass(frozen=True)
class PageRank(Rank):
    @property
    def function_name(self) -> str:
        return "gds.pageRank"


@dataclass(frozen=True)
class WriteRank(Rank):
    def run(self, log: bool = True) -> List[Dict[str, Any]]:
        if not self.configuration.write_property:
            raise NeededPropertyNameNotSpecified()
        return super().run(log)

    @property
    def with_line(self) -> str:
        return ""

    @property
    def additional_operation(self) -> str:
        return ""

    @property
    def filter_line(self) -> str:
        return ""

    @property
    def return_line(self) -> str:
        return ""

    @property
    def order_line(self) -> str:
        return ""

    @property
    def limit_line(self) -> str:
        return ""


@dataclass(frozen=True)
class StreamPageRank(PageRank):
    @property
    def operation(self) -> AlgorithmOperation:
        return AlgorithmOperation.stream


@dataclass(frozen=True)
class WritePageRank(PageRank, WriteRank):
    @property
    def operation(self) -> AlgorithmOperation:
        return AlgorithmOperation.write

    @property
    def yield_line(self) -> str:
        return "YIELD nodePropertiesWritten AS writtenProperties, ranIterations"

    @property
    def return_line(self) -> str:
        return "RETURN writtenProperties, ranIterations"


@dataclass(frozen=True)
class ArticleRank(Rank):
    @property
    def function_name(self) -> str:
        return "gds.alpha.articleRank"


@dataclass(frozen=True)
class StreamArticleRank(ArticleRank):
    @property
    def operation(self) -> AlgorithmOperation:
        return AlgorithmOperation.stream


@dataclass(frozen=True)
class WriteArticleRank(ArticleRank, WriteRank):
    @property
    def operation(self) -> AlgorithmOperation:
        return AlgorithmOperation.write

    @property
    def yield_line(self) -> str:
        return "YIELD nodes, iterations, createMillis, computeMillis, writeMillis, dampingFactor, writeProperty"

    @property
    def return_line(self) -> str:
        return "RETURN nodes, iterations, createMillis, computeMillis, writeMillis, dampingFactor, writeProperty"
