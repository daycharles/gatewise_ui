"""
Tests for the configuration module.
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config, get_config, str_to_bool


class TestConfig(unittest.TestCase):
    """Test configuration loading and management."""
    
    def setUp(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        
    def tearDown(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_str_to_bool(self):
        """Test string to boolean conversion."""
        self.assertTrue(str_to_bool('true'))
        self.assertTrue(str_to_bool('True'))
        self.assertTrue(str_to_bool('TRUE'))
        self.assertTrue(str_to_bool('1'))
        self.assertTrue(str_to_bool('yes'))
        self.assertTrue(str_to_bool('on'))
        self.assertTrue(str_to_bool('enabled'))
        
        self.assertFalse(str_to_bool('false'))
        self.assertFalse(str_to_bool('False'))
        self.assertFalse(str_to_bool('0'))
        self.assertFalse(str_to_bool('no'))
        self.assertFalse(str_to_bool('off'))
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        # Should have fallback admin password
        self.assertEqual(config.admin_password, 'admin')
        
        # Garage should be disabled by default
        self.assertFalse(config.garage_enabled)
        
        # RFID should be enabled by default
        self.assertTrue(config.rfid_enabled)
        
        # Default pins
        self.assertEqual(config.garage_relay_pin, 17)
        self.assertEqual(config.garage_button_pin, 27)
    
    def test_env_password(self):
        """Test password from environment variable."""
        os.environ['GATEWISE_ADMIN_PASSWORD'] = 'test_password_123'
        config = Config()
        self.assertEqual(config.admin_password, 'test_password_123')
    
    def test_garage_config(self):
        """Test garage configuration."""
        os.environ['GARAGE_ENABLED'] = 'true'
        os.environ['GARAGE_RELAY_PIN'] = '22'
        os.environ['GARAGE_BUTTON_PIN'] = '23'
        os.environ['GARAGE_RELAY_PULSE_MS'] = '1000'
        
        config = Config()
        
        self.assertTrue(config.garage_enabled)
        self.assertEqual(config.garage_relay_pin, 22)
        self.assertEqual(config.garage_button_pin, 23)
        self.assertEqual(config.garage_relay_pulse_ms, 1000)
    
    def test_window_size_parsing(self):
        """Test window size parsing."""
        os.environ['WINDOW_SIZE'] = '1024x768'
        config = Config()
        
        self.assertEqual(config.window_width, 1024)
        self.assertEqual(config.window_height, 768)
    
    def test_door_module_ips(self):
        """Test door module IP parsing."""
        os.environ['DOOR_MODULE_IPS'] = '192.168.1.10,192.168.1.11,192.168.1.12'
        config = Config()
        
        self.assertEqual(len(config.door_module_ips), 3)
        self.assertIn('192.168.1.10', config.door_module_ips)
        self.assertIn('192.168.1.11', config.door_module_ips)
        self.assertIn('192.168.1.12', config.door_module_ips)


if __name__ == '__main__':
    unittest.main()
