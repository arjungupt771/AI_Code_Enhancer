import json
import subprocess
import tempfile
from pathlib import Path

from .base import Analyzer
from .models import StaticFinding


class PythonAnalyzer(Analyzer):
    name = "python"

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".py"

    def analyze(
        self,
        file_path: Path,
        source_code: str,
    ) -> list[StaticFinding]:
        findings: list[StaticFinding] = []

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / file_path.name
            temp_file.write_text(source_code, encoding="utf-8")

            findings.extend(
                self._run_ruff(
                    temp_file,
                    file_path,
                )
            )

            findings.extend(
                self._run_bandit(
                    temp_file,
                    file_path,
                )
            )

        return findings

    def _run_ruff(
        self,
        temp_file: Path,
        original_path: Path,
    ) -> list[StaticFinding]:
        result = subprocess.run(
            [
                "ruff",
                "check",
                str(temp_file),
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if not result.stdout.strip():
            return []

        try:
            issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        findings = []

        for issue in issues:
            location = issue.get("location", {})
            end_location = issue.get("end_location", {})

            findings.append(
                StaticFinding(
                    tool="ruff",
                    rule_id=issue.get("code"),
                    message=issue.get("message", "Ruff finding"),
                    severity=self._ruff_severity(issue.get("code")),
                    category=self._ruff_category(issue.get("code")),
                    file_path=str(original_path),
                    line=location.get("row", 1),
                    column=location.get("column"),
                    end_line=end_location.get("row"),
                    end_column=end_location.get("column"),
                    code=issue.get("code"),
                    suggestion=issue.get("fix", {}).get("message")
                    if issue.get("fix")
                    else None,
                )
            )

        return findings

    def _run_bandit(
        self,
        temp_file: Path,
        original_path: Path,
    ) -> list[StaticFinding]:
        result = subprocess.run(
            [
                "bandit",
                "-q",
                "-f",
                "json",
                str(temp_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if not result.stdout.strip():
            return []

        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        findings = []

        for issue in report.get("results", []):
            findings.append(
                StaticFinding(
                    tool="bandit",
                    rule_id=issue.get("test_id"),
                    message=issue.get("issue_text", "Bandit finding"),
                    severity=self._bandit_severity(
                        issue.get("issue_severity")
                    ),
                    category="security",
                    file_path=str(original_path),
                    line=issue.get("line_number", 1),
                    column=None,
                    code=issue.get("test_id"),
                )
            )

        return findings

    @staticmethod
    def _ruff_severity(code: str | None) -> str:
        if not code:
            return "warning"

        if code.startswith(("E", "F")):
            return "error"

        if code.startswith(("S", "B")):
            return "error"

        return "warning"

    @staticmethod
    def _ruff_category(code: str | None) -> str:
        if not code:
            return "style"

        if code.startswith("S"):
            return "security"

        if code.startswith("B"):
            return "bug"

        if code.startswith("PERF"):
            return "performance"

        if code.startswith(("E", "W")):
            return "style"

        if code.startswith("F"):
            return "bug"

        return "style"

    @staticmethod
    def _bandit_severity(severity: str | None) -> str:
        normalized = (severity or "").upper()

        if normalized == "HIGH":
            return "error"

        if normalized == "MEDIUM":
            return "error"

        if normalized == "LOW":
            return "warning"

        return "info"