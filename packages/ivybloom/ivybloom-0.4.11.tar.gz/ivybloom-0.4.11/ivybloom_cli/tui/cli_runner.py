from __future__ import annotations

from typing import Any, List, Optional, Iterator
import subprocess
import json
import sys
import shutil
import os

from ..utils.config import Config


class CLIRunner:
	"""Thin wrapper around the installed ivybloom CLI for subprocess calls."""

	def __init__(self, config: Config) -> None:
		self.config = config

	def run_cli_json(self, args: List[str], timeout: int = 30) -> Any:
		cmd: List[str] = self._build_cmd(args)
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
		cmd: List[str] = self._build_cmd(args)
		result = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout)
		if result.returncode != 0:
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		return result.stdout

	def _build_cmd(self, args: List[str]) -> List[str]:
		# Prefer installed entrypoint if available in PATH, else fallback to in-process interpreter
		base: List[str]
		if shutil.which("ivybloom"):
			base = ["ivybloom"]
		else:
			base = [sys.executable, "-m", "ivybloom_cli.main"]
		cmd: List[str] = base[:]
		# Include config file only if present to avoid passing 'None'
		config_path = getattr(self.config, "config_path", None)
		if config_path:
			try:
				path_str = str(config_path)
				if path_str:
					cmd += ["--config-file", path_str]
			except Exception:
				pass
		return cmd + args

	def run_cli_stream(self, args: List[str], input_text: Optional[str] = None) -> Iterator[str]:
		cmd: List[str] = self._build_cmd(args)
		proc = subprocess.Popen(cmd, stdin=subprocess.PIPE if input_text else None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
		try:
			if input_text and proc.stdin:
				proc.stdin.write(input_text)
				proc.stdin.flush()
				proc.stdin.close()
			assert proc.stdout is not None
			for line in proc.stdout:
				yield line.rstrip("\n")
			proc.wait()
		finally:
			try:
				proc.kill()
			except Exception:
				pass


