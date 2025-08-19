from __future__ import annotations

from typing import Any, Dict, List

from .cli_runner import CLIRunner


class ProjectsService:
    """Service for listing projects via CLI subprocess."""

    def __init__(self, runner: CLIRunner) -> None:
        self.runner = runner

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = self.runner.run_cli_json(["projects", "list", "--format", "json"]) or []
        if not isinstance(projects, list):
            return []
        return projects


