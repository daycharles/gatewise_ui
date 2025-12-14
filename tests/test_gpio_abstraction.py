"""
Tests for GPIO abstraction layer.
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gpio_abstraction import (
    GPIOInterface, MockGPIO, get_gpio, is_raspberry_pi
)


class TestGPIOAbstraction(unittest.TestCase):
    """Test GPIO abstraction layer."""
    
    def test_is_raspberry_pi(self):
        """Test Raspberry Pi detection."""
        result = is_raspberry_pi()
        self.assertIsInstance(result, bool)
    
    def test_get_gpio_returns_interface(self):
        """Test get_gpio returns a GPIOInterface."""
        gpio = get_gpio()
        self.assertIsInstance(gpio, GPIOInterface)
    
    def test_mock_gpio_constants(self):
        """Test MockGPIO has required constants."""
        gpio = MockGPIO()
        
        # Pin modes
        self.assertIsNotNone(gpio.IN)
        self.assertIsNotNone(gpio.OUT)
        
        # Pin states
        self.assertIsNotNone(gpio.HIGH)
        self.assertIsNotNone(gpio.LOW)
        
        # Pull resistors
        self.assertIsNotNone(gpio.PUD_UP)
        self.assertIsNotNone(gpio.PUD_DOWN)
        self.assertIsNotNone(gpio.PUD_OFF)
        
        # Edge detection
        self.assertIsNotNone(gpio.RISING)
        self.assertIsNotNone(gpio.FALLING)
        self.assertIsNotNone(gpio.BOTH)
    
    def test_mock_gpio_pin_operations(self):
        """Test MockGPIO basic operations."""
        gpio = MockGPIO()
        
        # Setup output pin
        gpio.setup(17, gpio.OUT)
        self.assertIn(17, gpio.pin_modes)
        
        # Set output
        gpio.output(17, gpio.HIGH)
        self.assertEqual(gpio.pin_states[17], gpio.HIGH)
        
        # Read output (since we wrote to it)
        state = gpio.input(17)
        self.assertEqual(state, gpio.HIGH)
    
    def test_mock_gpio_input_with_pullup(self):
        """Test input pin with pull-up."""
        gpio = MockGPIO()
        gpio.setup(27, gpio.IN, pull_up_down=gpio.PUD_UP)
        self.assertIn(27, gpio.pin_modes)
    
    def test_mock_gpio_cleanup(self):
        """Test cleanup functionality."""
        gpio = MockGPIO()
        
        gpio.setup(17, gpio.OUT)
        gpio.setup(27, gpio.IN)
        
        # Cleanup single pin
        gpio.cleanup(17)
        self.assertNotIn(17, gpio.pin_modes)
        self.assertIn(27, gpio.pin_modes)
        
        # Cleanup all
        gpio.cleanup()
        self.assertEqual(len(gpio.pin_modes), 0)


if __name__ == '__main__':
    unittest.main()
