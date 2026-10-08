from backend.schemas import (
    ArchitectureEdgeResponse,
    ArchitectureNodeResponse,
    ArchitectureSummary,
)


def test_architecture_summary_schema():
    summary = ArchitectureSummary(
        nodes=[
            ArchitectureNodeResponse(
                id="src/App.js",
                label="App.js",
                node_type="file",
                path="src/App.js",
            )
        ],
        edges=[
            ArchitectureEdgeResponse(
                source="src/App.js",
                target="src/Header.js",
                edge_type="import",
            )
        ],
        cycles=[],
        total_nodes=1,
        total_edges=1,
        cycle_count=0,
    )

    assert summary.total_nodes == 1
    assert summary.total_edges == 1
    assert summary.cycle_count == 0
    assert summary.nodes[0].path == "src/App.js"
    assert summary.edges[0].target == "src/Header.js"


def test_architecture_summary_defaults():
    summary = ArchitectureSummary(
        total_nodes=0,
        total_edges=0,
        cycle_count=0,
    )

    assert summary.nodes == []
    assert summary.edges == []
    assert summary.cycles == []