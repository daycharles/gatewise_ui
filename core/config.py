"""
GateWise Configuration Management

Loads configuration from environment variables and .env files.
Provides centralized access to all application settings.
"""

import os
from typing import Any, Optional


def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')


class Config:
    """Application configuration loader and manager."""
    
    def __init__(self):
        """Initialize configuration by loading from environment."""
        self._load_env_file()
        self._load_settings()
    
    def _load_env_file(self):
        """Load .env file if it exists."""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Only set if not already in environment
                            if key not in os.environ:
                                os.environ[key] = value
            except Exception as e:
                print(f"[WARNING] Failed to load .env file: {e}")
    
    def _load_settings(self):
        """Load all configuration settings from environment."""
        # Security
        self.admin_password = os.environ.get('GATEWISE_ADMIN_PASSWORD', None)
        if not self.admin_password:
            print("[WARNING] GATEWISE_ADMIN_PASSWORD not set! Using insecure default.")
            print("[WARNING] Set environment variable GATEWISE_ADMIN_PASSWORD for security!")
            self.admin_password = 'admin'  # Fallback for development only
        
        # Garage Door Settings
        self.garage_enabled = str_to_bool(os.environ.get('GARAGE_ENABLED', 'false'))
        self.garage_relay_pin = int(os.environ.get('GARAGE_RELAY_PIN', '17'))
        self.garage_relay_active_low = str_to_bool(os.environ.get('GARAGE_RELAY_ACTIVE_LOW', 'true'))
        self.garage_relay_pulse_ms = int(os.environ.get('GARAGE_RELAY_PULSE_MS', '500'))
        self.garage_button_pin = int(os.environ.get('GARAGE_BUTTON_PIN', '27'))
        self.garage_sensor_pin = os.environ.get('GARAGE_SENSOR_PIN', '')
        self.garage_sensor_pin = int(self.garage_sensor_pin) if self.garage_sensor_pin else None
        self.garage_sensor_active_low = str_to_bool(os.environ.get('GARAGE_SENSOR_ACTIVE_LOW', 'true'))
        self.garage_auto_close_seconds = int(os.environ.get('GARAGE_AUTO_CLOSE_SECONDS', '0'))
        
        # RFID Settings
        self.rfid_enabled = str_to_bool(os.environ.get('RFID_ENABLED', 'true'))
        self.rfid_type = os.environ.get('RFID_TYPE', 'mfrc522')
        
        # Door Module Network Settings
        door_ips = os.environ.get('DOOR_MODULE_IPS', '192.168.0.51')
        self.door_module_ips = [ip.strip() for ip in door_ips.split(',') if ip.strip()]
        self.door_module_port = int(os.environ.get('DOOR_MODULE_PORT', '5006'))
        
        # Application Settings
        self.app_title = os.environ.get('APP_TITLE', 'GateWise Home Access Control')
        self.primary_color = os.environ.get('PRIMARY_COLOR', '#355265')
        self.debug_mode = str_to_bool(os.environ.get('DEBUG_MODE', 'false'))
        self.log_file = os.environ.get('LOG_FILE', 'gatewise.log')
        self.log_max_size_mb = int(os.environ.get('LOG_MAX_SIZE_MB', '10'))
        self.log_backup_count = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
        
        # UI Settings
        window_size = os.environ.get('WINDOW_SIZE', '800x480')
        width, height = window_size.split('x')
        self.window_width = int(width)
        self.window_height = int(height)
        self.fullscreen = str_to_bool(os.environ.get('FULLSCREEN', 'false'))
        self.show_cursor = str_to_bool(os.environ.get('SHOW_CURSOR', 'true'))
        
        # Data Persistence
        self.users_file = os.environ.get('USERS_FILE', 'users.json')
        self.blackout_file = os.environ.get('BLACKOUT_FILE', 'blackout.json')
        self.garage_state_file = os.environ.get('GARAGE_STATE_FILE', 'garage_state.json')
        self.auto_backup_hours = int(os.environ.get('AUTO_BACKUP_HOURS', '0'))
        self.backup_dir = os.environ.get('BACKUP_DIR', 'backups')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key, default)
    
    def is_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def print_config(self):
        """Print current configuration (excluding sensitive data)."""
        print("=" * 60)
        print("GateWise Configuration")
        print("=" * 60)
        print(f"Admin Password: {'SET' if self.admin_password != 'admin' else 'NOT SET (USING DEFAULT!)'}")
        print(f"Garage Enabled: {self.garage_enabled}")
        if self.garage_enabled:
            print(f"  Relay Pin: GPIO{self.garage_relay_pin}")
            print(f"  Button Pin: GPIO{self.garage_button_pin}")
            print(f"  Sensor Pin: {'GPIO' + str(self.garage_sensor_pin) if self.garage_sensor_pin else 'None'}")
            print(f"  Pulse Duration: {self.garage_relay_pulse_ms}ms")
        print(f"RFID Enabled: {self.rfid_enabled}")
        print(f"Door Modules: {', '.join(self.door_module_ips)}")
        print(f"Debug Mode: {self.debug_mode}")
        print(f"Window Size: {self.window_width}x{self.window_height}")
        print(f"Running on Raspberry Pi: {self.is_raspberry_pi()}")
        print("=" * 60)


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config():
    """Reload configuration from environment."""
    global _config
    _config = Config()
    return _config
