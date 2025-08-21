from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
import webbrowser
import json

try:
    from textual.app import App, ComposeResult
except Exception:
    # Fallback for older Textual versions without ComposeResult type
    from textual.app import App  # type: ignore
    ComposeResult = object  # type: ignore
from textual.widgets import Header, Footer, DataTable, Static, Input, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical
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
from .screens import CommandPalette, PromptScreen, FiltersScreen, SplashScreen, ProjectPicker, HistorySelectScreen
from .views import JobsView, DetailsView
from .history import HistoryManager


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
        ("ctrl+k", "open_palette", "Commands"),
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
        self._history = HistoryManager(self.config)

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
        self.cmd_input = Input(placeholder="Type '/' or Ctrl+K for palette. Enter commands like 'jobs list --status running' (no 'ivybloom' needed).")
        yield self.cmd_input
        self.status_bar = Static("", classes="muted")
        yield self.status_bar
        if self.show_footer:
            yield Footer()

    # ------------------ Readiness / gating ------------------
    def _is_ready(self) -> bool:
        try:
            if getattr(self, "_splash_opened", False):
                return False
        except Exception:
            pass
        if getattr(self, "_picker_open", False):
            return False
        if not self.initial_project_id:
            return False
        try:
            return self.auth_manager.is_authenticated()
        except Exception:
            return False

    def _require_ready(self) -> bool:
        if self._is_ready():
            return True
        if self.details_summary:
            self.details_summary.update("[yellow]Complete authentication and project selection to continue…[/yellow]")
        return False

    def on_mount(self) -> None:
        # Configure jobs table columns (dense)
        self.jobs_table.clear()
        self.jobs_table.add_columns("Job ID", "Tool", "Status", "Result")
        self.jobs_table.cursor_type = "row"
        self.jobs_table.focus()
        # Initialize view helpers once widgets exist
        self._jobs_view = JobsView(self.jobs_table, self._jobs)
        self._details_view = DetailsView(self.details_summary, self.details_params, self.details_artifacts, self._artifacts)
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
        if not self._require_ready():
            return
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
            ("run_custom", "Run: CLI (Custom)", "Run arbitrary ivybloom args; supports unknown flags"),
            ("run_history", "Run: History", "View and re-run recent custom commands"),
            ("run_history_clear", "Run: History (Clear)", "Clear custom run history"),
            ("refresh", "Refresh", "Reload jobs"),
            ("jobs_load_more", "Jobs: Load More", "Fetch next page (50)"),
            ("focus_filter", "Focus Filter", "Jump to filter input"),
            ("clear_filter", "Clear Filter", "Remove all filters"),
            ("quick_status_running", "Filter: status=running", "Show running jobs"),
            ("quick_status_completed", "Filter: status=completed", "Show completed jobs"),
            ("open_external", "Open Artifact", "Open best artifact in browser"),
            ("toggle_help", "Toggle Help", "Show/hide help panel"),
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
            # Two-step helper: first enter the full command tail, then optional extra env overrides
            def _after_args(extra: Optional[str]):
                def _after_env(env_kv: Optional[str]):
                    # Allow entering comma-separated KEY=VAL pairs to inject into subprocess env if needed
                    env_map = {}
                    if env_kv:
                        try:
                            for pair in (env_kv or "").split(","):
                                if "=" in pair:
                                    k, v = pair.split("=", 1)
                                    if k.strip():
                                        env_map[k.strip()] = v.strip()
                        except Exception:
                            pass
                    # Persist these overrides for the TUI session
                    try:
                        self._runner.set_session_env_overrides(env_map)
                    except Exception:
                        pass
                    self._cmd_run_custom(extra, env_overrides=env_map)
                self.push_screen(PromptScreen("Env overrides (KEY=VAL,KEY=VAL) [optional]", placeholder="optional"), _after_env)
            self.push_screen(PromptScreen("Custom args after 'ivybloom'", placeholder="e.g. jobs list --status running --flagX"), _after_args)
        elif result == "run_history":
            entries = self._history.list_entries()
            if not entries:
                if self.details_summary:
                    self.details_summary.update("No history available.")
                return
            self.push_screen(HistorySelectScreen(entries[:50]), lambda idx: self._on_history_pick(str(idx) if idx is not None else None))
        elif result == "run_history_clear":
            try:
                self._history.clear()
                if self.details_summary:
                    self.details_summary.update("History cleared.")
            except Exception as e:
                if self.details_summary:
                    self.details_summary.update(f"[red]Failed to clear history: {e}[/red]")
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
        if not self._is_ready():
            return
        self.jobs_offset = 0
        self.jobs_table.clear()
        try:
            jobs = self._jobs_view.load_initial(self.initial_project_id)
            self.jobs = jobs
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Failed to load jobs: {e}[/red]")
        finally:
            self._hide_splash()

    def _cmd_jobs_load_more(self) -> None:
        if not self._require_ready():
            return
        # Fetch next page and append
        try:
            self.jobs_offset += self.jobs_limit
            new_jobs = self._jobs_view.load_more(self.initial_project_id)
            self.jobs.extend(new_jobs)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Load more failed: {e}[/red]")
        finally:
            self._update_status_bar()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:  # type: ignore[override]
        if not self._is_ready():
            return
        try:
            row_key = event.row_key
            row_index = self.jobs_table.get_row_index(row_key)
            # Using JobsView for selection mapping
            selected = None
            if 0 <= row_index:
                selected = self._jobs_view.get_selected_job(row_index)
            if selected:
                self.selected_job = selected
                self._render_details(selected)
        except Exception:
            pass

    def _render_details(self, job: Dict[str, Any]) -> None:
        # Delegate to details view helpers
        if self.details_summary and self.details_params and self.details_artifacts:
            self._details_view.render_summary(job)
            self._details_view.render_params(job)
            self._details_view.render_artifacts(job)

    def action_refresh(self) -> None:
        if not self._require_ready():
            return
        self.call_later(self._load_jobs)

    def action_focus_filter(self) -> None:
        if self.cmd_input:
            self.cmd_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        if self.cmd_input and event.input is self.cmd_input:
            if not self._require_ready():
                return
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
        if not self._require_ready():
            return
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

    def _cmd_run_custom(self, extra: Optional[str], env_overrides: Optional[Dict[str, str]] = None) -> None:
        import shlex
        if not extra:
            return
        try:
            args = shlex.split(extra)
            # Allow users to paste full commands starting with 'ivybloom' or python -m entrypoint
            if args:
                if args[0] in {"ivybloom", "ivybloom-cli"}:
                    args = args[1:]
                elif len(args) >= 3 and args[0].lower().startswith("python") and args[1] == "-m" and args[2] in {"ivybloom_cli.main", "ivybloom_cli"}:
                    args = args[3:]
            # Pass env overrides down to the runner for this invocation
            text = self._runner.run_cli_text(args, timeout=600, env_overrides=env_overrides) or ""
            # Persist to history
            try:
                self._history.add_entry(extra, env_overrides or {})
            except Exception:
                pass
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Custom command failed: {e}[/red]")

    def _on_history_pick(self, idx: Optional[str]) -> None:
        try:
            n = int((idx or "0").strip())
        except Exception:
            n = 0
        entries = self._history.list_entries()
        if not entries:
            return
        if n < 0 or n >= len(entries):
            n = 0
        entry = entries[n]
        self._cmd_run_custom(entry.get("args", ""), env_overrides=entry.get("env") or {})

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
            self._structure_points = self._structure.parse_pdb_ca(pdb_text)
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

    def _render_ascii_frame(self) -> None:
        if not self.details_structure:
            return
        if not self._structure_points:
            self.details_structure.update("No structure loaded")
            return
        # Grid using StructureService
        rows, cols = 30, 80
        art, next_angle = self._structure.render_frame_advance(self._structure_points, self._structure_angle, rows=rows, cols=cols, delta=0.12)
        self._structure_angle = next_angle
        self.details_structure.update(art)
