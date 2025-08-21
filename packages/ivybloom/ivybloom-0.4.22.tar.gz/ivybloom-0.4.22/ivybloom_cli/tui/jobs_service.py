from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cli_runner import CLIRunner
from .debug_logger import DebugLogger


class JobsService:
	"""Service to fetch and normalize job data via the CLI."""

	def __init__(self, runner: CLIRunner, logger: DebugLogger | None = None) -> None:
		self.runner = runner
		self._logger = logger or DebugLogger(False, prefix="JOBS")

	def list_jobs(self, project_id: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
		# Always request deterministic paging and include project filter when present
		args: List[str] = [
			"jobs", "list", "--format", "json",
			"--limit", str(limit),
			"--offset", str(offset),
		]
		if project_id:
			args += ["--project-id", str(project_id)]
		self._logger.debug(f"list_jobs: project_id={project_id} limit={limit} offset={offset}")
		jobs = self.runner.run_cli_json(args) or []
		if not isinstance(jobs, list):
			return []
		return jobs

	@staticmethod
	def format_row(job: Dict[str, Any]) -> List[str]:
		return [
			str(job.get("job_id") or job.get("id") or ""),
			str(job.get("tool_name") or job.get("job_type") or ""),
			str(job.get("status", "")),
			str(job.get("result") or job.get("job_title") or job.get("title") or ""),
		]


