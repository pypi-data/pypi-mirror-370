from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
import webbrowser
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
from .cli_runner import CLIRunner
from .artifacts_service import ArtifactsService
from .structure_service import StructureService
from .jobs_service import JobsService
from .projects_service import ProjectsService


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
        # Help toggle state
        self._help_visible: bool = False
        self._help_prev_renderable = None

        # Services
        self._runner = CLIRunner(self.config)
        self._artifacts = ArtifactsService(self._runner)
        self._structure = StructureService()
        self._jobs = JobsService(self._runner)
        self._projects = ProjectsService(self._runner)

        # Project picker state
        self._picker_open: bool = False
        self._project_pick_timer = None

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
        # Welcome message
        try:
            user = self.auth_manager.get_current_user_id() if hasattr(self.auth_manager, 'get_current_user_id') else None
            welcome = f"Welcome, {user}!" if user else "Welcome!"
            if self.details_summary:
                self.details_summary.update(f"[bold]{welcome}[/bold] Initializing…")
        except Exception:
            pass
        # Forced splash + boot sequence
        self._splash_opened = False  # type: ignore[attr-defined]
        self._show_splash()
        self._start_boot_sequence()
        # Auto refresh and connectivity (kicks in after boot)
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

    def _start_boot_sequence(self) -> None:
        """Show splash for at least 5 seconds while connecting; then auth; then project pick; then load jobs."""
        # Kick off an initial connectivity probe
        try:
            self._probe_connectivity()
        except Exception:
            pass
        # Continue boot after minimum splash duration
        try:
            self.set_timer(5, self._continue_boot_sequence)
        except Exception:
            # If timers fail, continue immediately
            self._continue_boot_sequence()

    def _continue_boot_sequence(self) -> None:
        # Require authentication first
        try:
            if not self.auth_manager.is_authenticated():
                if self.details_summary:
                    self.details_summary.update("Please authenticate to continue (browser|device|link|paste API key).")
                self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
                return
        except Exception:
            # If auth manager errors, still try to prompt
            self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
            return
        # If authenticated, ensure project selection
        self.call_later(self._ensure_project_then_load)

    def _on_auth_chosen(self, choice: Optional[str]) -> None:
        sel = (choice or "").strip()
        if not sel:
            # default to browser
            sel = "browser"
        try:
            if sel.lower() in {"browser", "b"}:
                text = self._run_cli_text(["auth", "login", "--browser"], timeout=600) or ""
            elif sel.lower() in {"device", "d"}:
                text = self._run_cli_text(["auth", "login", "--device"], timeout=600) or ""
            elif sel.lower() in {"link", "l"}:
                text = self._run_cli_text(["auth", "login", "--link"], timeout=600) or ""
            else:
                # Treat input as API key
                text = self._run_cli_text(["auth", "login", "--api-key", sel], timeout=120) or ""
            if self.details_summary:
                self.details_summary.update(text or "Authentication flow completed.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Authentication failed: {e}[/red]")
            # Re-prompt
            self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
            return
        # After auth, proceed to project selection
        self.call_later(self._ensure_project_then_load)

    def _ensure_project_then_load(self) -> None:
        # If no project chosen, open picker; otherwise load jobs and hide splash once loaded
        if not self.initial_project_id:
            try:
                projects = self._projects.list_projects()
                if projects:
                    self._picker_open = True
                    self.push_screen(ProjectPicker(projects), self._on_project_picked)
                    if self.details_summary:
                        self.details_summary.update("Select a project to continue…")
                    return
                else:
                    if self.details_summary:
                        self.details_summary.update("No projects available. Create one in the web app.")
            except Exception as e:
                if self.details_summary:
                    self.details_summary.update(f"[red]Failed to load projects: {e}[/red]")
                # Retry shortly
                try:
                    self.set_timer(3, self._ensure_project_then_load)
                except Exception:
                    pass
                return
        # If we have a project, load jobs
        self.call_later(self._load_jobs)

    # ------------------ Command Palette ------------------
    def action_open_palette(self) -> None:
        commands = [
            ("list_tools", "Tools: List", "Show tools (choose format/verbosity)"),
            ("tools_info", "Tools: Info", "Show detailed info for a tool (choose format)"),
            ("tools_schema", "Tools: Schema", "Show parameter schema for a tool (choose format)"),
            ("tools_completions", "Tools: Completions", "Show enum choices for a tool (choose format)"),
            ("jobs_list", "Jobs: List", "List jobs with optional filters"),
            ("jobs_status", "Jobs: Status", "Show job status (optionally follow)"),
            ("jobs_results", "Jobs: Results", "Fetch job results (JSON)"),
            ("jobs_download", "Jobs: Download", "List/download job artifacts"),
            ("jobs_cancel", "Jobs: Cancel", "Cancel a running job"),
            ("projects_list", "Projects: List", "List projects"),
            ("projects_info", "Projects: Info", "Show project info"),
            ("projects_jobs", "Projects: Jobs", "List jobs for a project"),
            ("account_info", "Account: Info", "Show account info"),
            ("account_usage", "Account: Usage", "Show usage (choose period/tool)"),
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
            ("artifact_open_primary", "Artifacts: Open Primary", "Open primary (or best) artifact externally"),
            ("protein_view_ascii", "Protein: View ASCII", "Load and rotate ASCII protein (PDB)"),
            ("protein_stop_ascii", "Protein: Stop ASCII", "Stop protein ASCII view"),
            ("pick_project", "Project: Pick", "Select a project to focus"),
        ]
        self.push_screen(CommandPalette(commands), self._on_palette_result)

    def _on_palette_result(self, result: Optional[str]) -> None:
        if not result:
            return
        if result == "list_tools":
            # Prompt for options: format, verbose, schemas
            def _after_fmt(fmt: Optional[str]):
                def _after_verbose(verbose: Optional[str]):
                    def _after_schemas(schemas: Optional[str]):
                        self.call_later(lambda: self._cmd_tools_list(fmt or "table", (verbose or "no").lower() in {"yes","y","true"}, (schemas or "no").lower() in {"yes","y","true"}))
                    self.push_screen(PromptScreen("Embed schemas? (yes/no)", placeholder="no"), _after_schemas)
                self.push_screen(PromptScreen("Verbose? (yes/no)", placeholder="no"), _after_verbose)
            self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), _after_fmt)
        elif result == "tools_info":
            def _after_tool(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._cmd_tools_info(tool, fmt or "table"))
            self.push_screen(PromptScreen("Tool name (e.g., esmfold)"), _after_tool)
        elif result == "tools_schema":
            def _after_tool_schema(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._cmd_tools_schema(tool, fmt or "table"))
            self.push_screen(PromptScreen("Tool name for schema"), _after_tool_schema)
        elif result == "tools_completions":
            def _after_tool_comp(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._cmd_tools_completions(tool, fmt or "table"))
            self.push_screen(PromptScreen("Tool name for completions"), _after_tool_comp)
        elif result == "jobs_list":
            self.push_screen(FiltersScreen(), lambda filters: self._cmd_jobs_list_with_filters(filters))
        elif result == "jobs_status":
            # Ask for job id, then optional flags
            def _after_job_id(job_id: Optional[str]) -> None:
                if not job_id:
                    return
                self.push_screen(PromptScreen("Extra flags (e.g., --follow --logs)", placeholder="optional"), lambda flags: self._cmd_jobs_status(job_id, flags))
            self.push_screen(PromptScreen("Job ID (then choose flags)"), _after_job_id)
        elif result == "jobs_results":
            self.push_screen(PromptScreen("Job ID for results"), lambda job_id: self._cmd_jobs_results(job_id))
        elif result == "jobs_download":
            self.push_screen(PromptScreen("Job ID to download/list"), lambda job_id: self._cmd_jobs_download(job_id))
        elif result == "jobs_cancel":
            self.push_screen(PromptScreen("Job ID to cancel"), lambda job_id: self._cmd_jobs_cancel(job_id))
        elif result == "projects_list":
            self.call_later(self._cmd_projects_list)
        elif result == "projects_info":
            self.push_screen(PromptScreen("Project ID"), lambda pid: self._cmd_projects_info(pid))
        elif result == "projects_jobs":
            self.push_screen(PromptScreen("Project ID"), lambda pid: self._cmd_projects_jobs(pid))
        elif result == "account_info":
            self.call_later(self._cmd_account_info)
        elif result == "account_usage":
            def _after_tool(val_tool: Optional[str]):
                self.push_screen(PromptScreen("Period (month|30days|all)", placeholder="month"), lambda period: self._cmd_account_usage(val_tool, period or "month"))
            self.push_screen(PromptScreen("Filter by tool (optional)"), _after_tool)
        elif result == "artifacts_list":
            self.call_later(self._cmd_artifacts_list)
        elif result == "artifact_preview":
            self.push_screen(PromptScreen("Artifact type or filename (optional)", placeholder="optional"), lambda sel: self._cmd_artifact_preview(sel))
        elif result == "artifact_open_primary":
            self.call_later(self._cmd_artifact_open_primary)
        elif result == "protein_view_ascii":
            self._cmd_protein_view_ascii()
        elif result == "protein_stop_ascii":
            self._stop_protein_ascii()
        elif result == "pick_project":
            self.call_later(self._cmd_pick_project)
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
            self._cmd_jobs_list_with_filters({"status": "running"})
        elif result == "quick_status_completed":
            self._cmd_jobs_list_with_filters({"status": "completed"})
        elif result == "open_external":
            self.action_open_external()
        elif result == "toggle_help":
            self.action_toggle_help()

    async def _cmd_tools_list(self, fmt: str, verbose: bool, schemas: bool) -> None:
        try:
            args = ["tools", "list", "--format", fmt or "table"]
            if verbose:
                args.append("--verbose")
            if schemas:
                args.append("--format-json-with-schemas")
            if (fmt or "table").lower() == "json":
                data = self._run_cli_json(args) or []
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                # Table: if JSON list provided, render custom table; else reuse CLI text
                try:
                    tools_json = self._run_cli_json(["tools", "list", "--format", "json"] + (["--verbose"] if verbose else [])) or []
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
                except Exception:
                    text = self._run_cli_text(args) or ""
                    if self.details_summary:
                        self.details_summary.update(text)
            self._last_error = None
        except Exception as e:
            self._last_error = str(e)
            if self.details_summary:
                self.details_summary.update(f"[red]Failed to load tools: {e}[/red]")
        finally:
            self._update_status_bar()

    def _apply_filter(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Filters disabled for now; keep placeholder for future
        return jobs

    async def _load_jobs(self) -> None:
        self.jobs_offset = 0
        self.jobs_table.clear()
        try:
            jobs = self._jobs.list_jobs(self.initial_project_id, self.jobs_limit, self.jobs_offset)
            self.jobs = jobs
            for job in self._apply_filter(jobs):
                self.jobs_table.add_row(*JobsService.format_row(job))
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Failed to load jobs: {e}[/red]")
        finally:
            self._hide_splash()

    def _cmd_jobs_load_more(self) -> None:
        # Fetch next page and append
        try:
            self.jobs_offset += self.jobs_limit
            new_jobs = self._jobs.list_jobs(self.initial_project_id, self.jobs_limit, self.jobs_offset)
            self.jobs.extend(new_jobs)
            for job in new_jobs:
                self.jobs_table.add_row(*JobsService.format_row(job))
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
            # Simple built-in command: pick <project_id>
            parts = args_line.split()
            if parts and parts[0].lower() == "pick" and len(parts) > 1:
                self.initial_project_id = parts[1]
                if self.details_summary:
                    self.details_summary.update(f"Project set to {self.initial_project_id}. Reloading jobs…")
                self.call_later(self._load_jobs)
                return
            self._cmd_run_custom(args_line)

    def action_toggle_help(self) -> None:
        if not self.details_summary:
            return
        if not self._help_visible:
            # Save previous renderable and show shortcuts
            self._help_prev_renderable = self.details_summary.renderable
            help_text = "\n".join([
                "[b]Shortcuts[/b]",
                " r  – Refresh",
                " /  – Open command palette",
                " f  – Focus command input",
                " o  – Open artifact externally",
                " ?  – Toggle help",
                " q  – Quit",
            ])
            self.details_summary.update(help_text)
            self._help_visible = True
        else:
            # Restore previous content
            try:
                if self._help_prev_renderable is not None:
                    self.details_summary.update(self._help_prev_renderable)
            except Exception:
                self.details_summary.update("")
            finally:
                self._help_visible = False

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
        """Delegate to CLIRunner for JSON output."""
        return self._runner.run_cli_json(args, timeout=timeout)
        
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
        """Delegate to CLIRunner for text output."""
        return self._runner.run_cli_text(args, timeout=timeout, input_text=input_text)

    # ------------------ Command handlers (thin wrappers) ------------------
    async def _cmd_projects_list(self) -> None:
        try:
            text = self._run_cli_text(["projects", "list"]) or ""
            if self.details_summary:
                self.details_summary.update(text or "No projects found")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Projects list failed: {e}[/red]")

    def _cmd_projects_info(self, project_id: Optional[str]) -> None:
        if not project_id:
            return
        try:
            text = self._run_cli_text(["projects", "info", project_id, "--format", "table"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project info failed: {e}[/red]")

    def _cmd_projects_jobs(self, project_id: Optional[str]) -> None:
        if not project_id:
            return
        try:
            text = self._run_cli_text(["projects", "jobs", project_id, "--format", "table"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project jobs failed: {e}[/red]")

    async def _cmd_account_info(self) -> None:
        try:
            text = self._run_cli_text(["account", "info"]) or ""
            if self.details_summary:
                self.details_summary.update(text or "No account info")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Account info failed: {e}[/red]")

    def _cmd_account_usage(self, tool: Optional[str], period: str) -> None:
        try:
            args = ["account", "usage", "--format", "table"]
            if tool:
                args += ["--tool", tool]
            if period:
                args += ["--period", period]
            text = self._run_cli_text(args) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Account usage failed: {e}[/red]")

    def _cmd_tools_info(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "info", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "info", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool info failed: {e}[/red]")

    def _cmd_tools_schema(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "schema", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "schema", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool schema failed: {e}[/red]")

    def _cmd_tools_completions(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "completions", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "completions", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool completions failed: {e}[/red]")

    def _cmd_jobs_list_with_filters(self, filters: Optional[Dict[str, str]]) -> None:
        args = ["jobs", "list", "--format", "json"]
        if filters:
            for k, v in filters.items():
                if v:
                    args += [f"--{k}", str(v)]
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

    def _cmd_jobs_status(self, job_id: Optional[str], extra_flags: Optional[str]) -> None:
        if not job_id:
            return
        try:
            import shlex
            args = ["jobs", "status", job_id, "--format", "table"]
            if extra_flags:
                args += shlex.split(extra_flags)
            # If follow requested, stream lines into Summary
            follow = any(flag in args for flag in ["--follow", "-f"]) 
            if follow and self.details_summary:
                self.details_summary.update("[dim]Following job... press Ctrl+C in terminal to stop.[/dim]")
                for line in self._runner.run_cli_stream(args):
                    self.details_summary.update(line)
            else:
                text = self._run_cli_text(args, timeout=600) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs status failed: {e}[/red]")

    def _cmd_jobs_results(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            data = self._run_cli_json(["jobs", "results", job_id, "--format", "json"]) or {}
            # Render as table if list-of-dicts
            table = None
            if isinstance(data, list) and data and isinstance(data[0], dict):
                cols = list(data[0].keys())[:20]
                table = Table(title="Job Results")
                for c in cols:
                    table.add_column(str(c))
                for row in data[:200]:
                    table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
            elif isinstance(data, dict):
                # If "results" key exists and is list-of-dicts, tabularize that
                results = data.get("results")
                if isinstance(results, list) and results and isinstance(results[0], dict):
                    cols = list(results[0].keys())[:20]
                    table = Table(title="Job Results")
                    for c in cols:
                        table.add_column(str(c))
                    for row in results[:200]:
                        table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
            if table is not None:
                if self.details_summary:
                    self.details_summary.update(table)
            else:
                # Fallback to pretty JSON string
                pretty = json.dumps(data, indent=2)
                if self.details_summary:
                    self.details_summary.update(pretty)
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

    async def _cmd_pick_project(self) -> None:
        try:
            projects = self._projects.list_projects()
            if not projects:
                if self.details_summary:
                    self.details_summary.update("No projects available.")
                return
            self.push_screen(ProjectPicker(projects), self._on_project_picked)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project listing failed: {e}[/red]")

    def _on_project_picked(self, project_id: Optional[str]) -> None:
        # Picker dismissed
        self._picker_open = False
        if not project_id:
            # No selection; prompt again soon
            try:
                self._project_pick_timer = self.set_timer(3, self._ensure_project_pick)
            except Exception:
                pass
            return
        self.initial_project_id = project_id
        if self.details_summary:
            self.details_summary.update(f"Project set to {self.initial_project_id}. Reloading jobs…")
        # Show splash and load jobs now that we have a project
        self._splash_opened = False  # type: ignore[attr-defined]
        self._show_splash()
        self.call_later(self._load_jobs)

    def _ensure_project_pick(self) -> None:
        if self.initial_project_id or self._picker_open:
            return
        try:
            projects = self._projects.list_projects()
            if projects:
                self._picker_open = True
                self.push_screen(ProjectPicker(projects), self._on_project_picked)
                if self.details_summary:
                    self.details_summary.update("No project selected yet. Please pick a project.")
        except Exception:
            pass

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
            table = self._artifacts.list_artifacts_table(job_id)
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
            chosen = self._artifacts.choose_artifact(job_id, selector)
            if not chosen:
                if self.details_artifacts:
                    self.details_artifacts.update("No suitable artifact found (JSON/CSV)")
                return
            url = chosen.get('presigned_url') or chosen.get('url')
            if not url:
                if self.details_artifacts:
                    self.details_artifacts.update("Artifact has no URL. Try 'jobs download'.")
                return
            content = self._artifacts.fetch_bytes(url, timeout=15)
            content_type = ''
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
                preview = self._artifacts.preview_json(content, filename)
                if self.details_artifacts:
                    self.details_artifacts.update(preview)
                return
            # CSV
            if 'text/csv' in content_type or filename.lower().endswith('.csv'):
                preview = self._artifacts.preview_csv(content, filename)
                if self.details_artifacts:
                    self.details_artifacts.update(preview)
                return
            # Fallback
            if self.details_artifacts:
                self.details_artifacts.update("Unsupported inline preview. Use 'Artifacts: Open Primary' or 'Jobs: Download'.")
        except Exception as e:
            if self.details_artifacts:
                self.details_artifacts.update(f"[red]Artifact preview failed: {e}[/red]")

    def _cmd_artifact_open_primary(self) -> None:
        job = self.selected_job
        if not job:
            if self.details_summary:
                self.details_summary.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            if self.details_summary:
                self.details_summary.update("Invalid job id")
            return
        try:
            data = self._run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
            artifacts = data.get("artifacts") if isinstance(data, dict) else []
            url = None
            if isinstance(artifacts, list):
                chosen = next((a for a in artifacts if isinstance(a, dict) and a.get("primary")), None)
                if not chosen:
                    for pref in ("pdb", "sdf", "zip", "primary"):
                        chosen = next((a for a in artifacts if isinstance(a, dict) and pref in str(a.get("artifact_type") or a.get("type") or "").lower()), None)
                        if chosen:
                            break
                if chosen:
                    url = chosen.get("presigned_url") or chosen.get("url")
            if url:
                webbrowser.open(url)
                if self.details_summary:
                    self.details_summary.update("Opening primary artifact in browser...")
            else:
                if self.details_summary:
                    self.details_summary.update("No suitable artifact URL found.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Open primary failed: {e}[/red]")

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
        self.query_input: Input | None = None
        self.list_view: ListView | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            self.query_input = Input(placeholder="Type to filter commands… (Esc to close)")
            yield self.query_input
        self.list_view = ListView()
        yield self.list_view

    def on_mount(self) -> None:
        self._refresh_list()
        if self.query_input:
            self.query_input.focus()
        # Ensure the first item is highlighted for immediate arrow/enter usage
        if self.list_view and len(self.list_view.children) > 0:
            try:
                self.list_view.index = 0  # type: ignore[attr-defined]
            except Exception:
                pass

    def _refresh_list(self) -> None:
        if not self.list_view:
            return
        self.list_view.clear()
        for cmd_id, name, desc in self._filtered:
            self.list_view.append(ListItem(Static(f"[b]{name}[/b]\n[dim]{desc}[/dim]")))
        # Keep cursor at top after refresh so Enter selects the first item
        try:
            if len(self._filtered) > 0 and self.list_view:
                self.list_view.index = 0  # type: ignore[attr-defined]
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:  # type: ignore[override]
        if event.input is not self.query_input:
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
        # Esc closes the palette
        if event.key == "escape":
            self.dismiss(None)
            return
        # Arrow keys navigate the list even when focus is in the query input
        if event.key in ("down", "up") and self.list_view:
            try:
                self.list_view.focus()
                if event.key == "down":
                    self.list_view.action_cursor_down()  # type: ignore[attr-defined]
                else:
                    self.list_view.action_cursor_up()  # type: ignore[attr-defined]
                event.stop()
            except Exception:
                pass
            return
        # Enter selects the current item
        if event.key == "enter":
            try:
                if self.list_view and len(self._filtered) > 0:
                    # If focus is on list, trigger selection; otherwise, pick current index (default 0)
                    if self.list_view.has_focus:
                        self.list_view.action_select_cursor()  # type: ignore[attr-defined]
                    else:
                        idx = getattr(self.list_view, "index", 0)  # type: ignore[attr-defined]
                        idx = 0 if idx is None else idx
                        if 0 <= idx < len(self._filtered):
                            self.dismiss(self._filtered[idx][0])
                        else:
                            self.dismiss(None)
                    event.stop()
            except Exception:
                pass


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


class FiltersScreen(ModalScreen[Optional[Dict[str, str]]]):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: Dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Jobs Filters (leave blank to skip)")
            for label, key in [
                ("Status", "status"),
                ("Tool", "tool"),
                ("Project ID", "project-id"),
                ("Created After (ISO)", "created-after"),
                ("Created Before (ISO)", "created-before"),
                ("Sort By (created_at|status|job_type)", "sort-by"),
                ("Sort Order (asc|desc)", "sort-order"),
            ]:
                yield Static(label)
                inp = Input()
                self.inputs[key] = inp
                yield inp
            yield Static("Limit (default 50)")
            limit_inp = Input()
            self.inputs["limit"] = limit_inp
            yield limit_inp
            yield Static("Offset (default 0)")
            offset_inp = Input()
            self.inputs["offset"] = offset_inp
            yield offset_inp
            yield Static("Press Enter to apply; Esc to cancel", classes="muted")

    def on_mount(self) -> None:
        # Focus first field
        if self.inputs:
            first = next(iter(self.inputs.values()))
            first.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        # When any input submits, collect all values and dismiss
        values: Dict[str, str] = {}
        for k, inp in self.inputs.items():
            val = (inp.value or "").strip()
            if val:
                values[k] = val
        self.dismiss(values or None)

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


class ProjectPicker(ModalScreen[Optional[str]]):
    def __init__(self, projects: List[Dict[str, Any]]):
        super().__init__()
        self._projects = projects
        self._list: ListView | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Select a Project (Enter to confirm, Esc to cancel)")
            self._list = ListView()
            # Populate
            for p in self._projects:
                pid = str(p.get('project_id') or p.get('id') or '')
                name = str(p.get('name') or pid or 'Unnamed')
                self._list.append(ListItem(Static(f"[b]{name}[/b]  [dim]{pid}[/dim]")))
            yield self._list

    def on_mount(self) -> None:
        if self._list:
            self._list.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
        index = event.index
        if 0 <= index < len(self._projects):
            pid = str(self._projects[index].get('project_id') or self._projects[index].get('id') or '')
            self.dismiss(pid or None)
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)




