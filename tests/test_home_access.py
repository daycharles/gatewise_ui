"""
Basic tests for the home access control system.
"""

import os
import sys
import json
import tempfile
import shutil

# Set environment variables before imports
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['GATEWISE_ADMIN_PASSWORD'] = 'test_password_123'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_garage_controller_import():
    """Test that garage controller can be imported."""
    from core.garage import GarageController, get_garage_controller
    
    controller = get_garage_controller()
    assert controller is not None
    # GPIO won't be available in CI, so just check it initializes
    assert hasattr(controller, 'enabled')
    assert hasattr(controller, 'trigger_door')
    print("✓ Garage controller import test passed")


def test_ui_classes_import():
    """Test that UI classes can be imported."""
    from ui.gatewise_ui import GateWiseUI, PasswordDialog, UserDialog
    
    assert GateWiseUI is not None
    assert PasswordDialog is not None
    assert UserDialog is not None
    print("✓ UI classes import test passed")


def test_admin_password_from_env():
    """Test that admin password is read from environment variable."""
    from PyQt5.QtWidgets import QApplication
    from ui.gatewise_ui import GateWiseUI
    
    # Get existing app or create new one
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = GateWiseUI()
    
    # Check that password is loaded from environment
    assert window.admin_password == 'test_password_123'
    
    print("✓ Admin password from environment test passed")


def test_garage_controller_singleton():
    """Test that garage controller returns same instance."""
    from core.garage import get_garage_controller
    
    controller1 = get_garage_controller()
    controller2 = get_garage_controller()
    
    assert controller1 is controller2
    print("✓ Garage controller singleton test passed")


def test_user_persistence():
    """Test that user data can be saved and loaded."""
    from PyQt5.QtWidgets import QApplication
    from ui.gatewise_ui import GateWiseUI
    
    # Create temp directory for test files
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # Get existing app or create new one
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = GateWiseUI()
        
        # Add a test user
        test_user = {
            "uid": "123456",
            "name": "Test User",
            "isAdmin": False
        }
        window.users = [test_user]
        window.save_users()
        
        # Check file was created
        assert os.path.exists("users.json")
        
        # Read back and verify
        with open("users.json", "r") as f:
            loaded_users = json.load(f)
        
        assert len(loaded_users) == 1
        assert loaded_users[0]["uid"] == "123456"
        assert loaded_users[0]["name"] == "Test User"
        
        print("✓ User persistence test passed")
    
    finally:
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)


def test_ui_initialization():
    """Test that UI initializes without errors."""
    from PyQt5.QtWidgets import QApplication
    from ui.gatewise_ui import GateWiseUI
    
    # Get existing app or create new one
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = GateWiseUI()
    
    # Check that all screens are initialized
    assert window.main_screen is not None
    assert window.settings_screen is not None
    assert window.log_screen is not None
    assert window.blackout_screen is not None
    assert window.user_screen is not None
    assert window.garage_screen is not None
    
    # Check that garage controller is initialized
    assert window.garage_controller is not None
    
    print("✓ UI initialization test passed")


if __name__ == "__main__":
    print("\n=== Running Home Access Control Tests ===\n")
    
    test_garage_controller_import()
    test_ui_classes_import()
    test_admin_password_from_env()
    test_garage_controller_singleton()
    test_user_persistence()
    test_ui_initialization()
    
    print("\n=== All tests passed! ===\n")
