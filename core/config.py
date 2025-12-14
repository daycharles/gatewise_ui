"""Simple config helpers used by the GateWise UI.

These helpers are intentionally small and file-based so tests and the UI
can load/save JSON without pulling in a larger config system.
"""
import json
from pathlib import Path


def load_json(path, default=None):
	p = Path(path)
	if not p.exists():
		return default
	try:
		with p.open('r', encoding='utf-8') as f:
			return json.load(f)
	except Exception:
		return default


def save_json(path, data):
	p = Path(path)
	p.parent.mkdir(parents=True, exist_ok=True)
	with p.open('w', encoding='utf-8') as f:
		json.dump(data, f, indent=4)

