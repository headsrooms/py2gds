from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterable, Tuple

from py2gds.algorithm import Algorithm, AlgorithmOperation, AlgorithmConfiguration
from py2gds.exceptions import NeededPropertyNameNotSpecified
from py2gds.projection import Projection
from py2gds.utils import match_clause


@dataclass(frozen=True)
class RankConfiguration(AlgorithmConfiguration):
    max_iterations: int = 20
    damping_factor: float = 0.80
    write_property: Optional[str] = None

    @property
    def match_lines(self):
        return ""

    @property
    def source_nodes(self) -> str:
        source_nodes = ""
        return f"[{source_nodes}]"

    def __str__(self):
        inner_lines = [
            f"maxIterations: {self.max_iterations}",
            f"dampingFactor: {self.damping_factor}",
        ]
        if self.write_property:
            inner_lines.append(f"writeProperty: '{self.write_property}'")
        inner_lines = ",\n".join(inner_lines)

        return f"""{{
            {inner_lines}
        }}"""


@dataclass(frozen=True)
class RankConfigurationWithFilter(RankConfiguration):
    filter_elements: Optional[List[Tuple[str, str, Dict[str, str]]]] = None

    @property
    def match_lines(self):
        return "".join(
            [
                match_clause(reference, label, filter)
                for reference, label, filter in self.filter_elements
            ]
        )

    @property
    def source_nodes_names(self) -> Optional[List[str]]:
        return [filter_element[0] for filter_element in self.filter_elements]

    @property
    def source_nodes(self) -> str:
        source_nodes = ", ".join(self.source_nodes_names)
        return f"[{source_nodes}]"

    def __str__(self):
        write_property_part = (
            f", writeProperty: '{self.write_property}'" if self.write_property else ""
        )

        inner_lines = ",\n".join(
            [
                f"maxIterations: {self.max_iterations}",
                f"dampingFactor: {self.damping_factor}",
                f"sourceNodes: {self.source_nodes}",
                f"{write_property_part}",
            ]
        )

        return f"""{{
            {inner_lines}
        }}"""


@dataclass(frozen=True)
class Rank(Algorithm):
    projection: Projection
    configuration: RankConfiguration
    limit: Optional[int] = None
    labels_filter: Optional[Iterable[str]] = None
    _additional_filter: Optional[str] = None
    returned_properties: Optional[Iterable[str]] = None
    sort_by_properties: Optional[Iterable[str]] = None
    sort_descending: bool = False
    skip: Optional[int] = None

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
        if self.sort_by_properties:
            node_properties = ", ".join(
                [f"{property}" for property in self.sort_by_properties]
            )
            descending_part = "DESC" if self.sort_descending else ""
            return f"ORDER BY {node_properties} {descending_part}"
        return ""

    @property
    def limit_line(self) -> str:
        return f"LIMIT {self.limit}" if self.limit else ""

    @property
    def skip_line(self) -> str:
        return f"SKIP {self.skip}" if self.skip else ""


@dataclass(frozen=True)
class PageRank(Rank):
    @property
    @abstractmethod
    def operation(self) -> str:
        raise NotImplementedError

    @property
    def function_name(self) -> str:
        return "gds.pageRank"


@dataclass(frozen=True)
class WriteRank(Rank):
    @property
    @abstractmethod
    def function_name(self) -> str:
        raise NotImplementedError

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
    @abstractmethod
    def operation(self) -> str:
        raise NotImplementedError

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
