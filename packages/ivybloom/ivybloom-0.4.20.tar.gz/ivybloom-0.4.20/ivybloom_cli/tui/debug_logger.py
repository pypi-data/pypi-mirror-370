from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional


class DebugLogger:
    """Lightweight stderr logger for the TUI that prints behind the UI.

    Enabled via config (debug=true). Messages are flushed immediately to stderr
    so they appear in the terminal scrollback while the Textual app runs.
    """

    def __init__(self, enabled: bool = False, prefix: str = "TUI") -> None:
        self._enabled = bool(enabled)
        self._prefix = prefix

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def debug(self, message: str) -> None:
        if not self._enabled:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            print(f"[{self._prefix} DEBUG {ts}] {message}", file=sys.__stderr__, flush=True)
        except Exception:
            # Best-effort only
            pass

    def error(self, message: str) -> None:
        if not self._enabled:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            print(f"[{self._prefix} ERROR {ts}] {message}", file=sys.__stderr__, flush=True)
        except Exception:
            pass


