import sys
import os
import json
import threading
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QSizePolicy, QStackedWidget, QLineEdit, QDialog,
    QDialogButtonBox, QGridLayout, QComboBox, QScrollArea, QGroupBox, QTimeEdit,
    QMessageBox, QCheckBox, QFrame
)
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, QTime, QPropertyAnimation, QEasingCurve
from PySide6.QtCore import QRect

# Attempt to import MFRC522 RFID reader. If not present (e.g., running on Windows),
# fall back gracefully so the UI can run without hardware.
# try:
#     from mfrc522 import SimpleMFRC522
#     try:
#         reader = SimpleMFRC522()
#         RFID_AVAILABLE = True
#     except Exception:
#         reader = None
#         RFID_AVAILABLE = False
#         print("[WARNING] MFRC522 present but failed to initialize. RFID scanning disabled.")
# except Exception:
#     reader = None
#     RFID_AVAILABLE = False
#     print("[WARNING] MFRC522 not available. RFID scanning will be disabled.")



DOOR_MODULE_IPS = ["192.168.0.75"]  # replace with actual IPs
DOOR_MODULE_PORT = 80


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Admin Password")
        self.setModal(True)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px;")
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # On-screen keyboard for touch input
        keyboard_layout = QGridLayout()
        keyboard_layout.setSpacing(6)

        rows = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "@"],
            ["z", "x", "c", "v", "b", "n", "m", "_", "-", "."],
        ]

        def make_key_button(text, col_span=1, row=0, col=0):
            btn = QPushButton(text)
            btn.setMinimumHeight(42)
            btn.setStyleSheet(
                "QPushButton { background-color: #2c3e50; color: white; font-size: 14px; padding: 10px; border-radius: 6px; }"
                "QPushButton:hover { background-color: #3b5166; }"
                "QPushButton:pressed { background-color: #1f2d3a; }"
            )
            btn.clicked.connect(lambda _, t=text: self._append_text(t))
            keyboard_layout.addWidget(btn, row, col, 1, col_span)

        for row_index, keys in enumerate(rows):
            for col_index, key in enumerate(keys):
                make_key_button(key, row=row_index, col=col_index)

        # Control keys
        backspace_btn = QPushButton("Backspace")
        backspace_btn.setMinimumHeight(42)
        backspace_btn.setStyleSheet(
            "QPushButton { background-color: #7f8c8d; color: white; font-size: 14px; padding: 10px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #95a5a6; }"
            "QPushButton:pressed { background-color: #6c7a7b; }"
        )
        backspace_btn.clicked.connect(self._backspace)
        keyboard_layout.addWidget(backspace_btn, len(rows), 0, 1, 5)

        clear_btn = QPushButton("Clear")
        clear_btn.setMinimumHeight(42)
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; font-size: 14px; padding: 10px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #e74c3c; }"
            "QPushButton:pressed { background-color: #a93226; }"
        )
        clear_btn.clicked.connect(self._clear)
        keyboard_layout.addWidget(clear_btn, len(rows), 5, 1, 2)

        space_btn = QPushButton("Space")
        space_btn.setMinimumHeight(42)
        space_btn.setStyleSheet(
            "QPushButton { background-color: #2c3e50; color: white; font-size: 14px; padding: 10px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #3b5166; }"
            "QPushButton:pressed { background-color: #1f2d3a; }"
        )
        space_btn.clicked.connect(lambda: self._append_text(" "))
        keyboard_layout.addWidget(space_btn, len(rows), 7, 1, 3)

        layout.addLayout(keyboard_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _append_text(self, text: str):
        self.password_input.insert(text)

    def _backspace(self):
        current = self.password_input.text()
        self.password_input.setText(current[:-1])

    def _clear(self):
        self.password_input.clear()

    def get_password(self):
        return self.password_input.text()

class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setWindowTitle("User Details")
        self.setModal(True)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.uid_input = QLineEdit()
        self.uid_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 6px;")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 6px;")
        self.admin_check = QCheckBox("Is Admin")
        self.admin_check.setStyleSheet("font-size: 16px;")

        uid_label = QLabel("UID:")
        uid_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(uid_label)
        layout.addWidget(self.uid_input)
        
        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        layout.addWidget(self.admin_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; min-width: 80px; }")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        if user:
            self.uid_input.setText(user['uid'])
            self.name_input.setText(user['name'])
            self.admin_check.setChecked(user['isAdmin'])
            self.uid_input.setDisabled(True)

    def scan_uid(self):
        self.uid_input.setPlaceholderText("Waiting for scan...")
        thread = threading.Thread(target=self._read_uid, daemon=True)
        thread.start()

    def _read_uid(self):
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
        self.setWindowTitle("GateWise Access Control - Power Alley CrossFit")
        self.setGeometry(0, 0, 1024, 600)  # Scaled up for 7-inch touchscreen

        # Color scheme - Industrial dark mode
        self.BG_DARK = "#1A1A1A"
        self.BG_DARKER = "#0D0D0D"
        self.COLOR_UNLOCK = "#4CAF50"  # Safety Green
        self.COLOR_LOCK = "#F44336"    # Alert Red
        self.COLOR_SECONDARY = "#2196F3"  # Primary Blue
        self.COLOR_TEXT = "#FFFFFF"
        self.COLOR_TEXT_DIM = "#B0B0B0"
        
        self.logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "Gatewise.PNG")
        self.logs_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "logs-white.png")
        self.settings_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "config_white.png")
        self.unlock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "unlock_white.png")
        self.lock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "lock_white.png")
        self.class_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "unlock_for_class.png")

        # Apply global stylesheet with Roboto Condensed/Inter
        self.setStyleSheet(self._get_global_stylesheet())

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Header (persistent)
        main_layout.addLayout(self._create_header_layout())
        
        self.stack = QStackedWidget()
        self.main_screen = QWidget()
        self.settings_screen = QWidget()
        self.log_screen = QWidget()
        self.blackout_screen = QWidget()
        self.user_screen = QWidget()

        self.init_main_screen()
        self.init_settings_screen()
        self.init_log_screen()
        self.init_blackout_screen()
        self.init_user_screen()

        self.stack.addWidget(self.main_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.log_screen)
        self.stack.addWidget(self.blackout_screen)
        self.stack.addWidget(self.user_screen)

        main_layout.addWidget(self.stack, 1)

        # Footer status bar
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(12, 8, 12, 8)
        footer_layout.setSpacing(10)
        
        self.status_indicator = QFrame()
        self.status_indicator.setFixedSize(16, 16)
        self.status_indicator.setStyleSheet(f"background-color: {self.COLOR_LOCK}; border-radius: 8px;")
        footer_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {self.COLOR_TEXT_DIM}; font-size: 12px;")
        footer_layout.addWidget(self.status_label, 1)
        
        footer = QFrame()
        footer.setStyleSheet(f"background-color: {self.BG_DARKER}; border-top: 1px solid #333;")
        footer.setLayout(footer_layout)
        footer.setFixedHeight(40)
        main_layout.addWidget(footer)
    
    def _get_global_stylesheet(self):
        """Return global stylesheet with modern design system."""
        return f"""
        * {{
            background-color: {self.BG_DARK};
            color: {self.COLOR_TEXT};
            font-family: 'Roboto Condensed', 'Inter', sans-serif;
            font-size: 18px;
        }}
        
        QPushButton {{
            background-color: #2A2A2A;
            color: {self.COLOR_TEXT};
            border: 1px solid #444;
            border-radius: 10px;
            padding: 12px 16px;
            font-weight: 500;
            min-height: 60px;
            min-width: 60px;
        }}
        
        QPushButton:hover {{
            background-color: #3A3A3A;
            border: 1px solid #555;
        }}
        
        QPushButton:pressed {{
            background-color: #1A1A1A;
            border: 1px solid #333;
        }}
        
        QPushButton:disabled {{
            color: #666;
            background-color: #1A1A1A;
        }}
        
        QLabel {{
            background-color: transparent;
        }}
        
        QComboBox, QLineEdit, QTimeEdit {{
            background-color: #2A2A2A;
            color: {self.COLOR_TEXT};
            border: 1px solid #444;
            border-radius: 8px;
            padding: 12px;
            min-height: 50px;
            font-size: 18px;
        }}
        
        QGroupBox {{
            color: {self.COLOR_TEXT};
            border: 1px solid #444;
            border-radius: 6px;
            padding-top: 10px;
        }}
        
        QListWidget {{
            background-color: #2A2A2A;
            color: {self.COLOR_TEXT};
            border: 1px solid #444;
            border-radius: 6px;
        }}
        """
    
    def _create_header_layout(self):
        """Create persistent header with title and status."""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(16)
        
        title_label = QLabel("POWER ALLEY CROSSFIT")
        title_font = QFont("Roboto Condensed", 32, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {self.COLOR_TEXT};")
        header_layout.addWidget(title_label, 1)
        
        # Lock status indicator
        self.lock_status_frame = QFrame()
        self.lock_status_frame.setFixedHeight(60)
        self.lock_status_frame.setMinimumWidth(180)
        self.update_lock_status_display("locked")
        header_layout.addWidget(self.lock_status_frame)
        
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {self.BG_DARKER}; border-bottom: 2px solid #333;")
        header_frame.setLayout(header_layout)
        header_frame.setFixedHeight(90)
        
        container = QVBoxLayout()
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(header_frame)
        
        return container
    
    def update_lock_status_display(self, status):
        """Update the lock status indicator in header and main alert box."""
        # Update header indicator
        for i in reversed(range(self.lock_status_frame.layout().count() if self.lock_status_frame.layout() else 0)):
            self.lock_status_frame.layout().itemAt(i).widget().setParent(None)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        if status == "locked":
            indicator = QFrame()
            indicator.setFixedSize(28, 28)
            indicator.setStyleSheet(f"background-color: {self.COLOR_LOCK}; border-radius: 14px;")
            layout.addWidget(indicator)
            text = QLabel("LOCKED")
            text.setStyleSheet(f"color: {self.COLOR_LOCK}; font-weight: bold; font-size: 18px;")
        else:
            indicator = QFrame()
            indicator.setFixedSize(28, 28)
            indicator.setStyleSheet(f"background-color: {self.COLOR_UNLOCK}; border-radius: 14px;")
            layout.addWidget(indicator)
            text = QLabel("UNLOCKED")
            text.setStyleSheet(f"color: {self.COLOR_UNLOCK}; font-weight: bold; font-size: 18px;")
        
        layout.addWidget(text)
        layout.addStretch()
        
        self.lock_status_frame.setLayout(layout)
        self.lock_status_frame.setStyleSheet(f"background-color: {self.BG_DARKER}; border-radius: 8px; border: 1px solid #444;")
        
        # Update main screen alert box
        if hasattr(self, 'lock_status_alert'):
            if status == "locked":
                self.lock_status_alert.setStyleSheet(f"""
                    QFrame {{
                        background-color: {self.COLOR_LOCK};
                        border-radius: 12px;
                        padding: 20px;
                    }}
                """)
                self.lock_status_label.setText("LOCKED")
                self.lock_status_subtext.setText("ALERT")
                # Update icon
                lock_pixmap = QPixmap(self.lock_icon_path)
                if not lock_pixmap.isNull():
                    self.lock_icon_label.setPixmap(lock_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.lock_status_alert.setStyleSheet(f"""
                    QFrame {{
                        background-color: {self.COLOR_UNLOCK};
                        border-radius: 12px;
                        padding: 20px;
                    }}
                """)
                self.lock_status_label.setText("UNLOCKED")
                self.lock_status_subtext.setText("ACCESS GRANTED")
                # Update icon
                unlock_pixmap = QPixmap(self.unlock_icon_path)
                if not unlock_pixmap.isNull():
                    self.lock_icon_label.setPixmap(unlock_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    

    def set_status(self, message: str, is_locked: bool = None):
        """Update footer status text and lock indicator."""
        if hasattr(self, "status_label"):
            self.status_label.setText(message)
        if is_locked is not None:
            status = "locked" if is_locked else "unlocked"
            self.update_lock_status_display(status)

    def unlock_door(self, duration_ms: int):
        """Send unlock request to door module via HTTP POST."""
        payload = {"duration": duration_ms}
        self._send_http_request("unlock", payload)
        self.set_status(f"🔓 Door unlocked for {duration_ms / 1000:.1f}s", is_locked=False)

    def lock_door(self):
        """Send lock request to door module via HTTP POST."""
        payload = {}
        self._send_http_request("lock", payload)
        self.set_status("🔒 Door locked", is_locked=True)

    def exit_to_desktop(self):
        """Close the application and return to desktop."""
        app = QApplication.instance()
        if app:
            app.quit()

    def _send_http_request(self, endpoint: str, payload: dict):
        """Send HTTP POST request to door module in background thread."""
        def _worker(ep, data, hosts, port):
            json_data = json.dumps(data).encode("utf-8")
            for host in hosts:
                try:
                    import http.client
                    conn = http.client.HTTPConnection(host, port, timeout=5)
                    conn.request("POST", f"/{ep}", json_data, {"Content-Type": "application/json"})
                    response = conn.getresponse()
                    response.read()
                    conn.close()
                    print(f"[INFO] {ep} request sent to {host}:{port}")
                except Exception as e:
                    print(f"[WARN] Failed to send {ep} request to {host}:{port} - {e}")

        hosts = DOOR_MODULE_IPS.copy()
        t = threading.Thread(target=_worker, args=(endpoint, payload, hosts, DOOR_MODULE_PORT), daemon=True)
        t.start()

    def on_unlock_clicked(self):
        """Handle unlock button: unlock for 3 seconds."""
        self.unlock_door(3000)
        self.show_rfid_scan_event("Manual Unlock")

    def on_lock_clicked(self):
        """Handle lock button: lock the door with confirmation."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Lock",
            "Are you sure you want to lock the door?\n\nThis will override any active unlock duration.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No for safety
        )
        
        if reply == QMessageBox.Yes:
            self.lock_door()

    def on_class_unlock_clicked(self):
        """Handle class unlock button: unlock for duration from dropdown."""
        # Parse duration from dropdown text (e.g., "60 minutes" -> 60)
        duration_text = self.class_duration_dropdown.currentText()
        try:
            duration_minutes = int(duration_text.split()[0])
            duration_ms = duration_minutes * 60 * 1000
            self.unlock_door(duration_ms)
            self.show_rfid_scan_event("Class Unlock")
        except (ValueError, IndexError):
            print(f"[ERROR] Failed to parse duration from '{duration_text}'")
            self.set_status("Error parsing class duration")

    def init_main_screen(self):
        """Initialize main screen with status alert and 2x2 button grid."""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.main_screen.setLayout(layout)

        # Lock Status Alert Box (large, prominent)
        self.lock_status_alert = QFrame()
        self.lock_status_alert.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLOR_LOCK};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        self.lock_status_alert.setFixedHeight(100)
        lock_alert_layout = QHBoxLayout()
        lock_alert_layout.setContentsMargins(20, 12, 20, 12)
        lock_alert_layout.setSpacing(20)
        
        # Use icon image instead of emoji
        self.lock_icon_label = QLabel()
        lock_pixmap = QPixmap(self.lock_icon_path)
        if not lock_pixmap.isNull():
            self.lock_icon_label.setPixmap(lock_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lock_alert_layout.addWidget(self.lock_icon_label)
        
        self.lock_status_label = QLabel("LOCKED")
        self.lock_status_label.setFont(QFont("Roboto Condensed", 36, QFont.Bold))
        self.lock_status_label.setStyleSheet(f"color: #000000;")
        lock_alert_layout.addWidget(self.lock_status_label)
        
        self.lock_status_subtext = QLabel("ALERT")
        self.lock_status_subtext.setFont(QFont("Roboto Condensed", 18))
        self.lock_status_subtext.setStyleSheet(f"color: #000000;")
        lock_alert_layout.addWidget(self.lock_status_subtext)
        lock_alert_layout.addStretch()
        
        self.lock_status_alert.setLayout(lock_alert_layout)
        layout.addWidget(self.lock_status_alert)

        # RFID Scan Event Display (hidden by default, shown for 10 seconds on scan)
        self.scan_event_frame = QFrame()
        self.scan_event_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLOR_SECONDARY};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        self.scan_event_frame.setFixedHeight(100)
        scan_layout = QHBoxLayout()
        scan_layout.setContentsMargins(20, 12, 20, 12)
        scan_layout.setSpacing(20)
        
        scan_icon = QLabel("✓")
        scan_icon.setFont(QFont("Arial", 48))
        scan_icon.setStyleSheet("color: #FFFFFF;")
        scan_layout.addWidget(scan_icon)
        
        self.scan_name_label = QLabel("Guest User")
        self.scan_name_label.setFont(QFont("Roboto Condensed", 32, QFont.Bold))
        self.scan_name_label.setStyleSheet("color: #FFFFFF;")
        scan_layout.addWidget(self.scan_name_label)
        
        self.scan_time_label = QLabel("Just now")
        self.scan_time_label.setFont(QFont("Roboto Condensed", 18))
        self.scan_time_label.setStyleSheet("color: #FFFFFF;")
        scan_layout.addWidget(self.scan_time_label)
        scan_layout.addStretch()
        
        self.scan_event_frame.setLayout(scan_layout)
        self.scan_event_frame.hide()
        layout.addWidget(self.scan_event_frame)
        
        # Setup scan timer (10 seconds)
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self._hide_scan_event)

        # 2x2 Grid Layout for action buttons
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # 1. Lock Button (top-left)
        lock_btn = self._create_action_button(
            "LOCK",
            "Lock the door",
            self.COLOR_LOCK,
            self.on_lock_clicked,
            is_primary=True,
            icon_path=self.lock_icon_path
        )
        grid.addWidget(lock_btn, 0, 0)

        # 2. Unlock for Class Button (top-right)
        class_btn = self._create_action_button(
            "UNLOCK FOR\nCLASS",
            "Unlock for class",
            self.COLOR_UNLOCK,
            self.on_class_unlock_clicked,
            is_primary=True,
            icon_path=self.class_icon_path
        )
        grid.addWidget(class_btn, 0, 1)

        # 3. Settings Button (bottom-left)
        settings_btn = self._create_action_button(
            "SETTINGS",
            "Admin settings",
            "#FF9800",
            self.request_password,
            is_primary=True,
            icon_path=self.settings_icon_path
        )
        grid.addWidget(settings_btn, 1, 0)

        # 4. Log Viewer Button (bottom-right)
        logs_btn = self._create_action_button(
            "LOG VIEWER",
            "View entry logs",
            "#9C27B0",
            self.show_logs,
            is_primary=True,
            icon_path=self.logs_icon_path
        )
        grid.addWidget(logs_btn, 1, 1)

        layout.addLayout(grid, 1)
    
    def _create_action_button(self, label: str, tooltip: str, color: str, callback, is_primary: bool = True, icon_path: str = None):
        """Create a styled action button with tactile feedback and optional icon."""
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFont(QFont("Roboto Condensed", 20 if is_primary else 16, QFont.Bold))
        
        # Load and set icon if provided
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            btn.setIcon(icon)
            btn.setIconSize(QSize(48 if is_primary else 32, 48 if is_primary else 32))
        
        if is_primary:
            btn.setMinimumHeight(140)
            btn.setMinimumWidth(140)
        else:
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(80)
        
        # Create stylesheet with color-specific styling
        stylesheet = f"""
        QPushButton {{
            background-color: {color};
            color: #FFFFFF;
            border: 2px solid {self._darken_color(color, 0.2)};
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}
        
        QPushButton:hover {{
            background-color: {self._lighten_color(color, 0.1)};
            border: 2px solid {self._darken_color(color, 0.1)};
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        }}
        
        QPushButton:pressed {{
            background-color: {self._darken_color(color, 0.15)};
            border: 2px solid {self._darken_color(color, 0.3)};
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            padding: 12px 8px 8px 12px;
        }}
        
        QPushButton:disabled {{
            background-color: #555555;
            color: #999999;
            border: 2px solid #444444;
            box-shadow: none;
        }}
        """
        
        btn.setStyleSheet(stylesheet)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        
        return btn
    
    def _lighten_color(self, color: str, amount: float) -> str:
        """Lighten a hex color."""
        c = QColor(color)
        c.setHsv(c.hue(), c.saturation(), min(255, int(c.value() * (1 + amount))))
        return c.name()
    
    def _darken_color(self, color: str, amount: float) -> str:
        """Darken a hex color."""
        c = QColor(color)
        c.setHsv(c.hue(), c.saturation(), max(0, int(c.value() * (1 - amount))))
        return c.name()

    def show_rfid_scan_event(self, username: str):
        """Display RFID scan event for 10 seconds."""
        self.scan_name_label.setText(username)
        self.scan_time_label.setText("Just now")
        self.scan_event_frame.show()
        
        # Stop existing timer if running
        if self.scan_timer.isActive():
            self.scan_timer.stop()
        
        # Set timer to hide after 10 seconds (10000 ms)
        self.scan_timer.start(10000)
    
    def _hide_scan_event(self):
        """Hide the scan event display."""
        self.scan_event_frame.hide()
        self.scan_timer.stop()

    def init_settings_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.settings_screen.setLayout(layout)

        title = QLabel("SETTINGS")
        title_font = QFont("Roboto Condensed", 28, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.COLOR_TEXT}; margin-bottom: 10px;")
        layout.addWidget(title)

        # Main settings buttons
        blackout_btn = self._create_settings_button("📅 Blackout Schedule", "Manage access blackout times", self.show_blackout)
        user_btn = self._create_settings_button("👥 User Maintenance", "Add/edit/delete users", self.show_user_management)

        layout.addWidget(blackout_btn)
        layout.addWidget(user_btn)

        # Class Access Duration Section
        lock_settings_group = QGroupBox("Class Unlock Duration")
        lock_settings_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                color: {self.COLOR_TEXT};
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 8px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        lock_layout = QVBoxLayout()
        
        self.class_duration_dropdown = QComboBox()
        self.class_duration_dropdown.addItems(["15 minutes", "30 minutes", "45 minutes", "60 minutes", "90 minutes"])
        self.class_duration_dropdown.setCurrentIndex(3)
        self.class_duration_dropdown.setMinimumHeight(45)
        lock_layout.addWidget(self.class_duration_dropdown)
        lock_settings_group.setLayout(lock_layout)
        layout.addWidget(lock_settings_group)

        layout.addStretch()

        # System control buttons
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)

        shutdown_btn = self._create_danger_button("🔌 Shutdown System", self.shutdown_system, is_large=True)
        exit_btn = self._create_danger_button("🚪 Exit to Desktop", self.exit_to_desktop, is_large=True)
        back_btn = self._create_neutral_button("← Back to Main", self.show_main, is_large=True)

        buttons_layout.addWidget(shutdown_btn, 0, 0)
        buttons_layout.addWidget(exit_btn, 0, 1)
        buttons_layout.addWidget(back_btn, 0, 2)

        layout.addLayout(buttons_layout)
    
    def _create_settings_button(self, label: str, tooltip: str, callback):
        """Create a settings section button."""
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFont(QFont("Roboto Condensed", 18, QFont.Bold))
        btn.setMinimumHeight(70)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2A2A2A;
                color: {self.COLOR_TEXT};
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #3A3A3A;
                border: 1px solid #555;
            }}
            QPushButton:pressed {{
                background-color: #1A1A1A;
                border: 1px solid #333;
            }}
        """)
        btn.clicked.connect(callback)
        return btn
    
    def _create_danger_button(self, label: str, callback, is_large: bool = False):
        """Create a danger/warning button (red)."""
        btn = QPushButton(label)
        btn.setFont(QFont("Roboto Condensed", 16, QFont.Bold))
        btn.setMinimumHeight(65 if is_large else 58)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_LOCK};
                color: #FFFFFF;
                border: 2px solid #C62828;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FF5252;
                border: 2px solid #E53935;
            }}
            QPushButton:pressed {{
                background-color: #D32F2F;
                border: 2px solid #B71C1C;
            }}
        """)
        btn.clicked.connect(callback)
        return btn
    
    def _create_neutral_button(self, label: str, callback, is_large: bool = False):
        """Create a neutral/secondary button (gray)."""
        btn = QPushButton(label)
        btn.setFont(QFont("Roboto Condensed", 16, QFont.Bold))
        btn.setMinimumHeight(65 if is_large else 58)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #424242;
                color: {self.COLOR_TEXT};
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #505050;
                border: 1px solid #666;
            }}
            QPushButton:pressed {{
                background-color: #303030;
                border: 1px solid #444;
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def init_log_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.log_screen.setLayout(layout)
        
        title = QLabel("RFID ENTRY LOG")
        title_font = QFont("Roboto Condensed", 28, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.COLOR_TEXT}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet(f"""
            QListWidget {{
                font-size: 16px;
                padding: 8px;
                background-color: #2A2A2A;
                border: 1px solid #444;
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #333;
            }}
            QListWidget::item:selected {{
                background-color: #3A3A3A;
                color: {self.COLOR_TEXT};
            }}
        """)
        layout.addWidget(self.log_list, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        refresh_btn = self._create_action_button("🔄 REFRESH", "Reload logs", self.COLOR_SECONDARY, self.load_rfid_logs, is_primary=False)
        back_btn = self._create_neutral_button("← Back to Main", self.show_main, is_large=True)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(back_btn, 1)

        layout.addLayout(buttons_layout)

    def load_rfid_logs(self):
        """Load and display RFID logs from file."""
        self.log_list.clear()
        
        if not os.path.exists("rfid_logs.json"):
            self.log_list.addItem("No logs found. Logs will appear here after RFID scans.")
            return
        
        try:
            with open("rfid_logs.json", "r") as f:
                logs = json.load(f)
            
            if not logs:
                self.log_list.addItem("No RFID scans recorded yet.")
                return
            
            # Display logs in reverse order (newest first)
            for log in reversed(logs[-100:]):  # Show last 100 entries
                timestamp = log.get("timestamp", "Unknown time")
                name = log.get("name", "Unknown")
                uid = log.get("uid", "")
                authorized = log.get("authorized", False)
                reason = log.get("reason", "")
                
                # Format log entry with color coding
                status = "✓ GRANTED" if authorized else "✗ DENIED"
                color = "#27ae60" if authorized else "#e74c3c"
                
                log_text = f"{timestamp} | {status} | {name} ({uid})"
                if not authorized and reason:
                    log_text += f" - {reason}"
                
                item = QListWidget().item(0) if self.log_list.count() == 0 else None
                self.log_list.addItem(log_text)
                # Color code the item
                item = self.log_list.item(self.log_list.count() - 1)
                if authorized:
                    item.setForeground(QColor("#27ae60"))
                else:
                    item.setForeground(QColor("#e74c3c"))
                    
        except Exception as e:
            self.log_list.addItem(f"Error loading logs: {e}")
            print(f"[ERROR] Failed to load RFID logs: {e}")

    def init_blackout_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.blackout_screen.setLayout(layout)

        title = QLabel("BLACKOUT SCHEDULE")
        title_font = QFont("Roboto Condensed", 28, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.COLOR_TEXT}; margin-bottom: 10px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {self.BG_DARK}; border: none; }}")
        content = QWidget()
        grid = QVBoxLayout()
        grid.setSpacing(8)

        self.blackout_blocks = {}
        self.block_layouts = {}

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            group = QGroupBox(day)
            group.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    font-size: 13px;
                    color: {self.COLOR_TEXT};
                    border: 1px solid #444;
                    border-radius: 6px;
                    margin-top: 8px;
                    padding: 8px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }}
            """)
            group_layout = QVBoxLayout()
            self.blackout_blocks[day] = []
            self.block_layouts[day] = group_layout

            add_btn = QPushButton("+ Add Time Block")
            add_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2A2A2A;
                    color: {self.COLOR_TEXT};
                    font-size: 12px;
                    padding: 8px;
                    border-radius: 6px;
                    border: 1px solid #444;
                }}
                QPushButton:hover {{
                    background-color: #3A3A3A;
                    border: 1px solid #555;
                }}
                QPushButton:pressed {{
                    background-color: #1A1A1A;
                    border: 1px solid #333;
                }}
            """)
            add_btn.clicked.connect(lambda _, d=day: self.add_time_block(d))
            add_btn.setMinimumHeight(40)

            group_layout.addWidget(add_btn)
            group.setLayout(group_layout)
            grid.addWidget(group)

        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        save_btn = self._create_action_button("💾 SAVE", "Save blackout schedule", self.COLOR_UNLOCK, self.save_blackout_schedule, is_primary=False)
        back_btn = self._create_neutral_button("← Back", self.show_settings, is_large=True)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(back_btn, 1)

        layout.addLayout(buttons_layout)

        self.load_blackout_schedule()

    def add_time_block(self, day_name, start_str="04:00", end_str="10:00"):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        start_time = QTimeEdit()
        start_time.setTime(QTime.fromString(start_str, "HH:mm"))
        start_time.setDisplayFormat("HH:mm")
        start_time.setMinimumWidth(80)
        start_time.setMinimumHeight(38)
        start_time.setStyleSheet(f"""
            QTimeEdit {{
                font-size: 14px;
                background-color: #2A2A2A;
                color: {self.COLOR_TEXT};
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }}
        """)

        end_time = QTimeEdit()
        end_time.setTime(QTime.fromString(end_str, "HH:mm"))
        end_time.setDisplayFormat("HH:mm")
        end_time.setMinimumWidth(80)
        end_time.setMinimumHeight(38)
        end_time.setStyleSheet(f"""
            QTimeEdit {{
                font-size: 14px;
                background-color: #2A2A2A;
                color: {self.COLOR_TEXT};
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }}
        """)

        start_label = QLabel("From:")
        start_label.setStyleSheet(f"color: {self.COLOR_TEXT_DIM}; font-size: 12px; font-weight: bold;")
        
        end_label = QLabel("To:")
        end_label.setStyleSheet(f"color: {self.COLOR_TEXT_DIM}; font-size: 12px; font-weight: bold;")

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(48, 38)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_LOCK};
                color: #FFFFFF;
                border: 1px solid #C62828;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FF5252;
                border: 1px solid #E53935;
            }}
            QPushButton:pressed {{
                background-color: #D32F2F;
                border: 1px solid #B71C1C;
            }}
        """)

        layout.addWidget(start_label)
        layout.addWidget(start_time)
        layout.addWidget(end_label)
        layout.addWidget(end_time)
        layout.addStretch()
        layout.addWidget(remove_btn)
        
        container.setLayout(layout)
        self.block_layouts[day_name].insertWidget(self.block_layouts[day_name].count() - 1, container)

        self.blackout_blocks[day_name].append((start_time, end_time, container))

        def remove_block():
            self.block_layouts[day_name].removeWidget(container)
            container.setParent(None)
            self.blackout_blocks[day_name].remove((start_time, end_time, container))

        remove_btn.clicked.connect(remove_block)

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

        with open("blackout.json", "w") as f:
            json.dump(data, f, indent=4)
        QMessageBox.information(self, "✓ Saved", "Blackout schedule saved successfully.")
        self.set_status("✓ Blackout schedule saved")

    def load_blackout_schedule(self):
        if not os.path.exists("blackout.json"):
            return

        try:
            with open("blackout.json", "r") as f:
                data = json.load(f)

            for day, blocks in data.items():
                if day in self.blackout_blocks:
                    for b in blocks:
                        self.add_time_block(day, b["start"], b["end"])
        except Exception as e:
            print(f"[ERROR] Failed to load blackout schedule: {e}")


    def init_user_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.user_screen.setLayout(layout)

        title = QLabel("USER MAINTENANCE")
        title_font = QFont("Roboto Condensed", 28, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.COLOR_TEXT}; margin-bottom: 10px;")
        layout.addWidget(title)

        self.user_list_widget = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {self.BG_DARK}; border: none; }}")
        scroll_content = QWidget()
        scroll_content.setLayout(self.user_list_widget)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        add_user_btn = self._create_action_button("+ ADD USER", "Add a new user", self.COLOR_SECONDARY, self.add_user_dialog, is_primary=False)
        back_btn = self._create_neutral_button("← Back", self.show_settings, is_large=True)

        buttons_layout.addWidget(add_user_btn)
        buttons_layout.addWidget(back_btn, 1)

        layout.addLayout(buttons_layout)

        self.load_users()

    def load_users(self):
        self.users = []
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                self.users = json.load(f)
        self.refresh_user_list()

    def refresh_user_list(self):
        for i in reversed(range(self.user_list_widget.count())):
            widget = self.user_list_widget.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for user in self.users:
            group = QGroupBox()
            group.setStyleSheet(f"""
                QGroupBox {{
                    background-color: #2A2A2A;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 4px;
                }}
            """)
            layout = QHBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(12)
            
            uid_label = QLabel(f"ID: {user['uid']}")
            uid_label.setStyleSheet(f"font-size: 11px; color: {self.COLOR_TEXT_DIM};")
            layout.addWidget(uid_label, 0)
            
            name_label = QLabel(f"{user['name']}")
            name_font = QFont("Roboto Condensed", 13, QFont.Bold)
            name_label.setFont(name_font)
            name_label.setStyleSheet(f"color: {self.COLOR_TEXT};")
            layout.addWidget(name_label, 0)
            
            admin_badge = QLabel("👑 ADMIN" if user['isAdmin'] else "")
            admin_badge.setStyleSheet(f"font-size: 10px; color: {self.COLOR_UNLOCK}; font-weight: bold;")
            layout.addWidget(admin_badge, 0)
            
            layout.addStretch()

            edit_btn = QPushButton("✏️ EDIT")
            edit_btn.setMinimumHeight(40)
            edit_btn.setMinimumWidth(70)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_SECONDARY};
                    color: #FFFFFF;
                    border: 1px solid #1565C0;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #42A5F5;
                    border: 1px solid #1E88E5;
                }}
                QPushButton:pressed {{
                    background-color: #1E88E5;
                    border: 1px solid #0D47A1;
                }}
            """)
            edit_btn.clicked.connect(lambda _, u=user: self.edit_user_dialog(u))

            del_btn = QPushButton("🗑️ DEL")
            del_btn.setMinimumHeight(40)
            del_btn.setMinimumWidth(70)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_LOCK};
                    color: #FFFFFF;
                    border: 1px solid #C62828;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FF5252;
                    border: 1px solid #E53935;
                }}
                QPushButton:pressed {{
                    background-color: #D32F2F;
                    border: 1px solid #B71C1C;
                }}
            """)
            del_btn.clicked.connect(lambda _, u=user: self.delete_user(u))

            layout.addWidget(edit_btn, 0)
            layout.addWidget(del_btn, 0)
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
        with open("users.json", "w") as f:
            json.dump(self.users, f, indent=4)
        self.set_status("Users saved")

    def request_password(self):
        dlg = PasswordDialog(self)
        if dlg.exec_():
            if dlg.get_password() == "admin":
                self.show_settings()

    def shutdown_system(self):
        """Shutdown the Raspberry Pi system with confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Shutdown",
            "Are you sure you want to shut down the system?\n\nThis will power off the Raspberry Pi.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No for safety
        )
        
        if reply == QMessageBox.Yes:
            print("[SYSTEM] Shutting down...")
            self.set_status("Shutting down system...")
            
            # Close the application gracefully
            QApplication.processEvents()
            
            # Execute shutdown command
            try:
                if sys.platform.startswith('linux'):
                    # On Raspberry Pi/Linux
                    os.system('sudo shutdown -h now')
                elif sys.platform == 'win32':
                    # On Windows (for testing)
                    print("[SYSTEM] Would execute: shutdown /s /t 0")
                    QMessageBox.information(self, "Test Mode", "Shutdown command would execute on Raspberry Pi")
                else:
                    QMessageBox.warning(self, "Error", "Shutdown not supported on this platform")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to shutdown: {e}")

    def show_main(self):
        self.stack.setCurrentWidget(self.main_screen)

    def show_logs(self):
        self.load_rfid_logs()  # Load logs when screen is shown
        self.stack.setCurrentWidget(self.log_screen)
        self.set_status("Viewing logs")

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_screen)
        self.set_status("Settings opened")

    def show_blackout(self):
        self.stack.setCurrentWidget(self.blackout_screen)
        self.set_status("Blackout schedule")

    def show_user_management(self):
        self.stack.setCurrentWidget(self.user_screen)
        self.set_status("User maintenance")

def launch_ui():
    app = QApplication(sys.argv)
    window = GateWiseUI()
    window.showFullScreen()
    sys.exit(app.exec_())