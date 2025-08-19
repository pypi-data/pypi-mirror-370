from __future__ import annotations

from typing import Optional, Dict, Any, List
import webbrowser

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
from ..client.api_client import IvyBloomAPIClient


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
        self._client: Optional[IvyBloomAPIClient] = None
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
        self.jobs_table.clear(columns=True)
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
            ("list_tools", "List Tools", "Show available tools in a table"),
            ("refresh", "Refresh", "Reload jobs"),
            ("focus_filter", "Focus Filter", "Jump to filter input"),
            ("clear_filter", "Clear Filter", "Remove all filters"),
            ("quick_status_running", "Filter: status=running", "Show running jobs"),
            ("quick_status_completed", "Filter: status=completed", "Show completed jobs"),
            ("open_external", "Open Artifact", "Open best artifact in browser"),
            ("toggle_help", "Toggle Help", "Show/hide help panel"),
        ]
        self.push_screen(CommandPalette(commands), self._on_palette_result)

    def _on_palette_result(self, result: Optional[str]) -> None:
        if not result:
            return
        if result == "list_tools":
            self.call_later(self._show_tools)
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
            client = self._ensure_client()
            tools = client.list_tools(verbose=False) or []
            table = Table(title="Available Tools", show_lines=False, show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}", box=box.SIMPLE_HEAVY)
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Description", style="white")
            for t in tools:
                if not isinstance(t, dict):
                    continue
                table.add_row(str(t.get("id") or t.get("name") or ""), str(t.get("name") or t.get("id") or ""), str(t.get("description") or ""))
            self.details.update(table)
        except Exception as e:
            self.details.update(f"[red]Failed to load tools: {e}[/red]")

    def _ensure_client(self) -> IvyBloomAPIClient:
        if self._client is None:
            self._client = IvyBloomAPIClient(self.config, self.auth_manager)
        return self._client

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
        self.jobs_table.clear(rows=True)
        try:
            client = self._ensure_client()
            filters: Dict[str, Any] = {}
            if self.initial_project_id:
                filters["project_id"] = self.initial_project_id
            jobs = client.list_jobs(**filters) or []
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
            self.jobs_table.clear(rows=True)
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
            client = self._ensure_client()
            urls = client.get_job_download_urls(job_id)
            # Find a preferable artifact URL
            candidate_urls: List[str] = []
            if isinstance(urls, dict):
                for key, value in urls.items():
                    if not value:
                        continue
                    if isinstance(value, str):
                        key_l = str(key).lower()
                        if any(t in key_l for t in ["pdb", "sdf", "primary", "zip"]):
                            candidate_urls.append(value)
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str):
                                candidate_urls.append(v)
            if candidate_urls:
                webbrowser.open(candidate_urls[0])
                self.details.update(self.details.renderable + "\n[dim]Opening artifact in browser...[/dim]")
            else:
                self.details.update(self.details.renderable + "\n[dim]No artifact URLs found. Try 'ivybloom jobs download {job_id}'.[/dim]")
        except Exception as e:
            self.details.update(self.details.renderable + f"\n[red]Open failed: {e}[/red]")


class CommandPalette(ModalScreen[Optional[str]]):
    def __init__(self, commands: List[tuple[str, str, str]]):
        super().__init__()
        self._all_commands = commands
        self._filtered = commands
        self.query: Input | None = None
        self.list_view: ListView | None = None

    def compose(self) -> ComposeResult:
        container = Vertical()
        self.query = Input(placeholder="Type to filter commands… (Esc to close)")
        container.mount(self.query)
        self.list_view = ListView()
        container.mount(self.list_view)
        yield container

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


class SplashScreen(ModalScreen[None]):
    def __init__(self, title: str = "IvyBloom", subtitle: str = "Loading…"):
        super().__init__()
        self._title = title
        self._subtitle = subtitle

    def compose(self) -> ComposeResult:
        container = Vertical(classes="splash")
        ascii_logo = "\n".join([
            "  ____      __     ____  _                          ",
            " |_  /___  / /__  / __ )(_)___  ____  ____ _      __",
            "  / // _ \\/ / _ \\/ __  / / __ \\_/ __ \\/ __ \\ | /| / /",
            " /___/\\___/_/\\___/_/ /_/_/_/ /_(_) /_/ / /_/ / |/ |/ / ",
            "                                 /____/\\____/|__/|__/  ",
        ])
        container.mount(Static(f"[b]{self._title}[/b]", classes="panel-title"))
        container.mount(Static(ascii_logo))
        container.mount(LoadingIndicator())
        container.mount(Static(f"[dim]{self._subtitle}[/dim]", classes="muted"))
        yield container

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)




