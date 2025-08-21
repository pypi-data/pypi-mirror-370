from __future__ import annotations

from typing import List, Dict, Any, Optional
import json

from textual.widgets import DataTable, Static
from rich.table import Table

from .jobs_service import JobsService
from .artifacts_service import ArtifactsService
from ..utils.colors import EARTH_TONES


class JobsView:
	"""Encapsulates the jobs table UI logic."""

	def __init__(self, table: DataTable, jobs_service: JobsService) -> None:
		self.table = table
		self.jobs_service = jobs_service
		self.jobs: List[Dict[str, Any]] = []
		self.limit = 50
		self.offset = 0
		self._columns_initialized: bool = False

	def _ensure_columns(self) -> None:
		if not self._columns_initialized:
			# Keep in sync with app initialization
			try:
				self.table.add_columns("Job ID", "Tool", "Status", "Result")
			except Exception:
				# Headless / test mode where no active Textual app is present
				pass
			self._columns_initialized = True

	def _safe_add_row(self, cells: List[str]) -> None:
		try:
			self.table.add_row(*cells)
		except Exception:
			# Headless test mode: ignore UI errors
			pass

	def reset(self) -> None:
		self.offset = 0
		self.table.clear()
		self.jobs = []

	def load_initial(self, project_id: Optional[str]) -> List[Dict[str, Any]]:
		self.reset()
		self._ensure_columns()
		self.jobs = self.jobs_service.list_jobs(project_id, self.limit, self.offset)
		for job in self.jobs:
			self._safe_add_row(JobsService.format_row(job))
		return self.jobs

	def load_more(self, project_id: Optional[str]) -> List[Dict[str, Any]]:
		self.offset += self.limit
		self._ensure_columns()
		new_jobs = self.jobs_service.list_jobs(project_id, self.limit, self.offset)
		self.jobs.extend(new_jobs)
		for job in new_jobs:
			self._safe_add_row(JobsService.format_row(job))
		return new_jobs

	def get_selected_job(self, row_index: int) -> Optional[Dict[str, Any]]:
		if 0 <= row_index < len(self.jobs):
			return self.jobs[row_index]
		return None


class DetailsView:
	"""Encapsulates details panel rendering for summary, params, artifacts."""

	def __init__(self, summary: Static, params: Static, artifacts: Static, artifacts_service: ArtifactsService) -> None:
		self.summary = summary
		self.params = params
		self.artifacts = artifacts
		self.artifacts_service = artifacts_service

	def render_summary(self, job: Dict[str, Any]) -> None:
		lines: List[str] = []
		lines.append(f"[b]Job ID:[/b] {job.get('job_id') or job.get('id')}")
		lines.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
		lines.append(f"[b]Status:[/b] {job.get('status')}")
		title = job.get('job_title') or job.get('title')
		if title:
			lines.append(f"[b]Title:[/b] {title}")
		project = job.get('project_id')
		if project:
			lines.append(f"[b]Project:[/b] {project}")
		tool = (job.get('tool_name') or job.get('job_type') or '').lower()
		if tool in {"esmfold", "alphafold"}:
			lines.append("[b]Protein:[/b] structure prediction task")
		if tool in {"diffdock", "reinvent", "admetlab3"}:
			lines.append("[b]Compound:[/b] molecular/docking/design task")
		status_l = (job.get('status') or '').lower()
		if status_l in {"completed", "success"}:
			lines.append("[dim]Hint: press 'o' to open available artifacts externally[/dim]")
		self.summary.update("\n".join(lines))

	def render_params(self, job: Dict[str, Any]) -> None:
		params_obj = job.get('parameters') or job.get('request_params') or {}
		try:
			params_text = json.dumps(params_obj, indent=2) if params_obj else "No parameters"  # type: ignore[name-defined]
		except Exception:
			params_text = str(params_obj)
		self.params.update(params_text)

	def render_artifacts(self, job: Dict[str, Any]) -> None:
		job_id = str(job.get('job_id') or job.get('id') or '').strip()
		if not job_id:
			self.artifacts.update("Invalid job id")
			return
		try:
			table = self.artifacts_service.list_artifacts_table(job_id)
			self.artifacts.update(table)
		except Exception as e:
			self.artifacts.update(f"[red]Artifacts list failed: {e}[/red]")


