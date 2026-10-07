from .models import StaticFinding


def _normalize_message(message: str) -> str:
    return " ".join(message.lower().split())


def finding_key(finding: StaticFinding) -> tuple:
    return (
        finding.file_path,
        finding.line,
        finding.rule_id,
        _normalize_message(finding.message),
    )


def deduplicate_findings(
    findings: list[StaticFinding],
) -> list[StaticFinding]:
    seen: set[tuple] = set()
    unique: list[StaticFinding] = []

    for finding in findings:
        key = finding_key(finding)

        if key in seen:
            continue

        seen.add(key)
        unique.append(finding)

    return unique