import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from py2gds.connection import Connection


@dataclass(frozen=True)
class Query:
    connection: Connection

    @property
    @abstractmethod
    def cypher(self) -> str:
        raise NotImplementedError

    def run(self, log: bool = True) -> Any:
        if log:
            logging.info(f"Running query:\n {self.cypher}")
        return self.connection.execute(self.cypher)
