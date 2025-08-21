from __future__ import annotations

import os
import sys
from datetime import datetime


class DebugLogger:
    """Lightweight stderr logger for the TUI that prints behind the UI.

    Enabled via config (debug=true). Writes directly to file descriptor 2 to
    avoid being captured by Textual/Rich and ensure messages appear in the
    terminal scrollback behind the TUI.
    """

    def __init__(self, enabled: bool = False, prefix: str = "TUI") -> None:
        self._enabled = bool(enabled)
        self._prefix = prefix

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def _emit(self, level: str, message: str) -> None:
        if not self._enabled:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{self._prefix} {level} {ts}] {message}\n"
        # Best effort: write directly to stderr FD to bypass any capture
        try:
            os.write(2, line.encode("utf-8", errors="replace"))
            return
        except Exception:
            pass
        # Fallback to sys.__stderr__
        try:
            sys.__stderr__.write(line)
            sys.__stderr__.flush()
        except Exception:
            pass

    def debug(self, message: str) -> None:
        self._emit("DEBUG", message)

    def error(self, message: str) -> None:
        self._emit("ERROR", message)


