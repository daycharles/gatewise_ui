"""
Tests for the garage door controller module.
"""

import os
import sys
import unittest
import time
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.garage import GarageDoorController, GarageDoorState
from core.gpio_abstraction import MockGPIO
from core.config import Config


class TestGarageDoorController(unittest.TestCase):
    """Test garage door controller functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Set test environment variables
        os.environ['GARAGE_ENABLED'] = 'true'
        os.environ['GARAGE_RELAY_PIN'] = '17'
        os.environ['GARAGE_BUTTON_PIN'] = '27'
        os.environ['GARAGE_RELAY_PULSE_MS'] = '100'  # Short pulse for testing
        os.environ['GARAGE_STATE_FILE'] = 'test_garage_state.json'
        
        # Clean up any existing state file
        if os.path.exists('test_garage_state.json'):
            os.remove('test_garage_state.json')
        
        # Create mock GPIO
        self.gpio = MockGPIO()
        
        # Create config
        self.config = Config()
        
        # Create controller with mock GPIO
        self.controller = GarageDoorController(gpio=self.gpio, config=self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
        
        # Clean up test state file
        if os.path.exists('test_garage_state.json'):
            os.remove('test_garage_state.json')
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.relay_pin, 17)
        self.assertEqual(self.controller.button_pin, 27)
        self.assertEqual(self.controller.current_state, GarageDoorState.UNKNOWN)
    
    def test_trigger(self):
        """Test relay trigger."""
        result = self.controller.trigger("test")
        self.assertTrue(result)
        self.assertIsNotNone(self.controller.last_trigger_time)
    
    def test_trigger_rate_limit(self):
        """Test that triggers are rate limited."""
        # First trigger should succeed
        result1 = self.controller.trigger("test1")
        self.assertTrue(result1)
        
        # Second trigger immediately after should fail
        result2 = self.controller.trigger("test2")
        self.assertFalse(result2)
        
        # After waiting, trigger should succeed
        time.sleep(1.1)
        result3 = self.controller.trigger("test3")
        self.assertTrue(result3)
    
    def test_state_transitions(self):
        """Test door state transitions."""
        # Set state to closed
        self.controller.current_state = GarageDoorState.CLOSED
        
        # Trigger should change state to opening
        self.controller.trigger("test")
        self.assertEqual(self.controller.current_state, GarageDoorState.OPENING)
    
    def test_get_state(self):
        """Test getting current state."""
        state = self.controller.get_state()
        self.assertIn(state, [
            GarageDoorState.UNKNOWN,
            GarageDoorState.OPEN,
            GarageDoorState.CLOSED,
            GarageDoorState.OPENING,
            GarageDoorState.CLOSING
        ])
    
    def test_is_open(self):
        """Test is_open check."""
        self.controller.current_state = GarageDoorState.OPEN
        self.assertTrue(self.controller.is_open())
        
        self.controller.current_state = GarageDoorState.CLOSED
        self.assertFalse(self.controller.is_open())
    
    def test_is_closed(self):
        """Test is_closed check."""
        self.controller.current_state = GarageDoorState.CLOSED
        self.assertTrue(self.controller.is_closed())
        
        self.controller.current_state = GarageDoorState.OPEN
        self.assertFalse(self.controller.is_closed())
    
    def test_event_callback(self):
        """Test event callback is called."""
        callback_data = []
        
        def test_callback(event_type, data):
            callback_data.append((event_type, data))
        
        # Create controller with callback
        controller = GarageDoorController(
            gpio=self.gpio,
            config=self.config,
            event_callback=test_callback
        )
        
        # Trigger should call callback
        controller.trigger("test")
        
        # Check callback was called
        self.assertTrue(len(callback_data) > 0)
        self.assertEqual(callback_data[-1][0], "triggered")
        
        controller.cleanup()
    
    def test_cancel_auto_close(self):
        """Test canceling auto-close."""
        # Enable auto-close
        self.controller.auto_close_seconds = 5
        self.controller.current_state = GarageDoorState.CLOSED
        
        # Trigger to schedule auto-close
        self.controller.trigger("test")
        self.assertIsNotNone(self.controller.auto_close_timer)
        
        # Cancel auto-close
        time.sleep(1.1)  # Wait for rate limit
        self.controller.cancel_auto_close()
        self.assertIsNone(self.controller.auto_close_timer)
    
    def test_get_recent_events(self):
        """Test getting recent events."""
        # Trigger a few times to generate events
        self.controller.trigger("test1")
        time.sleep(1.1)
        self.controller.trigger("test2")
        
        # Get events
        events = self.controller.get_recent_events(5)
        self.assertIsInstance(events, list)


class TestMockGPIO(unittest.TestCase):
    """Test mock GPIO functionality."""
    
    def setUp(self):
        """Set up test GPIO."""
        self.gpio = MockGPIO()
    
    def test_setup(self):
        """Test pin setup."""
        self.gpio.setup(17, self.gpio.OUT)
        self.assertIn(17, self.gpio.pin_modes)
        self.assertEqual(self.gpio.pin_modes[17], self.gpio.OUT)
    
    def test_output(self):
        """Test pin output."""
        self.gpio.setup(17, self.gpio.OUT)
        self.gpio.output(17, self.gpio.HIGH)
        self.assertEqual(self.gpio.pin_states[17], self.gpio.HIGH)
    
    def test_input(self):
        """Test pin input."""
        self.gpio.setup(27, self.gpio.IN)
        state = self.gpio.input(27)
        self.assertIn(state, [self.gpio.HIGH, self.gpio.LOW])
    
    def test_event_detect(self):
        """Test event detection."""
        callback_called = []
        
        def test_callback(channel):
            callback_called.append(channel)
        
        self.gpio.setup(27, self.gpio.IN)
        self.gpio.add_event_detect(27, self.gpio.FALLING, test_callback)
        
        # Simulate button press
        self.gpio.simulate_button_press(27)
        
        # Check callback was called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], 27)
    
    def test_cleanup(self):
        """Test GPIO cleanup."""
        self.gpio.setup(17, self.gpio.OUT)
        self.gpio.setup(27, self.gpio.IN)
        
        self.gpio.cleanup(17)
        self.assertNotIn(17, self.gpio.pin_modes)
        self.assertIn(27, self.gpio.pin_modes)
        
        self.gpio.cleanup()
        self.assertEqual(len(self.gpio.pin_modes), 0)


if __name__ == '__main__':
    unittest.main()
