import json
import subprocess
import tempfile
from pathlib import Path

from .base import Analyzer
from .models import StaticFinding


class JavaScriptAnalyzer(Analyzer):
    name = "javascript"

    SUPPORTED_EXTENSIONS = {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
    }

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def analyze(
        self,
        file_path: Path,
        source_code: str,
    ) -> list[StaticFinding]:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / file_path.name
            temp_file.write_text(source_code, encoding="utf-8")

            result = subprocess.run(
                [
                    "npx",
                    "eslint",
                    str(temp_file),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        if not result.stdout.strip():
            return []

        try:
            reports = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        findings: list[StaticFinding] = []

        for report in reports:
            for message in report.get("messages", []):
                severity = message.get("severity", 1)

                findings.append(
                    StaticFinding(
                        tool="eslint",
                        rule_id=message.get("ruleId"),
                        message=message.get(
                            "message",
                            "ESLint finding",
                        ),
                        severity=(
                            "error"
                            if severity == 2
                            else "warning"
                        ),
                        category="style",
                        file_path=str(file_path),
                        line=max(message.get("line", 1), 1),
                        column=message.get("column"),
                        end_line=message.get("endLine"),
                        end_column=message.get("endColumn"),
                        code=message.get("ruleId"),
                    )
                )

        return findings