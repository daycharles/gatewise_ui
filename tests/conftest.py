import sys
import types

from PyQt5.QtWidgets import QCheckBox

# Provide a lightweight fake `mfrc522` module so tests can import the UI
if 'mfrc522' not in sys.modules:
    mfrc = types.ModuleType('mfrc522')
    class SimpleMFRC522:
        def read(self):
            return (12345678, None)
    mfrc.SimpleMFRC522 = SimpleMFRC522
    sys.modules['mfrc522'] = mfrc

# Now import the UI and patch missing pieces before tests run
import ui.gatewise_ui as gw


class Toggle(QCheckBox):
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)


# Ensure Toggle exists and don't block on real network calls
gw.Toggle = Toggle

def _noop_push(self):
    return None

gw.GateWiseUI.push_to_door_modules = _noop_push

def _toggle_auto_sync(self, state):
    # simple state handler used by the UI
    self.auto_sync_enabled = bool(state)

gw.GateWiseUI.toggle_auto_sync = _toggle_auto_sync

# Ensure instances have a default `auto_sync_enabled` attribute
gw.GateWiseUI.auto_sync_enabled = False


import pytest


@pytest.fixture(autouse=True)
def isolate_cwd(tmp_path, monkeypatch):
    """Run each test in an isolated temporary cwd so JSON files don't leak."""
    monkeypatch.chdir(tmp_path)
    yield
