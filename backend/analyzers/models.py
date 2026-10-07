from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["error", "warning", "info"]
Source = Literal["static", "ai"]


class StaticFinding(BaseModel):
    source: Source = "static"
    tool: str
    rule_id: str | None = None
    message: str
    severity: Severity
    category: str
    file_path: str
    line: int = Field(ge=1)
    column: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    end_column: int | None = Field(default=None, ge=1)
    code: str | None = None
    suggestion: str | None = None