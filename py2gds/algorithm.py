from abc import ABC, abstractmethod
from enum import Enum

from py2gds.query import Query


class AlgorithmType(str, Enum):
    PageRank = "pagerank"
    ArticleRank = "articlerank"


class AlgorithmOperation(str, Enum):
    stream = "stream"
    write = "write"


class Algorithm(Query):
    @property
    @abstractmethod
    def function_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def match_lines(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def call_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def yield_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def with_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def additional_operation(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def filter_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def return_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def order_line(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def limit_line(self) -> str:
        raise NotImplementedError

    @property
    def cypher(self) -> str:
        cypher = f"""{self.match_lines}
        {self.call_line}
        {self.yield_line}
        {self.with_line}
        {self.additional_operation}
        {self.filter_line}
        {self.return_line}
        {self.order_line}
        {self.limit_line}
        """

        return self._clean(cypher)

    @staticmethod
    def _clean(cypher):
        non_empty_lines = [
            stripped_line
            for line in cypher.split("\n")
            if (stripped_line := line.strip()) and len(stripped_line)
        ]

        return "\n".join(non_empty_lines)


class AlgorithmConfiguration(ABC):
    @property
    def match_lines(self):
        raise NotImplementedError

    @property
    def source_nodes(self):
        raise NotImplementedError
