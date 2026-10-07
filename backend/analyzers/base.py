from abc import ABC, abstractmethod
from pathlib import Path

from .models import StaticFinding


class Analyzer(ABC):
    name: str

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Return whether this analyzer can analyze the file."""
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        file_path: Path,
        source_code: str,
    ) -> list[StaticFinding]:
        """Analyze source code and return normalized findings."""
        raise NotImplementedError