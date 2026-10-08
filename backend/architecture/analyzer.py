"""Static repository architecture graph analysis."""

import ast
import re
from pathlib import Path

from backend.architecture.models import (
    ArchitectureAnalysis,
    ArchitectureEdge,
    ArchitectureNode,
)


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


class ArchitectureAnalyzer:
    """Build an architecture graph from repository source files."""

    def analyze(
        self,
        files: list[tuple[Path, str]],
    ) -> ArchitectureAnalysis:
        normalized_files = {
            path.as_posix(): content
            for path, content in files
            if path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        }

        nodes = self._build_nodes(
            normalized_files
        )

        file_paths = set(
            normalized_files
        )

        edges: list[ArchitectureEdge] = []

        for path, content in normalized_files.items():
            imports = self._extract_imports(
                path,
                content,
            )

            for imported in imports:
                target = self._resolve_import(
                    path,
                    imported,
                    file_paths,
                )

                if target is None:
                    continue

                edges.append(
                    ArchitectureEdge(
                        source=path,
                        target=target,
                        edge_type="import",
                    )
                )

        edges = self._deduplicate_edges(
            edges
        )

        cycles = self._find_cycles(
            normalized_files.keys(),
            edges,
        )

        return ArchitectureAnalysis(
            nodes=nodes,
            edges=edges,
            cycles=cycles,
        )

    @staticmethod
    def _build_nodes(
        files: dict[str, str],
    ) -> list[ArchitectureNode]:
        nodes = []

        for path in sorted(files):
            nodes.append(
                ArchitectureNode(
                    id=path,
                    label=Path(path).name,
                    node_type="file",
                    path=path,
                )
            )

        return nodes

    def _extract_imports(
        self,
        path: str,
        content: str,
    ) -> list[str]:
        suffix = Path(path).suffix.lower()

        if suffix == ".py":
            return self._extract_python_imports(
                content
            )

        if suffix in {
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
        }:
            return self._extract_javascript_imports(
                content
            )

        return []

    @staticmethod
    def _extract_python_imports(
        content: str,
    ) -> list[str]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        imports: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.append(
                        node.module
                    )

        return imports

    @staticmethod
    def _extract_javascript_imports(
        content: str,
    ) -> list[str]:
        imports: list[str] = []

        import_pattern = re.compile(
            r"""
            import\s+(?:.+?\s+from\s+)?["']([^"']+)["']
            |
            require\(\s*["']([^"']+)["']\s*\)
            |
            import\(\s*["']([^"']+)["']\s*\)
            """,
            re.VERBOSE,
        )

        for match in import_pattern.finditer(
            content
        ):
            imported = next(
                (
                    value
                    for value in match.groups()
                    if value
                ),
                None,
            )

            if imported:
                imports.append(imported)

        return imports

    @staticmethod
    def _resolve_import(
        source_path: str,
        imported: str,
        file_paths: set[str],
    ) -> str | None:
        """Resolve an import to a repository file."""

        source = Path(source_path)

        # JavaScript/TypeScript relative imports.
        if imported.startswith("."):
            base = (
                source.parent / imported
            )

            candidates = [
                base,
                *(
                    base.with_suffix(ext)
                    for ext in SUPPORTED_EXTENSIONS
                ),
            ]

            candidates.extend(
                [
                    base / "index.py",
                    base / "index.js",
                    base / "index.jsx",
                    base / "index.ts",
                    base / "index.tsx",
                ]
            )

            for candidate in candidates:
                normalized = (
                    candidate.as_posix()
                )

                if normalized in file_paths:
                    return normalized

            return None

        # Python repository imports.
        imported_path = (
            imported.replace(".", "/")
            + ".py"
        )

        if imported_path in file_paths:
            return imported_path

        package_init = (
            imported.replace(".", "/")
            + "/__init__.py"
        )

        if package_init in file_paths:
            return package_init

        return None

    @staticmethod
    def _deduplicate_edges(
        edges: list[ArchitectureEdge],
    ) -> list[ArchitectureEdge]:
        seen: set[
            tuple[str, str, str]
        ] = set()

        unique: list[
            ArchitectureEdge
        ] = []

        for edge in edges:
            key = (
                edge.source,
                edge.target,
                edge.edge_type,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(edge)

        return unique

    @staticmethod
    def _find_cycles(
        file_paths,
        edges: list[ArchitectureEdge],
    ) -> list[list[str]]:
        graph: dict[
            str,
            list[str],
        ] = {
            path: []
            for path in file_paths
        }

        for edge in edges:
            graph.setdefault(
                edge.source,
                [],
            ).append(edge.target)

        cycles: list[list[str]] = []
        seen_cycles: set[
            tuple[str, ...]
        ] = set()

        def canonical_cycle(
            cycle: list[str],
        ) -> tuple[str, ...]:
            rotations = [
                tuple(
                    cycle[index:]
                    + cycle[:index]
                )
                for index in range(
                    len(cycle)
                )
            ]

            return min(rotations)

        def visit(
            node: str,
            path: list[str],
            active: set[str],
        ) -> None:
            if node in active:
                start = path.index(node)
                cycle = path[start:]

                key = canonical_cycle(
                    cycle
                )

                if key not in seen_cycles:
                    seen_cycles.add(key)
                    cycles.append(
                        list(key)
                    )

                return

            active.add(node)
            path.append(node)

            for neighbor in graph.get(
                node,
                [],
            ):
                visit(
                    neighbor,
                    path,
                    active,
                )

            path.pop()
            active.remove(node)

        for node in graph:
            visit(
                node,
                [],
                set(),
            )

        return cycles