from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
import webbrowser
import subprocess
import json
import math

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Input, LoadingIndicator, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem
from rich.table import Table
from rich import box

from ..utils.colors import EARTH_TONES
from ..utils.config import Config
from ..utils.auth import AuthManager


class IvyBloomTUI(App):
	CSS = f"""
	Screen {{
		background: {EARTH_TONES['neutral_cream']};
	}}

	# Header / Footer use defaults for now

	.panel-title {{
		color: {EARTH_TONES['sage_dark']};
	}}

	.muted {{
		color: {EARTH_TONES['muted']};
	}}

	# DataTable coloring
	# Note: Textual's DataTable styling is limited via API; keep minimal
		
	.splash {{
		align: center middle;
		height: 100%;
	}}
	"""

	BINDINGS = [
		("r", "refresh", "Refresh"),
		("/", "open_palette", "Commands"),
		("f", "focus_filter", "Filter"),
		("o", "open_external", "Open Artifact"),
		("?", "toggle_help", "Help"),
		("tab", "focus_next", "Next"),
		("shift+tab", "focus_previous", "Prev"),
		("q", "quit", "Quit"),
	]

	def __init__(self, config: Config, auth_manager: AuthManager, initial_project_id: Optional[str] = None, show_header: bool = False, show_footer: bool = False) -> None:
		super().__init__()
		self.config = config
		self.auth_manager = auth_manager
		self.initial_project_id = initial_project_id
		self.show_header = show_header
		self.show_footer = show_footer

		self.jobs: List[Dict[str, Any]] = []
		self.selected_job: Optional[Dict[str, Any]] = None

		# Pagination / status
		self.jobs_offset: int = 0
		self.jobs_limit: int = 50
		self.refresh_interval_secs: int = 30
		self._connected: bool = False
		self._last_error: Optional[str] = None

		# UI refs
		self.cmd_input: Input | None = None
		self.status_bar: Static | None = None
		self.details_summary: Static | None = None
		self.details_params: Static | None = None
		self.details_artifacts: Static | None = None
		self.details_structure: Static | None = None
		self._structure_points: List[Tuple[float, float, float]] = []
		self._structure_angle: float = 0.0
		self._structure_timer = None

	def compose(self) -> ComposeResult:
		if self.show_header:
			yield Header()
		with Horizontal():
			with Vertical():
				yield Static("Jobs", classes="panel-title")
				self.jobs_table = DataTable(zebra_stripes=True)
				yield self.jobs_table
			with Vertical():
				yield Static("Details", classes="panel-title")
				self.details_summary = Static("Select a job to view details", classes="muted")
				self.details_params = Static("", classes="muted")
				self.details_artifacts = Static("", classes="muted")
				self.details_structure = Static("No structure loaded", classes="muted")
				with TabbedContent():
					with TabPane("Summary"):
						yield self.details_summary
					with TabPane("Parameters"):
						yield self.details_params
					with TabPane("Artifacts"):
						yield self.details_artifacts
					with TabPane("Structure"):
						yield self.details_structure
		# Bottom input + status bar
		self.cmd_input = Input(placeholder="Enter ivybloom args (e.g., jobs list --status running); '/' for palette; Enter to run")
		yield self.cmd_input
		self.status_bar = Static("", classes="muted")
		yield self.status_bar
		if self.show_footer:
			yield Footer()

	def on_mount(self) -> None:
		# Configure jobs table columns (dense)
		self.jobs_table.clear()
		self.jobs_table.add_columns("Job ID", "Tool", "Status", "Result")
		self.jobs_table.cursor_type = "row"
		self.jobs_table.focus()
		# Show splash and load
		self._splash_opened = False  # type: ignore[attr-defined]
		self._show_splash()
		self.call_later(self._load_jobs)
		# Auto refresh and connectivity
		try:
			self.set_interval(self.refresh_interval_secs, lambda: self.call_later(self._load_jobs))
			self.set_interval(10, self._probe_connectivity)
		except Exception:
			pass
		self._update_status_bar()

	# ------------------ Splash ------------------
	def _show_splash(self) -> None:
		try:
			if not getattr(self, "_splash_opened", False):  # type: ignore[attr-defined]
				self._splash_opened = True  # type: ignore[attr-defined]
				self.push_screen(SplashScreen("IvyBloom", "Starting up…"))
		except Exception:
			pass

	def _hide_splash(self) -> None:
		try:
			if getattr(self, "_splash_opened", False):  # type: ignore[attr-defined]
				self._splash_opened = False  # type: ignore[attr-defined]
				self.pop_screen()
		except Exception:
			pass

	# ------------------ Command Palette ------------------
	def action_open_palette(self) -> None:
		commands = [
			("list_tools", "Tools: List", "Show available tools in a table"),
			("tools_info", "Tools: Info", "Show detailed info for a tool"),
			("tools_schema", "Tools: Schema", "Show parameter schema for a tool"),
			("tools_completions", "Tools: Completions", "Show enum choices for a tool"),
			("jobs_list", "Jobs: List", "List jobs with optional filters"),
			("jobs_status", "Jobs: Status", "Show job status (optionally follow)"),
			("jobs_results", "Jobs: Results", "Fetch job results (JSON)"),
			("jobs_download", "Jobs: Download", "List/download job artifacts"),
			("jobs_cancel", "Jobs: Cancel", "Cancel a running job"),
			("projects_list", "Projects: List", "List projects"),
			("account_info", "Account: Info", "Show account info"),
			("run_tool", "Run: Tool", "Run a tool with key=value params"),
			("workflows_run", "Workflows: Run", "Run a workflow file"),
			("refresh", "Refresh", "Reload jobs"),
			("jobs_load_more", "Jobs: Load More", "Fetch next page (50)"),
			("focus_filter", "Focus Filter", "Jump to filter input"),
			("clear_filter", "Clear Filter", "Remove all filters"),
			("quick_status_running", "Filter: status=running", "Show running jobs"),
			("quick_status_completed", "Filter: status=completed", "Show completed jobs"),
			("open_external", "Open Artifact", "Open best artifact in browser"),
			("toggle_help", "Toggle Help", "Show/hide help panel"),
			("run_custom", "Run CLI: Custom", "Run arbitrary ivybloom args"),
			("artifacts_list", "Artifacts: List", "List artifacts for selected job"),
			("artifact_preview", "Artifacts: Preview", "Preview JSON/CSV for selected job"),
			("protein_view_ascii", "Protein: View ASCII", "Load and rotate ASCII protein (PDB)"),
			("protein_stop_ascii", "Protein: Stop ASCII", "Stop protein ASCII view"),
		]
		self.push_screen(CommandPalette(commands), self._on_palette_result)

	def _on_palette_result(self, result: Optional[str]) -> None:
		if not result:
			return
		if result == "list_tools":
			self.call_later(self._show_tools)
		elif result == "tools_info":
			self.push_screen(PromptScreen("Tool name (e.g., esmfold)"), lambda val: self._cmd_tools_info(val))
		elif result == "tools_schema":
			self.push_screen(PromptScreen("Tool name for schema"), lambda val: self._cmd_tools_schema(val))
		elif result == "tools_completions":
			self.push_screen(PromptScreen("Tool name for completions"), lambda tool: self._cmd_tools_completions(tool))
		elif result == "jobs_list":
			self.push_screen(PromptScreen("Extra filters (e.g. --status running --tool esmfold)", placeholder="optional"), lambda extra: self._cmd_jobs_list(extra))
		elif result == "jobs_status":
			self.push_screen(PromptScreen("Job ID (add --follow or --logs in next step)"), lambda job_id: self._cmd_jobs_status(job_id))
		elif result == "jobs_results":
			self.push_screen(PromptScreen("Job ID for results"), lambda job_id: self._cmd_jobs_results(job_id))
		elif result == "jobs_download":
			self.push_screen(PromptScreen("Job ID to download/list"), lambda job_id: self._cmd_jobs_download(job_id))
		elif result == "jobs_cancel":
			self.push_screen(PromptScreen("Job ID to cancel"), lambda job_id: self._cmd_jobs_cancel(job_id))
		elif result == "projects_list":
			self.call_later(self._cmd_projects_list)
		elif result == "account_info":
			self.call_later(self._cmd_account_info)
		elif result == "artifacts_list":
			self.call_later(self._cmd_artifacts_list)
		elif result == "artifact_preview":
			self.push_screen(PromptScreen("Artifact type or filename (optional)", placeholder="optional"), lambda sel: self._cmd_artifact_preview(sel))
		elif result == "protein_view_ascii":
			self._cmd_protein_view_ascii()
		elif result == "protein_stop_ascii":
			self._stop_protein_ascii()
		elif result == "run_tool":
			self.push_screen(PromptScreen("Tool name to run"), lambda tool: self._cmd_run_tool_start(tool))
		elif result == "workflows_run":
			self.push_screen(PromptScreen("Workflow file path"), lambda path: self._cmd_workflows_run_start(path))
		elif result == "run_custom":
			self.push_screen(PromptScreen("Custom args after 'ivybloom'", placeholder="e.g. jobs list --status running"), lambda extra: self._cmd_run_custom(extra))
		elif result == "refresh":
			self.action_refresh()
		elif result == "jobs_load_more":
			self._cmd_jobs_load_more()
		elif result == "focus_filter":
			self.action_focus_filter()
		elif result == "clear_filter":
			# No filters currently; noop
			pass
		elif result == "quick_status_running":
			# No filters currently; noop
			pass
		elif result == "quick_status_completed":
			# No filters currently; noop
			pass
		elif result == "open_external":
			self.action_open_external()
		elif result == "toggle_help":
			self.action_toggle_help()

	async def _show_tools(self) -> None:
		try:
			# Thin wrapper: call CLI and render JSON
			tools_json = self._run_cli_json(["tools", "list", "--format", "json"]) or []
			# tools_json may be a list of dicts or names
			table = Table(title="Available Tools", show_lines=False, show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}", box=box.SIMPLE_HEAVY)
			table.add_column("ID", style="cyan", no_wrap=True)
			table.add_column("Name", style="white")
			table.add_column("Description", style="white")
			if isinstance(tools_json, list):
				for item in tools_json:
					if isinstance(item, dict):
						table.add_row(
							str(item.get("id") or item.get("name") or ""),
							str(item.get("name") or item.get("id") or ""),
							str(item.get("description") or ""),
						)
					else:
						name_val = str(item)
						table.add_row(name_val, name_val, "")
			if self.details_summary:
				self.details_summary.update(table)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Failed to load tools: {e}[/red]")

	def _apply_filter(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		# Filters disabled for now; keep placeholder for future
		return jobs

	async def _load_jobs(self) -> None:
		self.jobs_offset = 0
		self.jobs_table.clear()
		try:
			# Thin wrapper: call CLI for jobs list
			args: List[str] = ["jobs", "list", "--format", "json", "--limit", str(self.jobs_limit), "--offset", str(self.jobs_offset)]
			if self.initial_project_id:
				args += ["--project-id", str(self.initial_project_id)]
			jobs = self._run_cli_json(args) or []
			if not isinstance(jobs, list):
				jobs = []
			self.jobs = jobs
			for job in self._apply_filter(jobs):
				self.jobs_table.add_row(
					str(job.get("job_id") or job.get("id") or ""),
					str(job.get("tool_name") or job.get("job_type") or ""),
					str(job.get("status", "")),
					str(job.get("job_title") or job.get("title") or ""),
				)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Failed to load jobs: {e}[/red]")
		finally:
			self._hide_splash()

	def _cmd_jobs_load_more(self) -> None:
		# Fetch next page and append
		try:
			self.jobs_offset += self.jobs_limit
			args: List[str] = ["jobs", "list", "--format", "json", "--limit", str(self.jobs_limit), "--offset", str(self.jobs_offset)]
			if self.initial_project_id:
				args += ["--project-id", str(self.initial_project_id)]
			new_jobs = self._run_cli_json(args) or []
			if not isinstance(new_jobs, list):
				new_jobs = []
			self.jobs.extend(new_jobs)
			for job in new_jobs:
				self.jobs_table.add_row(
					str(job.get("job_id") or job.get("id") or ""),
					str(job.get("tool_name") or job.get("job_type") or ""),
					str(job.get("status", "")),
					str(job.get("job_title") or job.get("title") or ""),
				)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Load more failed: {e}[/red]")
		finally:
			self._update_status_bar()

	def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:  # type: ignore[override]
		try:
			row_key = event.row_key
			row_index = self.jobs_table.get_row_index(row_key)
			filtered = self._apply_filter(self.jobs)
			if 0 <= row_index < len(filtered):
				self.selected_job = filtered[row_index]
				self._render_details(self.selected_job)
		except Exception:
			pass

	def _render_details(self, job: Dict[str, Any]) -> None:
		# Summary, Parameters, Artifacts
		summary_lines: List[str] = []
		summary_lines.append(f"[b]Job ID:[/b] {job.get('job_id') or job.get('id')}")
		summary_lines.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
		summary_lines.append(f"[b]Status:[/b] {job.get('status')}")
		title = job.get('job_title') or job.get('title')
		if title:
			summary_lines.append(f"[b]Title:[/b] {title}")
		project = job.get('project_id')
		if project:
			summary_lines.append(f"[b]Project:[/b] {project}")
		tool = (job.get('tool_name') or job.get('job_type') or '').lower()
		if tool in {"esmfold", "alphafold"}:
			summary_lines.append("[b]Protein:[/b] structure prediction task")
		if tool in {"diffdock", "reinvent", "admetlab3"}:
			summary_lines.append("[b]Compound:[/b] molecular/docking/design task")
		status_l = (job.get('status') or '').lower()
		if status_l in {"completed", "success"}:
			summary_lines.append("[dim]Hint: press 'o' to open available artifacts externally[/dim]")
		if self.details_summary:
			self.details_summary.update("\n".join(summary_lines))

		params_obj = job.get('parameters') or job.get('request_params') or {}
		try:
			params_text = json.dumps(params_obj, indent=2) if params_obj else "No parameters"
		except Exception:
			params_text = str(params_obj)
		if self.details_params:
			self.details_params.update(params_text)

		artifacts_render = Table(title="Artifacts", show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}")
		artifacts_render.add_column("Type", style="green")
		artifacts_render.add_column("Filename", style="blue")
		artifacts_render.add_column("Size", style="yellow")
		try:
			job_id = str(job.get('job_id') or job.get('id') or '').strip()
			if job_id:
				data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
				arts = data.get('artifacts') if isinstance(data, dict) else []
				for art in arts or []:
					if isinstance(art, dict):
						artifacts_render.add_row(
							str(art.get('artifact_type') or art.get('type') or ''),
							str(art.get('filename') or ''),
							str(art.get('file_size') or ''),
						)
		except Exception as e:
			artifacts_render = Table(title=f"Artifacts (error: {e})")
		if self.details_artifacts:
			self.details_artifacts.update(artifacts_render)

	def action_refresh(self) -> None:
		self.call_later(self._load_jobs)

	def action_focus_filter(self) -> None:
		if self.cmd_input:
			self.cmd_input.focus()

	def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
		if self.cmd_input and event.input is self.cmd_input:
			args_line = (event.value or "").strip()
			if not args_line:
				return
			self._cmd_run_custom(args_line)

	def action_toggle_help(self) -> None:
		pass

	def action_open_external(self) -> None:
		job = self.selected_job
		if not job:
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			return
		try:
			# Thin wrapper: query artifacts via CLI in list-only JSON mode
			data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
			candidate_urls: List[str] = []
			# Preferred selection: artifacts list with type and URL
			artifacts = []
			if isinstance(data, dict):
				artifacts = data.get("artifacts") or []
			for art in artifacts:
				if not isinstance(art, dict):
					continue
				url = art.get("presigned_url") or art.get("url")
				aType = str(art.get("artifact_type") or art.get("type") or "").lower()
				if url and (any(t in aType for t in ["pdb", "sdf", "primary", "zip"])):
					candidate_urls.append(str(url))
			# Fallback: scan any string URLs elsewhere
			if not candidate_urls and isinstance(data, dict):
				for val in data.values():
					if isinstance(val, str) and val.startswith("http"):
						candidate_urls.append(val)
					elif isinstance(val, list):
						candidate_urls.extend([v for v in val if isinstance(v, str) and v.startswith("http")])
			if candidate_urls:
				webbrowser.open(candidate_urls[0])
				if self.details_summary:
					self.details_summary.update("Opening artifact in browser...")
			else:
				if self.details_summary:
					self.details_summary.update(f"No artifact URLs found. Try 'ivybloom jobs download {job_id}'.")
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Open failed: {e}[/red]")

	# ------------------ CLI wrapper helper ------------------
	def _run_cli_json(self, args: List[str], timeout: int = 30) -> Any:
		"""Run ivybloom CLI with provided args and parse JSON output.
		Prepends --config-file to ensure same context as running CLI.
		Raises on non-zero exit or invalid JSON.
		"""
		cmd: List[str] = [
			"ivybloom",
			"--config-file",
			str(self.config.config_path),
		] + args
		result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
		if result.returncode != 0:
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		output = result.stdout.strip()
		if not output:
			return None
		try:
			return json.loads(output)
		except json.JSONDecodeError:
			raise RuntimeError(f"Invalid JSON from CLI: {output[:200]}...")
		
	def _probe_connectivity(self) -> None:
		try:
			_ = self._run_cli_text(["version"], timeout=5)
			self._connected = True
		except Exception:
			self._connected = False
		finally:
			self._update_status_bar()

	def _update_status_bar(self) -> None:
		if not self.status_bar:
			return
		connected = "connected ✓" if self._connected else "offline ✗"
		err = f"errors: {'1' if self._last_error else '0'}"
		status = f"[dim][status: {connected}][refresh: {self.refresh_interval_secs}s][project: {self.initial_project_id or 'N/A'}] [{err}][/dim]"
		self.status_bar.update(status)

	def _run_cli_text(self, args: List[str], timeout: int = 60, input_text: Optional[str] = None) -> str:
		cmd: List[str] = [
			"ivybloom",
			"--config-file",
			str(self.config.config_path),
		] + args
		result = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout)
		if result.returncode != 0:
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		return result.stdout

	# ------------------ Command handlers (thin wrappers) ------------------
	async def _cmd_projects_list(self) -> None:
		try:
			text = self._run_cli_text(["projects", "list"]) or ""
			if self.details_summary:
				self.details_summary.update(text or "No projects found")
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Projects list failed: {e}[/red]")

	async def _cmd_account_info(self) -> None:
		try:
			text = self._run_cli_text(["account", "info"]) or ""
			if self.details_summary:
				self.details_summary.update(text or "No account info")
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Account info failed: {e}[/red]")

	def _cmd_tools_info(self, tool: Optional[str]) -> None:
		if not tool:
			return
		try:
			text = self._run_cli_text(["tools", "info", tool, "--format", "table"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Tool info failed: {e}[/red]")

	def _cmd_tools_schema(self, tool: Optional[str]) -> None:
		if not tool:
			return
		try:
			text = self._run_cli_text(["tools", "schema", tool, "--format", "table"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Tool schema failed: {e}[/red]")

	def _cmd_tools_completions(self, tool: Optional[str]) -> None:
		if not tool:
			return
		try:
			text = self._run_cli_text(["tools", "completions", tool, "--format", "table"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Tool completions failed: {e}[/red]")

	def _cmd_jobs_list(self, extra_args: Optional[str]) -> None:
		import shlex
		args = ["jobs", "list", "--format", "json"]
		if extra_args:
			args += shlex.split(extra_args)
		try:
			jobs = self._run_cli_json(args) or []
			if not isinstance(jobs, list):
				jobs = []
			self.jobs = jobs
			self.jobs_table.clear()
			for job in self._apply_filter(jobs):
				self.jobs_table.add_row(
					str(job.get("job_id") or job.get("id") or ""),
					str(job.get("tool_name") or job.get("job_type") or ""),
					str(job.get("status", "")),
					str(job.get("job_title") or job.get("title") or ""),
				)
			if self.details_summary:
				self.details_summary.update(f"[dim]Loaded {len(jobs)} jobs[/dim]")
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Jobs list failed: {e}[/red]")

	def _cmd_jobs_status(self, job_id: Optional[str]) -> None:
		if not job_id:
			return
		try:
			text = self._run_cli_text(["jobs", "status", job_id, "--format", "table"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Jobs status failed: {e}[/red]")

	def _cmd_jobs_results(self, job_id: Optional[str]) -> None:
		if not job_id:
			return
		try:
			text = self._run_cli_text(["jobs", "results", job_id, "--format", "json"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Jobs results failed: {e}[/red]")

	def _cmd_jobs_download(self, job_id: Optional[str]) -> None:
		if not job_id:
			return
		try:
			# default to list-only to avoid writing files implicitly
			text = self._run_cli_text(["jobs", "download", job_id, "--list-only", "--format", "table"]) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Jobs download failed: {e}[/red]")

	def _cmd_jobs_cancel(self, job_id: Optional[str]) -> None:
		if not job_id:
			return
		try:
			# auto-confirm cancellation to avoid interactive prompt
			text = self._run_cli_text(["jobs", "cancel", job_id], input_text="y\n") or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Jobs cancel failed: {e}[/red]")

	def _cmd_run_tool_start(self, tool: Optional[str]) -> None:
		if not tool:
			return
		self.push_screen(PromptScreen(f"Parameters for '{tool}' (key=value ...)", placeholder="optional"), lambda params: self._cmd_run_tool(tool, params))

	def _cmd_run_tool(self, tool: str, params: Optional[str]) -> None:
		import shlex
		args = ["run", tool]
		if params:
			args += shlex.split(params)
		try:
			text = self._run_cli_text(args, timeout=3600) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Run tool failed: {e}[/red]")

	def _cmd_workflows_run_start(self, path: Optional[str]) -> None:
		if not path:
			return
		self.push_screen(PromptScreen("Extra args (e.g., --dry-run --input key=val)", placeholder="optional"), lambda extra: self._cmd_workflows_run(path, extra))

	def _cmd_workflows_run(self, path: str, extra: Optional[str]) -> None:
		import shlex
		args = ["workflows", "run", path]
		if extra:
			args += shlex.split(extra)
		try:
			text = self._run_cli_text(args, timeout=3600) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Workflows run failed: {e}[/red]")

	def _cmd_run_custom(self, extra: Optional[str]) -> None:
		import shlex
		if not extra:
			return
		try:
			args = shlex.split(extra)
			text = self._run_cli_text(args, timeout=600) or ""
			if self.details_summary:
				self.details_summary.update(text)
		except Exception as e:
			if self.details_summary:
				self.details_summary.update(f"[red]Custom command failed: {e}[/red]")

	def _cmd_artifacts_list(self) -> None:
		job = self.selected_job
		if not job:
			if self.details_artifacts:
				self.details_artifacts.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.details_artifacts:
				self.details_artifacts.update("Invalid job id")
			return
		try:
			data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
			table = Table(title="Artifacts", show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}")
			table.add_column("Type", style="green")
			table.add_column("Filename", style="blue")
			table.add_column("Size", style="yellow")
			table.add_column("URL", style="dim")
			arts = data.get('artifacts') if isinstance(data, dict) else []
			for art in arts or []:
				if isinstance(art, dict):
					table.add_row(
						str(art.get('artifact_type') or art.get('type') or ''),
						str(art.get('filename') or ''),
						str(art.get('file_size') or ''),
						(art.get('presigned_url') or '')[:40] + ('...' if art.get('presigned_url') else ''),
					)
			if self.details_artifacts:
				self.details_artifacts.update(table)
		except Exception as e:
			if self.details_artifacts:
				self.details_artifacts.update(f"[red]Artifacts list failed: {e}[/red]")

	def _cmd_artifact_preview(self, selector: Optional[str]) -> None:
		job = self.selected_job
		if not job:
			if self.details_artifacts:
				self.details_artifacts.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.details_artifacts:
				self.details_artifacts.update("Invalid job id")
			return
		try:
			data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
			arts = data.get('artifacts') if isinstance(data, dict) else []
			chosen = None
			sel = (selector or "").strip().lower()
			def is_match(a: Dict[str, Any]) -> bool:
				if not sel:
					return True
				t = str(a.get('artifact_type') or a.get('type') or '').lower()
				fn = str(a.get('filename') or '').lower()
				return sel in t or sel in fn
			for tprio in ("json", "csv"):
				for a in arts or []:
					if not isinstance(a, dict):
						continue
					at = str(a.get('artifact_type') or a.get('type') or '').lower()
					if at == tprio and is_match(a):
						chosen = a
						break
				if chosen:
					break
			if not chosen:
				for a in arts or []:
					if isinstance(a, dict) and is_match(a):
						chosen = a
						break
			if not chosen:
				if self.details_artifacts:
					self.details_artifacts.update("No suitable artifact found (JSON/CSV)")
				return
			url = chosen.get('presigned_url') or chosen.get('url')
			if not url:
				if self.details_artifacts:
					self.details_artifacts.update("Artifact has no URL. Try 'jobs download'.")
				return
			import requests
			resp = requests.get(url, timeout=15)
			resp.raise_for_status()
			content_type = (resp.headers.get('Content-Type') or '').lower()
			content = resp.content
			text = None
			try:
				text = content.decode('utf-8')
			except Exception:
				try:
					text = content.decode('latin-1')
				except Exception:
					text = None
			max_json_bytes = 200 * 1024
			max_csv_bytes = 500 * 1024
			filename = str(chosen.get('filename') or '')
			# JSON
			if 'application/json' in content_type or filename.lower().endswith('.json'):
				if len(content) > max_json_bytes:
					if self.details_artifacts:
						self.details_artifacts.update(f"JSON too large to preview ({len(content)} bytes). Use Open/Download.")
					return
				try:
					data_obj = json.loads(text or "")
					if isinstance(data_obj, list) and data_obj and isinstance(data_obj[0], dict):
						cols = list(data_obj[0].keys())[:20]
						table = Table(title=f"JSON Preview: {filename}")
						for c in cols:
							table.add_column(str(c))
						for row in data_obj[:100]:
							table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
						if self.details_artifacts:
							self.details_artifacts.update(table)
					else:
						pretty = json.dumps(data_obj, indent=2)
						if self.details_artifacts:
							self.details_artifacts.update(pretty)
				except Exception as e:
				if self.details_artifacts:
					self.details_artifacts.update(f"[red]JSON parse failed: {e}[/red]")
				return
			# CSV
			if 'text/csv' in content_type or filename.lower().endswith('.csv'):
				if len(content) > max_csv_bytes:
					preview_text = (text or '').splitlines()[:15]
					if self.details_artifacts:
						self.details_artifacts.update("\n".join(preview_text) + "\n[dim](truncated) Use Open/Download[/dim]")
					return
				try:
					sample = (text or '')[:4096]
					try:
						dialect = csv.Sniffer().sniff(sample)
					except Exception:
						dialect = csv.excel
					reader = csv.reader(io.StringIO(text or ''), dialect)
					rows = list(reader)
					if not rows:
						if self.details_artifacts:
							self.details_artifacts.update("Empty CSV")
						return
					table = Table(title=f"CSV Preview: {filename}")
					header = rows[0]
					for h in header[:20]:
						table.add_column(str(h))
					for r in rows[1:101]:
						table.add_row(*[str(x)[:120] for x in r[:20]])
					if self.details_artifacts:
						self.details_artifacts.update(table)
				except Exception as e:
				if self.details_artifacts:
					self.details_artifacts.update(f"[red]CSV parse failed: {e}[/red]")
				return
			# Fallback
			if self.details_artifacts:
				self.details_artifacts.update(f"Unsupported content type: {content_type or 'unknown'}. Use Open/Download.")
		except Exception as e:
			if self.details_artifacts:
				self.details_artifacts.update(f"[red]Artifact preview failed: {e}[/red]")

	def _cmd_protein_view_ascii(self) -> None:
		job = self.selected_job
		if not job:
			if self.details_structure:
				self.details_structure.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.details_structure:
				self.details_structure.update("Invalid job id")
			return
		try:
			data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
			arts = data.get('artifacts') if isinstance(data, dict) else []
			pdb_url = None
			for art in arts or []:
				if not isinstance(art, dict):
					continue
				aType = str(art.get('artifact_type') or art.get('type') or '').lower()
				if aType == 'pdb' and art.get('presigned_url'):
					pdb_url = art.get('presigned_url')
					break
			if not pdb_url:
				if self.details_structure:
					self.details_structure.update("No PDB artifact found")
				return
			import requests
			resp = requests.get(pdb_url, timeout=10)
			resp.raise_for_status()
			pdb_text = resp.text
			self._structure_points = self._parse_pdb_ca(pdb_text)
			self._structure_angle = 0.0
			# Start animation timer
			try:
				if self._structure_timer:
					self._structure_timer.stop()  # type: ignore[attr-defined]
			except Exception:
				pass
			try:
				self._structure_timer = self.set_interval(0.15, self._render_ascii_frame)
			except Exception as e:
				if self.details_structure:
					self.details_structure.update(f"[red]Animation failed to start: {e}[/red]")
		except Exception as e:
			if self.details_structure:
				self.details_structure.update(f"[red]Failed to load PDB: {e}[/red]")

	def _stop_protein_ascii(self) -> None:
		try:
			if self._structure_timer:
				self._structure_timer.stop()  # type: ignore[attr-defined]
				self._structure_timer = None
		except Exception:
			pass
		if self.details_structure:
			self.details_structure.update("Stopped.")

	def _parse_pdb_ca(self, pdb_text: str) -> List[Tuple[float, float, float]]:
		points: List[Tuple[float, float, float]] = []
		for line in pdb_text.splitlines():
			if not line.startswith("ATOM"):
				continue
			# Atom name cols 13-16; coords cols 31-54
			name = line[12:16].strip()
			if name != 'CA':
				continue
			try:
				x = float(line[30:38].strip())
				y = float(line[38:46].strip())
				z = float(line[46:54].strip())
				points.append((x, y, z))
			except Exception:
				continue
		# Center & scale
		if not points:
			return []
		cx = sum(p[0] for p in points) / len(points)
		cy = sum(p[1] for p in points) / len(points)
		cz = sum(p[2] for p in points) / len(points)
		centered = [(p[0]-cx, p[1]-cy, p[2]-cz) for p in points]
		max_r = max(math.sqrt(px*px+py*py+pz*pz) for px,py,pz in centered) or 1.0
		scale = 1.0 / max_r
		return [(px*scale, py*scale, pz*scale) for px,py,pz in centered]

	def _render_ascii_frame(self) -> None:
		if not self.details_structure:
			return
		if not self._structure_points:
			self.details_structure.update("No structure loaded")
			return
		# Grid
		rows, cols = 30, 80
		angle = self._structure_angle
		ca = math.cos(angle)
		sa = math.sin(angle)
		cb = math.cos(angle*0.5)
		sb = math.sin(angle*0.5)
		grid = [[" "]*cols for _ in range(rows)]
		charset = ".:*oO#@"
		step = max(1, len(self._structure_points)//1500 or 1)
		for x,y,z in self._structure_points[::step]:
			# Rotate Y then X
			x1 = ca*x + sa*z
			z1 = -sa*x + ca*z
			y1 = cb*y - sb*z1
			z2 = sb*y + cb*z1
			# Project
			u = int((x1*0.5 + 0.5) * (cols-1))
			v = int((y1*0.5 + 0.5) * (rows-1))
			if 0 <= v < rows and 0 <= u < cols:
				depth = (z2*0.5 + 0.5)
				ch = charset[min(len(charset)-1, max(0, int(depth*len(charset))))]
				grid[v][u] = ch
		self._structure_angle += 0.12
		art = "\n".join("".join(r) for r in grid)
		self.details_structure.update(art)


class CommandPalette(ModalScreen[Optional[str]]):
	def __init__(self, commands: List[tuple[str, str, str]]):
		super().__init__()
		self._all_commands = commands
		self._filtered = commands
		self.query: Input | None = None
		self.list_view: ListView | None = None

	def compose(self) -> ComposeResult:
		with Vertical():
			self.query = Input(placeholder="Type to filter commands… (Esc to close)")
			yield self.query
			self.list_view = ListView()
			yield self.list_view

	def on_mount(self) -> None:
		self._refresh_list()
		if self.query:
			self.query.focus()

	def _refresh_list(self) -> None:
		if not self.list_view:
			return
		self.list_view.clear()
		for cmd_id, name, desc in self._filtered:
			self.list_view.append(ListItem(Static(f"[b]{name}[/b]\n[dim]{desc}[/dim]")))

	def on_input_changed(self, event: Input.Changed) -> None:  # type: ignore[override]
		if event.input is not self.query:
			return
		q = (event.value or "").strip().lower()
		if not q:
			self._filtered = self._all_commands
		else:
			self._filtered = [c for c in self._all_commands if q in c[1].lower() or q in c[2].lower()]
		self._refresh_list()

	def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
		# Map selection index back to filtered commands
		index = event.index
		if 0 <= index < len(self._filtered):
			cmd_id = self._filtered[index][0]
			self.dismiss(cmd_id)
		else:
			self.dismiss(None)

	def on_key(self, event) -> None:  # type: ignore[override]
		if event.key == "escape":
			self.dismiss(None)


class PromptScreen(ModalScreen[Optional[str]]):
	def __init__(self, prompt: str, placeholder: str = ""):
		super().__init__()
		self._prompt = prompt
		self._placeholder = placeholder
		self.input: Input | None = None

	def compose(self) -> ComposeResult:
		with Vertical():
			yield Static(self._prompt)
			self.input = Input(placeholder=self._placeholder or "Press Enter to submit; Esc to cancel")
			yield self.input

	def on_mount(self) -> None:
		if self.input:
			self.input.focus()

	def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
		if event.input is self.input:
			self.dismiss(event.value)

	def on_key(self, event) -> None:  # type: ignore[override]
		if event.key == "escape":
			self.dismiss(None)


class SplashScreen(ModalScreen[None]):
	def __init__(self, title: str = "IvyBloom", subtitle: str = "Loading…"):
		super().__init__()
		self._title = title
		self._subtitle = subtitle

	def compose(self) -> ComposeResult:
		ascii_logo = "\n".join([
			"  ____      __     ____  _                          ",
			" |_  /___  / /__  / __ )(_)___  ____  ____ _      __",
			"  / // _ \\/ / _ \\/ __  / / __ \\_/ __ \\/ __ \\ | /| / /",
			" /___/\\___/_/\\___/_/ /_/_/_/ /_(_) /_/ / /_/ / |/ |/ / ",
			"                                 /____/\\____/|__/|__/  ",
		])
		with Vertical(classes="splash"):
			yield Static(f"[b]{self._title}[/b]", classes="panel-title")
			yield Static(ascii_logo)
			yield LoadingIndicator()
			yield Static(f"[dim]{self._subtitle}[/dim]", classes="muted")

	def on_key(self, event) -> None:  # type: ignore[override]
		if event.key == "escape":
			self.dismiss(None)




