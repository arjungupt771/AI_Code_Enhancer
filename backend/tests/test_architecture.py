from pathlib import Path

from backend.architecture import (
    ArchitectureAnalyzer,
)


def test_python_import_graph():
    analyzer = ArchitectureAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("backend/main.py"),
                "from backend.services.llm import review_code",
            ),
            (
                Path("backend/services/llm.py"),
                "from backend.schemas import ReviewResponse",
            ),
            (
                Path("backend/schemas.py"),
                "from pydantic import BaseModel",
            ),
        ]
    )

    assert result.total_nodes == 3
    assert result.total_edges == 2

    assert any(
        edge.source == "backend/main.py"
        and edge.target
        == "backend/services/llm.py"
        for edge in result.edges
    )


def test_javascript_relative_imports():
    analyzer = ArchitectureAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("src/App.js"),
                'import Header from "./components/Header";',
            ),
            (
                Path("src/components/Header.js"),
                "export default function Header() {}",
            ),
        ]
    )

    assert result.total_nodes == 2
    assert result.total_edges == 1

    edge = result.edges[0]

    assert edge.source == "src/App.js"
    assert (
        edge.target
        == "src/components/Header.js"
    )


def test_external_dependencies_are_not_graph_edges():
    analyzer = ArchitectureAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("src/App.js"),
                """
import React from "react";
import axios from "axios";
""",
            ),
        ]
    )

    assert result.total_nodes == 1
    assert result.total_edges == 0


def test_duplicate_edges_are_removed():
    analyzer = ArchitectureAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("src/App.js"),
                """
import Header from "./Header";
import HeaderAgain from "./Header";
""",
            ),
            (
                Path("src/Header.js"),
                "export default function Header() {}",
            ),
        ]
    )

    assert result.total_edges == 1


def test_cycles_are_detected():
    analyzer = ArchitectureAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("a.py"),
                "from b import value",
            ),
            (
                Path("b.py"),
                "from a import value",
            ),
        ]
    )

    assert result.cycle_count == 1