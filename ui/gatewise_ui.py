import sys
import os
import json
import threading
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QSizePolicy, QStackedWidget, QLineEdit, QDialog,
    QDialogButtonBox, QGridLayout, QComboBox, QScrollArea, QGroupBox, QTimeEdit,
    QMessageBox, QCheckBox
)
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, QTime

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
        self.setWindowTitle("GateWise Access Control")
        self.setGeometry(100, 100, 800, 480)

        self.primary_color = "#355265"
        self.logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "Gatewise.PNG")
        self.logs_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "logs-white.png")
        self.settings_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "config_white.png")
        self.unlock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "unlock_white.png")
        self.lock_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "lock_white.png")
        self.class_icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "unlock_for_class.png")

        self.setStyleSheet(f"background-color: {self.primary_color}; color: white;")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

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

        main_layout.addWidget(self.stack)
        main_layout.addLayout(self.init_action_bar())

        # Status label for quick feedback on button presses
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setStyleSheet("padding: 6px 10px; color: #d0dbe7; font-size: 12px; background: #1f2d3a;")
        main_layout.addWidget(self.status_label)

    def set_status(self, message: str):
        """Update footer status text."""
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def unlock_door(self, duration_ms: int):
        """Send unlock request to door module via HTTP POST."""
        payload = {"duration": duration_ms}
        self._send_http_request("unlock", payload)
        self.set_status(f"Door unlocked for {duration_ms / 1000:.1f}s")

    def lock_door(self):
        """Send lock request to door module via HTTP POST."""
        payload = {}
        self._send_http_request("lock", payload)
        self.set_status("Door locked")

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

    def on_lock_clicked(self):
        """Handle lock button: lock the door."""
        self.lock_door()

    def on_class_unlock_clicked(self):
        """Handle class unlock button: unlock for duration from dropdown."""
        # Parse duration from dropdown text (e.g., "60 minutes" -> 60)
        duration_text = self.class_duration_dropdown.currentText()
        try:
            duration_minutes = int(duration_text.split()[0])
            duration_ms = duration_minutes * 60 * 1000
            self.unlock_door(duration_ms)
        except (ValueError, IndexError):
            print(f"[ERROR] Failed to parse duration from '{duration_text}'")
            self.set_status("Error parsing class duration")

    def init_main_screen(self):
        layout = QVBoxLayout()
        self.main_screen.setLayout(layout)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            logo_label.setPixmap(pixmap.scaledToHeight(60, Qt.SmoothTransformation))
        else:
            logo_label.setText("GateWise")
            logo_label.setFont(QFont("Arial", 20))
        layout.addWidget(logo_label)

        icons_layout = QGridLayout()
        icons_layout.setColumnStretch(0, 1)
        icons_layout.setColumnStretch(1, 1)
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

        layout.addLayout(icons_layout)

    def init_action_bar(self):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        unlock_btn = QPushButton()
        if os.path.exists(self.unlock_icon_path):
            unlock_btn.setIcon(QIcon(self.unlock_icon_path))
        unlock_btn.setIconSize(QSize(48, 48))
        unlock_btn.setToolTip("Unlock")
        unlock_btn.clicked.connect(self.on_unlock_clicked)

        lock_btn = QPushButton()
        if os.path.exists(self.lock_icon_path):
            lock_btn.setIcon(QIcon(self.lock_icon_path))
        lock_btn.setIconSize(QSize(48, 48))
        lock_btn.setToolTip("Lock")
        lock_btn.clicked.connect(self.on_lock_clicked)

        class_btn = QPushButton()
        if os.path.exists(self.class_icon_path):
            class_btn.setIcon(QIcon(self.class_icon_path))
        class_btn.setIconSize(QSize(48, 48))
        class_btn.setToolTip("Unlock for Class")
        class_btn.clicked.connect(self.on_class_unlock_clicked)

        for btn in (unlock_btn, lock_btn, class_btn):
            btn.setStyleSheet(
                "QPushButton { background-color: #2c3e50; color: white; padding: 10px; border-radius: 10px; }"
                "QPushButton:hover { background-color: #3b5166; }"
                "QPushButton:pressed { background-color: #1f2d3a; }"
            )
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn_layout.addWidget(btn)

        return btn_layout

    def init_settings_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        self.settings_screen.setLayout(layout)

        title = QLabel("Settings")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(title)

        # Main settings buttons
        blackout_btn = QPushButton("Blackout Schedule")
        blackout_btn.clicked.connect(self.show_blackout)
        user_btn = QPushButton("User Maintenance")
        user_btn.clicked.connect(self.show_user_management)

        for btn in (blackout_btn, user_btn):
            btn.setStyleSheet(
                "QPushButton { background-color: #34495e; color: white; font-size: 18px; padding: 18px; border-radius: 8px; }"
                "QPushButton:hover { background-color: #3f5f78; }"
                "QPushButton:pressed { background-color: #26394a; }"
            )
            btn.setMinimumHeight(70)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(btn)

        # Lock Settings Section
        lock_settings_group = QGroupBox("Class Access Duration")
        lock_settings_group.setStyleSheet(
            "QGroupBox { font-size: 16px; font-weight: bold; color: white; border: 2px solid #444; "
            "border-radius: 8px; margin-top: 10px; padding: 10px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        lock_layout = QVBoxLayout()
        
        self.class_duration_dropdown = QComboBox()
        self.class_duration_dropdown.addItems(["15 minutes", "30 minutes", "45 minutes", "60 minutes", "90 minutes"])
        self.class_duration_dropdown.setCurrentIndex(3)  # Default to 60 minutes
        self.class_duration_dropdown.setStyleSheet(
            "QComboBox { background-color: #2c3e50; color: white; font-size: 16px; padding: 10px; border-radius: 6px; }"
            "QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 30px; border-left: 1px solid #555; }"
            "QComboBox::down-arrow { width: 12px; height: 12px; }"
            "QComboBox QAbstractItemView { background-color: #2c3e50; color: white; selection-background-color: #34495e; }"
        )
        self.class_duration_dropdown.setMinimumHeight(45)
        lock_layout.addWidget(self.class_duration_dropdown)
        lock_settings_group.setLayout(lock_layout)
        layout.addWidget(lock_settings_group)

        layout.addStretch()

        back_btn = QPushButton("< Back to Main")
        back_btn.clicked.connect(self.show_main)
        back_btn.setStyleSheet(
            "QPushButton { background-color: #7f8c8d; color: white; font-size: 16px; padding: 12px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #95a5a6; }"
            "QPushButton:pressed { background-color: #6c7a7b; }"
        )
        back_btn.setMinimumHeight(55)
        layout.addWidget(back_btn)

    def init_log_screen(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        self.log_screen.setLayout(layout)
        
        title = QLabel("RFID Entry Log")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(title)
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet(
            "QListWidget { font-size: 13px; padding: 6px; background-color: #2c3e50; }"
            "QListWidget::item { padding: 8px; border-bottom: 1px solid #34495e; }"
            "QListWidget::item:selected { background-color: #34495e; }"
        )
        layout.addWidget(self.log_list)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_rfid_logs)
        refresh_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; font-size: 16px; padding: 10px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #5dade2; }"
            "QPushButton:pressed { background-color: #2874a6; }"
        )
        refresh_btn.setMinimumHeight(55)
        buttons_layout.addWidget(refresh_btn)

        back_btn = QPushButton("< Back to Main")
        back_btn.clicked.connect(self.show_main)
        back_btn.setStyleSheet(
            "QPushButton { background-color: #7f8c8d; color: white; font-size: 16px; padding: 12px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #95a5a6; }"
            "QPushButton:pressed { background-color: #6c7a7b; }"
        )
        back_btn.setMinimumHeight(55)
        buttons_layout.addWidget(back_btn)

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
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        self.blackout_screen.setLayout(layout)

        title = QLabel("Blackout Schedule")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QVBoxLayout()
        grid.setSpacing(6)

        self.blackout_blocks = {}
        self.block_layouts = {}

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            group = QGroupBox(day)
            group.setStyleSheet(
                "QGroupBox { font-weight: bold; font-size: 14px; border: 2px solid #444; "
                "border-radius: 6px; margin-top: 8px; padding: 8px; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
            )
            group_layout = QVBoxLayout()
            self.blackout_blocks[day] = []
            self.block_layouts[day] = group_layout

            add_btn = QPushButton("+ Add Time Block")
            add_btn.setStyleSheet(
                "QPushButton { background-color: #2c3e50; color: white; font-size: 13px; padding: 8px; border-radius: 6px; }"
                "QPushButton:hover { background-color: #3b5166; }"
                "QPushButton:pressed { background-color: #1f2d3a; }"
            )
            add_btn.clicked.connect(lambda _, d=day: self.add_time_block(d))

            group_layout.addWidget(add_btn)
            group.setLayout(group_layout)
            grid.addWidget(group)

        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        save_btn = QPushButton("Save Schedule")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-size: 16px; padding: 10px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #2ecc71; }"
            "QPushButton:pressed { background-color: #1f8a4d; }"
        )
        save_btn.setMinimumHeight(55)
        save_btn.clicked.connect(self.save_blackout_schedule)
        buttons_layout.addWidget(save_btn)

        back_btn = QPushButton("< Back")
        back_btn.setStyleSheet(
            "QPushButton { background-color: #7f8c8d; color: white; font-size: 16px; padding: 10px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #95a5a6; }"
            "QPushButton:pressed { background-color: #6c7a7b; }"
        )
        back_btn.setMinimumHeight(55)
        back_btn.clicked.connect(self.show_settings)
        buttons_layout.addWidget(back_btn)

        layout.addLayout(buttons_layout)

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

        remove_btn = QPushButton("X")
        remove_btn.setFixedSize(40, 40)
        remove_btn.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background: transparent;")

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

        with open("blackout.json", "w") as f:
            json.dump(data, f, indent=4)
        QMessageBox.information(self, "Saved", "Blackout schedule saved successfully.")
        self.set_status("Blackout schedule saved")

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
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        self.user_screen.setLayout(layout)

        title = QLabel("User Maintenance")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(title)

        self.user_list_widget = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.user_list_widget)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        add_user_btn = QPushButton("+ Add User")
        add_user_btn.setStyleSheet(
            "QPushButton { background-color: #2980b9; color: white; font-size: 16px; padding: 10px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #3498db; }"
            "QPushButton:pressed { background-color: #1f6691; }"
        )
        add_user_btn.setMinimumHeight(55)
        add_user_btn.clicked.connect(self.add_user_dialog)
        buttons_layout.addWidget(add_user_btn)

        back_btn = QPushButton("< Back")
        back_btn.setStyleSheet(
            "QPushButton { background-color: #7f8c8d; color: white; font-size: 16px; padding: 10px; border-radius: 8px; }"
            "QPushButton:hover { background-color: #95a5a6; }"
            "QPushButton:pressed { background-color: #6c7a7b; }"
        )
        back_btn.setMinimumHeight(55)
        back_btn.clicked.connect(self.show_settings)
        buttons_layout.addWidget(back_btn)

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
            group.setStyleSheet(
                "QGroupBox { background-color: #34495e; border: 1px solid #555; "
                "border-radius: 6px; padding: 6px; margin: 3px; }"
            )
            layout = QHBoxLayout()
            
            uid_label = QLabel(f"UID: {user['uid']}")
            uid_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
            layout.addWidget(uid_label)
            
            name_label = QLabel(f"Name: {user['name']}")
            name_label.setStyleSheet("font-size: 13px; color: #ecf0f1; font-weight: bold;")
            layout.addWidget(name_label)
            
            admin_label = QLabel(f"Admin: {'Yes' if user['isAdmin'] else 'No'}")
            admin_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
            layout.addWidget(admin_label)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(55, 40)
            edit_btn.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; font-size: 13px; border-radius: 6px; }"
                "QPushButton:hover { background-color: #5dade2; }"
                "QPushButton:pressed { background-color: #2874a6; }"
            )
            edit_btn.clicked.connect(lambda _, u=user: self.edit_user_dialog(u))

            del_btn = QPushButton("Del")
            del_btn.setFixedSize(55, 40)
            del_btn.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white; font-size: 13px; border-radius: 6px; }"
                "QPushButton:hover { background-color: #ec7063; }"
                "QPushButton:pressed { background-color: #c0392b; }"
            )
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
        with open("users.json", "w") as f:
            json.dump(self.users, f, indent=4)
        self.set_status("Users saved")

    def request_password(self):
        dlg = PasswordDialog(self)
        if dlg.exec_():
            if dlg.get_password() == "admin":
                self.show_settings()

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
    window.show()
    sys.exit(app.exec_())