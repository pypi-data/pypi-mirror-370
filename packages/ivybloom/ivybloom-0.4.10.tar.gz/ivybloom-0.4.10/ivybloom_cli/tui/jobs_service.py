from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cli_runner import CLIRunner


class JobsService:
	"""Service to fetch and normalize job data via the CLI."""

	def __init__(self, runner: CLIRunner) -> None:
		self.runner = runner

	def list_jobs(self, project_id: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
		args: List[str] = ["jobs", "list", "--format", "json", "--limit", str(limit), "--offset", str(offset)]
		if project_id:
			args += ["--project-id", str(project_id)]
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


