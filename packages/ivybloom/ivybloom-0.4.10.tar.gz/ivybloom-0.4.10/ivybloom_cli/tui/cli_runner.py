from __future__ import annotations

from typing import Any, List, Optional
import subprocess
import json

from ..utils.config import Config


class CLIRunner:
	"""Thin wrapper around the installed ivybloom CLI for subprocess calls."""

	def __init__(self, config: Config) -> None:
		self.config = config

	def run_cli_json(self, args: List[str], timeout: int = 30) -> Any:
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

	def run_cli_text(self, args: List[str], timeout: int = 60, input_text: Optional[str] = None) -> str:
		cmd: List[str] = [
			"ivybloom",
			"--config-file",
			str(self.config.config_path),
		] + args
		result = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout)
		if result.returncode != 0:
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		return result.stdout


