from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

from py2gds.algorithms.algorithm import AlgorithmConfiguration
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
