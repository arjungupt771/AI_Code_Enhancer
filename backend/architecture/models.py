"""Models for repository architecture analysis."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArchitectureNode:
    """A node in the repository architecture graph."""

    id: str
    label: str
    node_type: str
    path: str | None = None


@dataclass(frozen=True)
class ArchitectureEdge:
    """A directed relationship between architecture nodes."""

    source: str
    target: str
    edge_type: str


@dataclass
class ArchitectureAnalysis:
    """Repository architecture graph."""

    nodes: list[ArchitectureNode] = field(
        default_factory=list
    )
    edges: list[ArchitectureEdge] = field(
        default_factory=list
    )
    cycles: list[list[str]] = field(
        default_factory=list
    )

    @property
    def total_nodes(self) -> int:
        return len(self.nodes)

    @property
    def total_edges(self) -> int:
        return len(self.edges)

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)