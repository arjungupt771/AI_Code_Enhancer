from dataclasses import dataclass
from pathlib import Path

from .base import Analyzer
from .models import StaticFinding


@dataclass
class HybridReviewResult:
    static_findings: list[StaticFinding]
    total_files_analyzed: int

    @property
    def total_findings(self) -> int:
        return len(self.static_findings)


class HybridAnalyzer:
    """
    Coordinates all deterministic analyzers.

    AI review is intentionally kept outside this class.
    This class is responsible only for static analysis.
    """

    def __init__(self, analyzers: list[Analyzer]):
        self.analyzers = analyzers

    def analyze_file(
        self,
        file_path: Path,
        source_code: str,
    ) -> list[StaticFinding]:
        findings: list[StaticFinding] = []

        for analyzer in self.analyzers:
            if not analyzer.supports(file_path):
                continue

            try:
                findings.extend(
                    analyzer.analyze(
                        file_path,
                        source_code,
                    )
                )
            except Exception as exc:
                findings.append(
                    StaticFinding(
                        tool=analyzer.name,
                        rule_id="ANALYZER_ERROR",
                        message=(
                            f"{analyzer.name} failed while analyzing "
                            f"{file_path.name}: {exc}"
                        ),
                        severity="warning",
                        category="analysis",
                        file_path=str(file_path),
                        line=1,
                    )
                )

        return findings

    def analyze_files(
        self,
        files: list[tuple[Path, str]],
    ) -> HybridReviewResult:
        all_findings: list[StaticFinding] = []

        for file_path, source_code in files:
            all_findings.extend(
                self.analyze_file(
                    file_path,
                    source_code,
                )
            )

        return HybridReviewResult(
            static_findings=all_findings,
            total_files_analyzed=len(files),
        )