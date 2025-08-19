from __future__ import annotations

from typing import Optional, Dict, Any, List
import webbrowser
import subprocess
import json

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Input, LoadingIndicator
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

        self.filter_text = reactive("")

    def compose(self) -> ComposeResult:
        if self.show_header:
            yield Header()
        with Horizontal():
            with Vertical():
                yield Static("Jobs", classes="panel-title")
                self.filter_input = Input(placeholder="Filter by status/tool/project (e.g. status=running)")
                yield self.filter_input
                self.jobs_table = DataTable(zebra_stripes=True)
                yield self.jobs_table
            with Vertical():
                yield Static("Details", classes="panel-title")
                self.details = Static("Select a job to view details", classes="muted")
                yield self.details
                self.help_panel = Static(
                    "\n".join([
                        "[b]Shortcuts[/b]",
                        " r  – Refresh",
                        " /  – Open command palette",
                        " f  – Focus filter",
                        " o  – Open artifact in external viewer (if available)",
                        " ?  – Toggle this help",
                        " q  – Quit",
                    ]),
                    classes="muted",
                )
                yield self.help_panel
        if self.show_footer:
            yield Footer()

    def on_mount(self) -> None:
        # Configure jobs table columns
        self.jobs_table.clear()
        self.jobs_table.add_columns("Job ID", "Tool", "Status", "Title")
        self.jobs_table.cursor_type = "row"
        self.jobs_table.focus()
        # Hide help by default
        try:
            self.help_panel.display = False  # type: ignore[attr-defined]
        except Exception:
            pass
        # Show splash and load
        self._splash_opened = False  # type: ignore[attr-defined]
        self._show_splash()
        self.call_later(self._load_jobs)

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
            ("focus_filter", "Focus Filter", "Jump to filter input"),
            ("clear_filter", "Clear Filter", "Remove all filters"),
            ("quick_status_running", "Filter: status=running", "Show running jobs"),
            ("quick_status_completed", "Filter: status=completed", "Show completed jobs"),
            ("open_external", "Open Artifact", "Open best artifact in browser"),
            ("toggle_help", "Toggle Help", "Show/hide help panel"),
            ("run_custom", "Run CLI: Custom", "Run arbitrary ivybloom args"),
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
        elif result == "run_tool":
            self.push_screen(PromptScreen("Tool name to run"), lambda tool: self._cmd_run_tool_start(tool))
        elif result == "workflows_run":
            self.push_screen(PromptScreen("Workflow file path"), lambda path: self._cmd_workflows_run_start(path))
        elif result == "run_custom":
            self.push_screen(PromptScreen("Custom args after 'ivybloom'", placeholder="e.g. jobs list --status running"), lambda extra: self._cmd_run_custom(extra))
        elif result == "refresh":
            self.action_refresh()
        elif result == "focus_filter":
            self.action_focus_filter()
        elif result == "clear_filter":
            self.filter_input.value = ""
            self.on_input_changed(Input.Changed(self.filter_input, ""))  # type: ignore[arg-type]
        elif result == "quick_status_running":
            self.filter_input.value = "status=running"
            self.on_input_changed(Input.Changed(self.filter_input, self.filter_input.value))  # type: ignore[arg-type]
        elif result == "quick_status_completed":
            self.filter_input.value = "status=completed"
            self.on_input_changed(Input.Changed(self.filter_input, self.filter_input.value))  # type: ignore[arg-type]
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
            self.details.update(table)
        except Exception as e:
            self.details.update(f"[red]Failed to load tools: {e}[/red]")

    

    def _apply_filter(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        text = self.filter_text.strip()
        if not text:
            return jobs
        parts = [p.strip() for p in text.split() if p.strip()]
        filters: Dict[str, str] = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                filters[k.lower()] = v.lower()
        def _match(job: Dict[str, Any]) -> bool:
            for k, v in filters.items():
                if k == "status" and v not in str(job.get("status", "")).lower():
                    return False
                if k in {"tool", "tool_name", "job_type"}:
                    value = str(job.get("tool_name") or job.get("job_type") or "").lower()
                    if v not in value:
                        return False
                if k in {"project", "project_id"}:
                    value = str(job.get("project_id", "")).lower()
                    if v not in value:
                        return False
            return True
        return [j for j in jobs if _match(j)]

    async def _load_jobs(self) -> None:
        self.jobs_table.clear()
        try:
            # Thin wrapper: call CLI for jobs list
            args: List[str] = ["jobs", "list", "--format", "json"]
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
            self.details.update(f"[red]Failed to load jobs: {e}[/red]")
        finally:
            self._hide_splash()

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
        parts: List[str] = []
        parts.append(f"[b]Job ID:[/b] {job.get('job_id') or job.get('id')}")
        parts.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
        parts.append(f"[b]Status:[/b] {job.get('status')}")
        title = job.get('job_title') or job.get('title')
        if title:
            parts.append(f"[b]Title:[/b] {title}")
        project = job.get('project_id')
        if project:
            parts.append(f"[b]Project:[/b] {project}")
        # Minimal visualization hints
        tool = (job.get('tool_name') or job.get('job_type') or '').lower()
        if tool in {"esmfold", "alphafold"}:
            parts.append("[b]Protein:[/b] structure prediction task (view artifacts via jobs download)")
        if tool in {"diffdock", "reinvent", "admetlab3"}:
            parts.append("[b]Compound:[/b] molecular/docking/design task")
        status = (job.get('status') or '').lower()
        if status in {"completed", "success"}:
            parts.append("[dim]Hint: press 'o' to open available artifacts externally[/dim]")
        self.details.update("\n".join(parts))

    def action_refresh(self) -> None:
        self.call_later(self._load_jobs)

    def action_focus_filter(self) -> None:
        self.filter_input.focus()

    def on_input_changed(self, event: Input.Changed) -> None:  # type: ignore[override]
        if event.input is self.filter_input:
            self.filter_text = event.value
            # Re-render table using local filter without refetch
            self.jobs_table.clear()
            for job in self._apply_filter(self.jobs):
                self.jobs_table.add_row(
                    str(job.get("job_id") or job.get("id") or ""),
                    str(job.get("tool_name") or job.get("job_type") or ""),
                    str(job.get("status", "")),
                    str(job.get("job_title") or job.get("title") or ""),
                )

    def action_toggle_help(self) -> None:
        try:
            self.help_panel.display = not getattr(self.help_panel, "display", False)  # type: ignore[attr-defined]
        except Exception:
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
                atype = str(art.get("artifact_type") or art.get("type") or "").lower()
                if url and (any(t in atype for t in ["pdb", "sdf", "primary", "zip"])):
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
                self.details.update(self.details.renderable + "\n[dim]Opening artifact in browser...[/dim]")
            else:
                self.details.update(self.details.renderable + f"\n[dim]No artifact URLs found. Try 'ivybloom jobs download {job_id}'.[/dim]")
        except Exception as e:
            self.details.update(self.details.renderable + f"\n[red]Open failed: {e}[/red]")

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
            self.details.update(text or "No projects found")
        except Exception as e:
            self.details.update(f"[red]Projects list failed: {e}[/red]")

    async def _cmd_account_info(self) -> None:
        try:
            text = self._run_cli_text(["account", "info"]) or ""
            self.details.update(text or "No account info")
        except Exception as e:
            self.details.update(f"[red]Account info failed: {e}[/red]")

    def _cmd_tools_info(self, tool: Optional[str]) -> None:
        if not tool:
            return
        try:
            text = self._run_cli_text(["tools", "info", tool, "--format", "table"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Tool info failed: {e}[/red]")

    def _cmd_tools_schema(self, tool: Optional[str]) -> None:
        if not tool:
            return
        try:
            text = self._run_cli_text(["tools", "schema", tool, "--format", "table"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Tool schema failed: {e}[/red]")

    def _cmd_tools_completions(self, tool: Optional[str]) -> None:
        if not tool:
            return
        try:
            text = self._run_cli_text(["tools", "completions", tool, "--format", "table"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Tool completions failed: {e}[/red]")

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
            self.details.update(f"[dim]Loaded {len(jobs)} jobs[/dim]")
        except Exception as e:
            self.details.update(f"[red]Jobs list failed: {e}[/red]")

    def _cmd_jobs_status(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            text = self._run_cli_text(["jobs", "status", job_id, "--format", "table"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Jobs status failed: {e}[/red]")

    def _cmd_jobs_results(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            text = self._run_cli_text(["jobs", "results", job_id, "--format", "json"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Jobs results failed: {e}[/red]")

    def _cmd_jobs_download(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            # default to list-only to avoid writing files implicitly
            text = self._run_cli_text(["jobs", "download", job_id, "--list-only", "--format", "table"]) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Jobs download failed: {e}[/red]")

    def _cmd_jobs_cancel(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            # auto-confirm cancellation to avoid interactive prompt
            text = self._run_cli_text(["jobs", "cancel", job_id], input_text="y\n") or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Jobs cancel failed: {e}[/red]")

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
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Run tool failed: {e}[/red]")

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
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Workflows run failed: {e}[/red]")

    def _cmd_run_custom(self, extra: Optional[str]) -> None:
        import shlex
        if not extra:
            return
        try:
            args = shlex.split(extra)
            text = self._run_cli_text(args, timeout=600) or ""
            self.details.update(text)
        except Exception as e:
            self.details.update(f"[red]Custom command failed: {e}[/red]")


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




