import sys
import os
import json
import threading
from datetime import datetime
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QSizePolicy, QStackedWidget, QLineEdit, QDialog,
    QDialogButtonBox, QGridLayout, QComboBox, QScrollArea, QGroupBox, QTimeEdit,
    QMessageBox, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QTime
from core.config import get_config

# Load configuration
config = get_config()

# Try to import RFID reader, use mock if not available
reader = None
if config.rfid_enabled:
    try:
        from mfrc522 import SimpleMFRC522
        reader = SimpleMFRC522()
        print("[INFO] RFID reader initialized")
    except ImportError:
        print("[WARNING] mfrc522 library not available, RFID features disabled")
    except Exception as e:
        print(f"[WARNING] Failed to initialize RFID reader: {e}")

DOOR_MODULE_IPS = config.door_module_ips
DOOR_MODULE_PORT = config.door_module_port

# Try to import RFID reader - will fail on systems without hardware
try:
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
    RFID_AVAILABLE = True
except (ImportError, RuntimeError):
    reader = None
    RFID_AVAILABLE = False
    print("[WARNING] MFRC522 not available. RFID scanning will be disabled.")

# Import garage controller
from core.garage import get_garage_controller

DOOR_MODULE_IPS = ["192.168.0.51"]  # replace with actual IPs
DOOR_MODULE_PORT = 5006


class Toggle(QCheckBox):
    """Simple Toggle control implemented as a styled QCheckBox.

    Keeps the `stateChanged` signal API used by the rest of the UI.
    """
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)
        # Basic visual styling; keep small and self-contained so tests/dev UI render.
        self.setStyleSheet(
            "QCheckBox { color: white; font-size: 14px; }"
            "QCheckBox::indicator { width: 44px; height: 24px; border-radius: 12px; }"
            "QCheckBox::indicator:unchecked { background: #7f8c8d; }"
            "QCheckBox::indicator:checked { background: #27ae60; }"
        )


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Admin Password")
        self.setModal(True)
        layout = QVBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_password(self):
        return self.password_input.text()

class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setWindowTitle("User Details")
        self.setModal(True)
        layout = QVBoxLayout()

        self.uid_input = QLineEdit()
        self.name_input = QLineEdit()
        self.admin_check = QCheckBox("Is Admin")

        layout.addWidget(QLabel("UID:"))
        layout.addWidget(self.uid_input)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.admin_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        if user:
            self.uid_input.setText(user['uid'])
            self.name_input.setText(user['name'])
            self.admin_check.setChecked(user['isAdmin'])
            self.uid_input.setDisabled(True)

    def scan_uid(self):
        if not RFID_AVAILABLE or reader is None:
            QMessageBox.warning(self, "RFID Not Available", "RFID scanning is not available on this system.")
            return
        self.uid_input.setPlaceholderText("Waiting for scan...")
        thread = threading.Thread(target=self._read_uid, daemon=True)
        thread.start()

    def _read_uid(self):
        if reader is None:
            QMessageBox.warning(self, "RFID Error", "RFID reader not available")
        if not RFID_AVAILABLE or reader is None:
            return
        try:
            uid, _ = reader.read()
            self.uid_input.setText(str(uid))
        except Exception as e:
            QMessageBox.warning(self, "Scan Error", f"Failed to read RFID card: {e}")

    def get_user(self):
        return {
            "uid": self.uid_input.text().strip(),
            "name": self.name_input.text().strip(),
            "isAdmin": self.admin_check.isChecked()
        }

