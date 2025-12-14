import json

import ui.gatewise_ui as gw
from ui.gatewise_ui import GateWiseUI


def test_save_and_load_users(qtbot):
    ui = GateWiseUI()
    qtbot.addWidget(ui)

    ui.users = [{'uid': '1001', 'name': 'Alice', 'isAdmin': False}]
    ui.save_users()

    with open('users.json', 'r') as f:
        data = json.load(f)

    assert data == ui.users


def test_blackout_save_and_load(qtbot):
    ui1 = GateWiseUI()
    qtbot.addWidget(ui1)

    ui1.add_time_block('Monday', '04:00', '05:00')
    ui1.save_blackout_schedule()

    with open('blackout.json', 'r') as f:
        data = json.load(f)

    assert 'Monday' in data
    assert any(b['start'] == '04:00' for b in data['Monday'])

    ui2 = GateWiseUI()
    qtbot.addWidget(ui2)
    # The second instance should load the file on init
    assert len(ui2.blackout_blocks['Monday']) >= 1


def test_request_password_shows_settings(qtbot, monkeypatch):
    # Replace the PasswordDialog with a fake that returns the admin password
    class FakeDlg:
        def exec_(self):
            return True

        def get_password(self):
            return 'admin'

    monkeypatch.setattr(gw, 'PasswordDialog', lambda parent=None: FakeDlg())

    ui = GateWiseUI()
    qtbot.addWidget(ui)

    ui.request_password()
    assert ui.stack.currentWidget() is ui.settings_screen
