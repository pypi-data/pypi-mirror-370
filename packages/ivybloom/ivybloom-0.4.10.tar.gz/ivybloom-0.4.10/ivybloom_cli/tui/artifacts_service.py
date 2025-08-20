from __future__ import annotations

from typing import Any, Dict, List, Optional
import csv
import io
import json
import requests

from rich.table import Table

from ..utils.colors import EARTH_TONES
from .cli_runner import CLIRunner


class ArtifactsService:
	"""Service for listing and previewing artifacts via CLI subprocess + HTTP fetch."""

	def __init__(self, runner: CLIRunner) -> None:
		self.runner = runner

	def list_artifacts_table(self, job_id: str) -> Table:
		data = self.runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
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
		return table

	def choose_artifact(self, job_id: str, selector: Optional[str]) -> Optional[Dict[str, Any]]:
		data = self.runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
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
		return chosen

	def fetch_bytes(self, url: str, timeout: int = 15) -> bytes:
		resp = requests.get(url, timeout=timeout)
		resp.raise_for_status()
		return resp.content

	def preview_json(self, content: bytes, filename: str) -> str | Table:
		max_json_bytes = 200 * 1024
		if len(content) > max_json_bytes:
			return f"JSON too large to preview ({len(content)} bytes). Use Open/Download."
		text = content.decode('utf-8', errors='ignore')
		data_obj = json.loads(text or "")
		if isinstance(data_obj, list) and data_obj and isinstance(data_obj[0], dict):
			cols = list(data_obj[0].keys())[:20]
			table = Table(title=f"JSON Preview: {filename}")
			for c in cols:
				table.add_column(str(c))
			for row in data_obj[:100]:
				table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
			return table
		return json.dumps(data_obj, indent=2)

	def preview_csv(self, content: bytes, filename: str) -> str | Table:
		max_csv_bytes = 500 * 1024
		text = content.decode('utf-8', errors='ignore')
		if len(content) > max_csv_bytes:
			preview = "\n".join(text.splitlines()[:15])
			return preview + "\n[dim](truncated) Use Open/Download[/dim]"
		sample = text[:4096]
		try:
			dialect = csv.Sniffer().sniff(sample)
		except Exception:
			dialect = csv.excel
		reader = csv.reader(io.StringIO(text), dialect)
		rows = list(reader)
		if not rows:
			return "Empty CSV"
		table = Table(title=f"CSV Preview: {filename}")
		header = rows[0]
		for h in header[:20]:
			table.add_column(str(h))
		for r in rows[1:101]:
			table.add_row(*[str(x)[:120] for x in r[:20]])
		return table