class GateWiseUI(QWidget):
    def __init__(self):
        super().__init__()
        self.config = config
        self.setWindowTitle(self.config.app_title)
        self.setGeometry(100, 100, self.config.window_width, self.config.window_height)

        self.primary_color = self.config.primary_color
        self.logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "Gatewise.PNG")
        self.setWindowTitle("Home Access Control")
        self.setGeometry(100, 100, 800, 480)

        self.primary_color = "#2c3e50"  # Neutral dark blue-gray for home
        self.logs_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "logs-white.png")
        self.settings_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "config_white.png")
        self.unlock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "unlock_white.png")
        self.lock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "lock_white.png")

        self.setStyleSheet(f"background-color: {self.primary_color}; color: white;")
        
        # Admin password from environment variable
        self.admin_password = os.environ.get("GATEWISE_ADMIN_PASSWORD", "admin")

        # Initialize garage controller based on config
        self.garage_controller = None
        if self.config.garage_enabled:
            try:
                from core.garage import GarageDoorController
                self.garage_controller = GarageDoorController(event_callback=self._garage_event_callback)
                print("[UI] Garage controller initialized")
            except Exception as e:
                print(f"[UI ERROR] Failed to initialize garage controller: {e}")
        else:
            # Use simpler GarageController for basic functionality
            try:
                self.garage_controller = get_garage_controller()
                if self.garage_controller and self.garage_controller.enabled:
                    self.garage_controller.set_button_callback(self.on_physical_garage_button)
            except Exception as e:
                print(f"[UI WARNING] Basic garage controller unavailable: {e}")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.stack = QStackedWidget()
        self.main_screen = QWidget()
        self.settings_screen = QWidget()
        self.log_screen = QWidget()
        self.blackout_screen = QWidget()
        self.user_screen = QWidget()
        self.garage_screen = QWidget()

        self.init_main_screen()
        self.init_settings_screen()
        self.init_log_screen()
        self.init_blackout_screen()
        self.init_user_screen()
        if self.config.garage_enabled:
            self.init_garage_screen()

        self.stack.addWidget(self.main_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.log_screen)
        self.stack.addWidget(self.blackout_screen)
        self.stack.addWidget(self.user_screen)
        if self.config.garage_enabled:
            self.stack.addWidget(self.garage_screen)

        main_layout.addWidget(self.stack)
        main_layout.addLayout(self.init_action_bar())
    
    def _garage_event_callback(self, event_type: str, data):
        """Handle garage controller events."""
        print(f"[UI] Garage event: {event_type} - {data}")
        # Update garage UI if on garage screen
        if self.config.garage_enabled and self.stack.currentWidget() == self.garage_screen:
            self.update_garage_status()

    def init_main_screen(self):
        layout = QVBoxLayout()
        self.main_screen.setLayout(layout)

        # Simple welcome header for home use
        title_label = QLabel("Home Access Control")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("padding: 20px;")
        layout.addWidget(title_label)

        icons_layout = QGridLayout()
        icons_layout.setColumnStretch(0, 1)
        icons_layout.setColumnStretch(1, 1)
        if self.config.garage_enabled:
            icons_layout.setColumnStretch(2, 1)
        icons_layout.setRowStretch(0, 1)

        logs_icon = QPushButton()
        if os.path.exists(self.logs_icon_path):
            logs_icon.setIcon(QIcon(self.logs_icon_path))
        logs_icon.setIconSize(QSize(128, 128))
        logs_icon.setStyleSheet("background-color: transparent;")
        logs_icon.clicked.connect(self.show_logs)
        icons_layout.addWidget(logs_icon, 0, 0, alignment=Qt.AlignCenter)

        settings_icon = QPushButton()
        if os.path.exists(self.settings_icon_path):
            settings_icon.setIcon(QIcon(self.settings_icon_path))
        settings_icon.setIconSize(QSize(128, 128))
        settings_icon.setStyleSheet("background-color: transparent;")
        settings_icon.clicked.connect(self.request_password)
        icons_layout.addWidget(settings_icon, 0, 1, alignment=Qt.AlignCenter)

        # Add garage button if enabled
        if self.config.garage_enabled:
            garage_icon = QPushButton()
            garage_icon.setText("🚪")  # Garage door emoji as placeholder
            garage_icon.setFont(QFont("Arial", 48))
            garage_icon.setStyleSheet("background-color: transparent; color: white;")
            garage_icon.clicked.connect(self.show_garage)
            garage_icon.setToolTip("Garage Control")
            icons_layout.addWidget(garage_icon, 0, 2, alignment=Qt.AlignCenter)

        layout.addLayout(icons_layout)

    def init_action_bar(self):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        unlock_btn = QPushButton("Unlock Door")
        if os.path.exists(self.unlock_icon_path):
            unlock_btn.setIcon(QIcon(self.unlock_icon_path))
        unlock_btn.setIconSize(QSize(32, 32))
        unlock_btn.clicked.connect(self.unlock_door)

        lock_btn = QPushButton("Lock Door")
        if os.path.exists(self.lock_icon_path):
            lock_btn.setIcon(QIcon(self.lock_icon_path))
        lock_btn.setIconSize(QSize(32, 32))
        lock_btn.clicked.connect(self.lock_door)

        garage_btn = QPushButton("Garage")
        garage_btn.setIcon(QIcon(self.settings_icon_path))  # Reuse settings icon for garage
        garage_btn.setIconSize(QSize(32, 32))
        garage_btn.clicked.connect(self.show_garage)

        for btn in (unlock_btn, lock_btn, garage_btn):
            btn.setStyleSheet("background-color: #34495e; color: white; padding: 10px; border-radius: 10px; font-size: 14px;")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn_layout.addWidget(btn)

        return btn_layout

    def init_settings_screen(self):
        layout = QVBoxLayout()
        self.settings_screen.setLayout(layout)

        title = QLabel("Settings Panel")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        blackout_btn = QPushButton("Blackout Schedule")
        blackout_btn.clicked.connect(self.show_blackout)
        user_btn = QPushButton("User Maintenance")
        user_btn.clicked.connect(self.show_user_management)
        garage_btn = QPushButton("Garage Control")
        garage_btn.clicked.connect(self.show_garage)

        for btn in (blackout_btn, user_btn, garage_btn):
            btn.setStyleSheet("background-color: #34495e; color: white; font-size: 16px; padding: 12px;")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(btn)

        # Timed Access Settings Section (renamed from "Class Access Settings")
        lock_settings_title = QLabel("Timed Access Settings")
        lock_settings_title.setFont(QFont("Arial", 14))
        lock_settings_title.setAlignment(Qt.AlignLeft)
        layout.addWidget(lock_settings_title)

        self.class_duration_dropdown = QComboBox()
        self.class_duration_dropdown.addItems(["15 minutes", "30 minutes", "45 minutes", "60 minutes", "90 minutes"])
        self.class_duration_dropdown.setStyleSheet("background-color: #1e1e1e; color: white; font-size: 14px; padding: 8px;")
        layout.addWidget(self.class_duration_dropdown)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.show_main)
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 14px; padding: 10px;")
        layout.addWidget(back_btn)

    def init_log_screen(self):
        layout = QVBoxLayout()
        self.log_screen.setLayout(layout)
        layout.addWidget(QLabel("RFID Entry Log"))
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.show_main)
        layout.addWidget(back_btn)

    def init_blackout_screen(self):
        layout = QVBoxLayout()
        self.blackout_screen.setLayout(layout)

        title = QLabel("Blackout Schedule")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QVBoxLayout()

        self.blackout_blocks = {}
        self.block_layouts = {}

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            group = QGroupBox(day)
            group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; padding: 10px; }")
            group_layout = QVBoxLayout()
            self.blackout_blocks[day] = []
            self.block_layouts[day] = group_layout

            add_btn = QPushButton("Add Time Block")
            add_btn.setStyleSheet("background-color: #2c3e50; color: white; font-size: 16px; padding: 8px;")
            add_btn.clicked.connect(lambda _, d=day: self.add_time_block(d))

            group_layout.addWidget(add_btn)
            group.setLayout(group_layout)
            grid.addWidget(group)

        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        save_btn = QPushButton("Save Schedule")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-size: 16px; padding: 10px;")
        save_btn.clicked.connect(self.save_blackout_schedule)
        layout.addWidget(save_btn)

        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 16px; padding: 10px;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_screen))
        layout.addWidget(back_btn)

        self.load_blackout_schedule()

    def add_time_block(self, day_name, start_str="04:00", end_str="10:00"):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        start_time = QTimeEdit()
        start_time.setTime(QTime.fromString(start_str, "HH:mm"))
        start_time.setDisplayFormat("HH:mm")
        start_time.setMinimumWidth(100)
        start_time.setStyleSheet("font-size: 16px;")

        end_time = QTimeEdit()
        end_time.setTime(QTime.fromString(end_str, "HH:mm"))
        end_time.setDisplayFormat("HH:mm")
        end_time.setMinimumWidth(100)
        end_time.setStyleSheet("font-size: 16px;")

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(40, 40)
        remove_btn.setStyleSheet("font-size: 18px; color: red; background: transparent;")

        layout.addWidget(QLabel("Start:"))
        layout.addWidget(start_time)
        layout.addWidget(QLabel("End:"))
        layout.addWidget(end_time)
        layout.addWidget(remove_btn)
        container.setLayout(layout)
        self.block_layouts[day_name].insertWidget(self.block_layouts[day_name].count() - 1, container)

        self.blackout_blocks[day_name].append((start_time, end_time, container))

        def remove_block():
            self.block_layouts[day_name].removeWidget(container)
            container.setParent(None)
            self.blackout_blocks[day_name].remove((start_time, end_time, container))
            # QMessageBox.information(self, "Removed", f"Block removed from {day_name}")

        remove_btn.clicked.connect(remove_block)
        # QMessageBox.information(self, "Added", f"Block added to {day_name}")

    def save_blackout_schedule(self):
        data = {}
        for day, blocks in self.blackout_blocks.items():
            day_list = []
            for start, end, _ in blocks:
                day_list.append({
                    "start": start.time().toString("HH:mm"),
                    "end": end.time().toString("HH:mm")
                })
            data[day] = day_list

        with open(self.config.blackout_file, "w") as f:
            json.dump(data, f, indent=4)
        QMessageBox.information(self, "Saved", "Blackout schedule saved successfully.")
        # Navigate back to settings screen after saving
        self.stack.setCurrentWidget(self.settings_screen)

    def load_blackout_schedule(self):
        if not os.path.exists(self.config.blackout_file):
            return

        try:
            with open(self.config.blackout_file, "r") as f:
                data = json.load(f)

            for day, blocks in data.items():
                if day in self.blackout_blocks:
                    for b in blocks:
                        self.add_time_block(day, b["start"], b["end"])
        except Exception as e:
            print(f"[ERROR] Failed to load blackout schedule: {e}")

    def init_garage_screen(self):
        """Initialize garage door control screen."""
        layout = QVBoxLayout()
        self.garage_screen.setLayout(layout)

        title = QLabel("Garage Door Control")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Status display
        status_group = QGroupBox("Current Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #444; margin-top: 10px; padding: 15px; }")
        status_layout = QVBoxLayout()

        self.garage_status_label = QLabel("Status: Unknown")
        self.garage_status_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.garage_status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.garage_status_label)

        self.garage_last_trigger_label = QLabel("Last triggered: Never")
        self.garage_last_trigger_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.garage_last_trigger_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Control buttons
        control_group = QGroupBox("Controls")
        control_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #444; margin-top: 10px; padding: 15px; }")
        control_layout = QVBoxLayout()

        self.garage_trigger_btn = QPushButton("Trigger Garage Door")
        self.garage_trigger_btn.setStyleSheet("background-color: #e67e22; color: white; font-size: 18px; padding: 15px; font-weight: bold;")
        self.garage_trigger_btn.clicked.connect(self.trigger_garage_door)
        control_layout.addWidget(self.garage_trigger_btn)

        if self.config.garage_auto_close_seconds > 0:
            self.garage_cancel_auto_close_btn = QPushButton("Cancel Auto-Close")
            self.garage_cancel_auto_close_btn.setStyleSheet("background-color: #c0392b; color: white; font-size: 14px; padding: 10px;")
            self.garage_cancel_auto_close_btn.clicked.connect(self.cancel_auto_close)
            control_layout.addWidget(self.garage_cancel_auto_close_btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Recent events
        events_group = QGroupBox("Recent Activity")
        events_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #444; margin-top: 10px; padding: 10px; }")
        events_layout = QVBoxLayout()

        self.garage_events_list = QListWidget()
        self.garage_events_list.setStyleSheet("background-color: #1e1e1e; color: white; font-size: 12px;")
        events_layout.addWidget(self.garage_events_list)

        events_group.setLayout(events_layout)
        layout.addWidget(events_group)

        # Back button
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 14px; padding: 10px;")
        back_btn.clicked.connect(self.show_main)
        layout.addWidget(back_btn)

        # Initial status update
        self.update_garage_status()

    def trigger_garage_door(self):
        """Trigger the garage door relay."""
        if not self.garage_controller:
            QMessageBox.warning(self, "Error", "Garage controller not available.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Action",
            "Trigger the garage door?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success = self.garage_controller.trigger("ui")
            if success:
                QMessageBox.information(self, "Success", "Garage door triggered.")
                self.update_garage_status()
            else:
                QMessageBox.warning(self, "Failed", "Failed to trigger garage door.")

    def cancel_auto_close(self):
        """Cancel scheduled auto-close."""
        if not self.garage_controller:
            return

        self.garage_controller.cancel_auto_close()
        QMessageBox.information(self, "Cancelled", "Auto-close cancelled.")

    def update_garage_status(self):
        """Update garage status display."""
        if not self.garage_controller:
            return

        # Update status label
        state = self.garage_controller.get_state()
        state_colors = {
            "open": "#e74c3c",
            "closed": "#27ae60",
            "opening": "#f39c12",
            "closing": "#f39c12",
            "unknown": "#95a5a6"
        }
        color = state_colors.get(state, "#95a5a6")
        self.garage_status_label.setText(f"Status: {state.upper()}")
        self.garage_status_label.setStyleSheet(f"color: {color};")

        # Update last trigger time
        if self.garage_controller.last_trigger_time:
            last_time = datetime.fromtimestamp(self.garage_controller.last_trigger_time)
            self.garage_last_trigger_label.setText(f"Last triggered: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.garage_last_trigger_label.setText("Last triggered: Never")

        # Update events list
        events = self.garage_controller.get_recent_events(20)
        self.garage_events_list.clear()
        for event in reversed(events):  # Show newest first
            self.garage_events_list.addItem(event)

    def show_garage(self):
        """Show garage control screen."""
        if self.config.garage_enabled:
            self.update_garage_status()
            self.stack.setCurrentWidget(self.garage_screen)
        else:
            QMessageBox.information(self, "Not Available", "Garage control is not enabled.")

    def init_user_screen(self):
        layout = QVBoxLayout()
        self.user_screen.setLayout(layout)

        title = QLabel("User Maintenance")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.user_list_widget = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.user_list_widget)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        buttons_layout = QHBoxLayout()

        add_user_btn = QPushButton("Add User")
        add_user_btn.setStyleSheet("background-color: #2980b9; color: white; font-size: 16px; padding: 10px;")
        add_user_btn.clicked.connect(self.add_user_dialog)
        buttons_layout.addWidget(add_user_btn)

        push_btn = QPushButton("Push to Doors")
        push_btn.setStyleSheet("background-color: #27ae60; color: white; font-size: 16px; padding: 10px;")
        push_btn.clicked.connect(self.push_to_door_modules)
        buttons_layout.addWidget(push_btn)

        self.auto_sync_toggle = QCheckBox("Enable Auto-Sync")
        self.auto_sync_toggle.setStyleSheet("color: white; font-size: 14px;")
        self.auto_sync_toggle.setChecked(False)
        self.auto_sync_toggle.stateChanged.connect(self.toggle_auto_sync)
        self.auto_sync_enabled = False
        self.auto_sync_toggle.setChecked(False)
        self.auto_sync_toggle.stateChanged.connect(self.toggle_auto_sync)
        self.auto_sync_toggle.setStyleSheet("font-size: 14px;")
        buttons_layout.addWidget(self.auto_sync_toggle)

        layout.addLayout(buttons_layout)
        
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_screen))
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 14px; padding: 10px;")
        layout.addWidget(back_btn)

        self.auto_sync_enabled = False
        self.load_users()

    def load_users(self):
        self.users = []
        if os.path.exists(self.config.users_file):
            with open(self.config.users_file, "r") as f:
                self.users = json.load(f)
        self.refresh_user_list()

    def refresh_user_list(self):
        for i in reversed(range(self.user_list_widget.count())):
            widget = self.user_list_widget.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for user in self.users:
            group = QGroupBox()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f"UID: {user['uid']}"))
            layout.addWidget(QLabel(f"Name: {user['name']}"))
            layout.addWidget(QLabel(f"Admin: {'Yes' if user['isAdmin'] else 'No'}"))

            edit_btn = QPushButton("✎")
            edit_btn.setFixedSize(40, 40)
            edit_btn.clicked.connect(lambda _, u=user: self.edit_user_dialog(u))

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(40, 40)
            del_btn.clicked.connect(lambda _, u=user: self.delete_user(u))

            layout.addWidget(edit_btn)
            layout.addWidget(del_btn)
            group.setLayout(layout)
            self.user_list_widget.addWidget(group)

    def add_user_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec_():
            new_user = dialog.get_user()
            if not new_user['uid'] or not new_user['name']:
                QMessageBox.warning(self, "Invalid Input", "UID and Name are required.")
                return
            if any(u['uid'] == new_user['uid'] for u in self.users):
                QMessageBox.warning(self, "Duplicate UID", "A user with this UID already exists.")
                return
            self.users.append(new_user)
            self.save_users()
            self.refresh_user_list()
            QMessageBox.information(self, "Success", "User added successfully.")

    def edit_user_dialog(self, user):
        dialog = UserDialog(self, user=user)
        if dialog.exec_():
            updated_user = dialog.get_user()
            for i, u in enumerate(self.users):
                if u['uid'] == updated_user['uid']:
                    self.users[i] = updated_user
                    break
            self.save_users()
            self.refresh_user_list()
            QMessageBox.information(self, "Success", "User updated successfully.")

    def delete_user(self, user):
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete user {user['name']}?")
        if confirm == QMessageBox.Yes:
            self.users = [u for u in self.users if u['uid'] != user['uid']]
            self.save_users()
            self.refresh_user_list()
            QMessageBox.information(self, "Deleted", "User removed.")

    def save_users(self):
        with open(self.config.users_file, "w") as f:
            json.dump(self.users, f, indent=4)
        if getattr(self, "auto_sync_enabled", False):
            # trigger a non-blocking push so GUI stays responsive
            self.push_to_door_modules()

    def toggle_auto_sync(self, state):
        """Enable/disable automatic syncing when user lists change."""
        self.auto_sync_enabled = bool(state)

    def push_to_door_modules(self):
        """Send the current `self.users` to each door module.

        This call is non-blocking: it spawns a background thread to perform network I/O.
        The payload is JSON: {"users": [...]}
        """
        users_payload = {
            "users": self.users
        }

        def _worker(payload, hosts, port):
            data = json.dumps(payload).encode("utf-8")
            for host in hosts:
                try:
                    with socket.create_connection((host, port), timeout=5) as s:
                        s.sendall(data)
                        # optional small ACK read (non-blocking, best-effort)
                        try:
                            s.settimeout(1.0)
                            _ = s.recv(1024)
                        except Exception:
                            pass
                    print(f"[INFO] Pushed users to {host}:{port}")
                except Exception as e:
                    print(f"[WARN] Failed to push to {host}:{port} - {e}")

        hosts = DOOR_MODULE_IPS.copy()
        t = threading.Thread(target=_worker, args=(users_payload, hosts, DOOR_MODULE_PORT), daemon=True)
        t.start()

    def request_password(self):
        dlg = PasswordDialog(self)
        if dlg.exec_():
            entered_password = dlg.get_password()
            if entered_password == self.config.admin_password:
                self.show_settings()
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect password.")

    def show_main(self):
        self.stack.setCurrentWidget(self.main_screen)

    def show_logs(self):
        self.stack.setCurrentWidget(self.log_screen)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_screen)

    def show_blackout(self):
        self.stack.setCurrentWidget(self.blackout_screen)

    def show_user_management(self):
        self.stack.setCurrentWidget(self.user_screen)
    
    def unlock_door(self):
        """Unlock door action."""
        print("[INFO] Unlock door triggered")
        QMessageBox.information(self, "Door Action", "Door unlocked")
    
    def lock_door(self):
        """Lock door action."""
        print("[INFO] Lock door triggered")
        QMessageBox.information(self, "Door Action", "Door locked")
    
    def on_physical_garage_button(self):
        """Handle physical garage button press."""
        print("[INFO] Physical garage button pressed - triggering door")
        if self.garage_controller:
            self.garage_controller.trigger_door()
    
    def closeEvent(self, event):
        """Handle window close event - clean up resources."""
        print("[UI] Closing application...")
        if self.garage_controller:
            self.garage_controller.cleanup()
        event.accept()


def launch_ui():
    app = QApplication(sys.argv)
    window = GateWiseUI()
    
    # Apply fullscreen if configured
    if config.fullscreen:
        window.showFullScreen()
    else:
        window.show()
    
    # Hide cursor if configured (for touchscreen-only systems)
    if not config.show_cursor:
        app.setOverrideCursor(Qt.BlankCursor)
    
    sys.exit(app.exec_())