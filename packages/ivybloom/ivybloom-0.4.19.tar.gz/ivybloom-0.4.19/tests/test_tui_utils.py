from __future__ import annotations

from ivybloom_cli.tui.search import rank_commands
from ivybloom_cli.tui.structure_service import StructureService


def test_rank_commands_basic():
	commands = [
		("refresh", "Refresh", "Reload jobs"),
		("open_external", "Open Artifact", "Open best artifact in browser"),
		("jobs_list", "Jobs: List", "List jobs with optional filters"),
	]
	res = rank_commands(commands, "jo li")
	assert res and res[0][0] == "jobs_list"
	# Empty query returns original list
	assert rank_commands(commands, "") == commands


def test_structure_frame_advances():
	service = StructureService()
	# Minimal two points to render something deterministic-ish
	points = [(0.0, 0.0, 0.0), (0.2, 0.2, 0.2)]
	art1, a1 = service.render_frame_advance(points, 0.0, rows=10, cols=20, delta=0.5)
	art2, a2 = service.render_frame_advance(points, a1, rows=10, cols=20, delta=0.5)
	assert a2 > a1
	assert isinstance(art1, str) and isinstance(art2, str)

