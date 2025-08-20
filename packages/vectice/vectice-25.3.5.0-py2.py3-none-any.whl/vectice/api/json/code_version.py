from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class GitVersion:
    repositoryName: str
    branchName: str
    commitHash: str
    isDirty: bool
    uri: str
    commitComment: str | None = None
    commitAuthorName: str | None = None
    commitAuthorEmail: str | None = None
    entrypoint: str | None = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DatabricksVersion:
    url_notebook: str
    relative_path: str
    timestamp: datetime

    def asdict(self) -> dict[str, Any]:
        return {
            "urlNotebook": self.url_notebook,
            "relativePath": self.relative_path,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CodeVersion:
    git_version: GitVersion | None = None
    databricks_version: DatabricksVersion | None = None

    def asdict(self) -> dict[str, Any]:
        return {
            "gitVersion": self.git_version.asdict() if self.git_version else None,
            "databricksVersion": self.databricks_version.asdict() if self.databricks_version else None,
        }
