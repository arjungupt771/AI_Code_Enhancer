from pathlib import Path

from .base import Analyzer


class AnalyzerRegistry:
    def __init__(self, analyzers: list[Analyzer] | None = None):
        self._analyzers = analyzers or []

    def register(self, analyzer: Analyzer) -> None:
        self._analyzers.append(analyzer)

    def for_file(self, file_path: Path) -> list[Analyzer]:
        return [
            analyzer
            for analyzer in self._analyzers
            if analyzer.supports(file_path)
        ]

    def all(self) -> list[Analyzer]:
        return list(self._analyzers)