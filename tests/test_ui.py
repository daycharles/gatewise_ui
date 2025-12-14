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


def test_blackout_back_button_navigates_to_settings(qtbot):
    """Test that the back button in blackout screen navigates to settings screen."""
    ui = GateWiseUI()
    qtbot.addWidget(ui)

    # Navigate to settings, then blackout
    ui.show_settings()
    assert ui.stack.currentWidget() is ui.settings_screen
    
    ui.show_blackout()
    assert ui.stack.currentWidget() is ui.blackout_screen
    
    # Find and click the back button in blackout screen
    back_button = None
    for child in ui.blackout_screen.findChildren(gw.QPushButton):
        if child.text() == "Back":
            back_button = child
            break
    
    assert back_button is not None, "Back button not found in blackout screen"
    back_button.click()
    
    # Should navigate back to settings screen
    assert ui.stack.currentWidget() is ui.settings_screen


def test_save_blackout_navigates_to_settings(qtbot, monkeypatch):
    """Test that saving blackout schedule navigates back to settings screen."""
    ui = GateWiseUI()
    qtbot.addWidget(ui)

    # Mock QMessageBox to avoid blocking
    monkeypatch.setattr(gw.QMessageBox, 'information', lambda *args, **kwargs: None)

    # Navigate to blackout screen
    ui.show_blackout()
    assert ui.stack.currentWidget() is ui.blackout_screen
    
    # Save the schedule
    ui.save_blackout_schedule()
    
    # Should navigate back to settings screen
    assert ui.stack.currentWidget() is ui.settings_screen


def test_all_back_buttons_work_correctly(qtbot):
    """Test that all back buttons navigate to the correct screens."""
    ui = GateWiseUI()
    qtbot.addWidget(ui)
    
    # Test settings -> main
    ui.show_settings()
    assert ui.stack.currentWidget() is ui.settings_screen
    back_btn = None
    for child in ui.settings_screen.findChildren(gw.QPushButton):
        if child.text() == "Back":
            back_btn = child
            break
    if back_btn:
        back_btn.click()
        assert ui.stack.currentWidget() is ui.main_screen
    
    # Test log -> main
    ui.show_logs()
    assert ui.stack.currentWidget() is ui.log_screen
    back_btn = None
    for child in ui.log_screen.findChildren(gw.QPushButton):
        if child.text() == "Back":
            back_btn = child
            break
    if back_btn:
        back_btn.click()
        assert ui.stack.currentWidget() is ui.main_screen
    
    # Test user management -> settings
    ui.show_user_management()
    assert ui.stack.currentWidget() is ui.user_screen
    back_btn = None
    for child in ui.user_screen.findChildren(gw.QPushButton):
        if child.text() == "Back":
            back_btn = child
            break
    if back_btn:
        back_btn.click()
        assert ui.stack.currentWidget() is ui.settings_screen

