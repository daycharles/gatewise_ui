"""
Garage Door Control Module

Provides GPIO control for garage door relay and physical button monitoring.
Designed for Raspberry Pi with relay module for triggering garage door opener.

Safety features:
- Momentary pulse activation (default 250ms)
- Debounce on physical button input
- Optional door state sensor support
"""

import os
import time
import threading

# Try to import GPIO library - will fail on non-Raspberry Pi systems
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[WARNING] RPi.GPIO not available. Garage control will be disabled.")


class GarageController:
    """
    Controls garage door via GPIO relay and monitors physical button.
    
    Configuration via environment variables:
    - GARAGE_RELAY_PIN: GPIO pin for relay (default: 17)
    - GARAGE_BUTTON_PIN: GPIO pin for physical button (default: 27)
    - GARAGE_PULSE_MS: Relay pulse duration in milliseconds (default: 250)
    """
    
    def __init__(self):
        self.enabled = GPIO_AVAILABLE
        self.relay_pin = int(os.environ.get('GARAGE_RELAY_PIN', '17'))
        self.button_pin = int(os.environ.get('GARAGE_BUTTON_PIN', '27'))
        self.pulse_duration = int(os.environ.get('GARAGE_PULSE_MS', '250')) / 1000.0
        
        self.button_callback = None
        self.last_button_press = 0
        self.debounce_time = 0.3  # 300ms debounce
        
        if self.enabled:
            self._setup_gpio()
    
    def _setup_gpio(self):
        """Initialize GPIO pins for relay and button."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup relay pin as output (default LOW/off)
            GPIO.setup(self.relay_pin, GPIO.OUT)
            GPIO.output(self.relay_pin, GPIO.LOW)
            
            # Setup button pin as input with pull-up resistor
            GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Add event detection for button (falling edge = button pressed)
            GPIO.add_event_detect(
                self.button_pin,
                GPIO.FALLING,
                callback=self._button_pressed_handler,
                bouncetime=300
            )
            
            print(f"[INFO] Garage control initialized - Relay: GPIO{self.relay_pin}, Button: GPIO{self.button_pin}")
        except Exception as e:
            print(f"[ERROR] Failed to setup GPIO: {e}")
            self.enabled = False
    
    def _button_pressed_handler(self, channel):
        """Handle physical button press with debounce."""
        current_time = time.time()
        
        # Debounce check
        if current_time - self.last_button_press < self.debounce_time:
            return
        
        self.last_button_press = current_time
        print("[INFO] Physical garage button pressed")
        
        # Call registered callback if any
        if self.button_callback:
            try:
                self.button_callback()
            except Exception as e:
                print(f"[ERROR] Button callback failed: {e}")
    
    def trigger_door(self):
        """
        Trigger garage door opener with momentary pulse.
        
        Returns:
            bool: True if successful, False if GPIO not available or error
        """
        if not self.enabled:
            print("[WARNING] Garage control not available (GPIO not initialized)")
            return False
        
        try:
            print(f"[INFO] Triggering garage door relay (pulse: {self.pulse_duration*1000:.0f}ms)")
            
            # Momentary pulse: HIGH then LOW
            GPIO.output(self.relay_pin, GPIO.HIGH)
            time.sleep(self.pulse_duration)
            GPIO.output(self.relay_pin, GPIO.LOW)
            
            print("[INFO] Garage door trigger complete")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to trigger garage door: {e}")
            return False
    
    def trigger_door_async(self, callback=None):
        """
        Trigger garage door in separate thread to avoid blocking UI.
        
        Args:
            callback: Optional function to call after trigger completes (takes success bool)
        """
        def _trigger():
            success = self.trigger_door()
            if callback:
                callback(success)
        
        thread = threading.Thread(target=_trigger, daemon=True)
        thread.start()
    
    def set_button_callback(self, callback):
        """
        Register callback for physical button presses.
        
        Args:
            callback: Function to call when physical button is pressed (no arguments)
        """
        self.button_callback = callback
        print("[INFO] Garage button callback registered")
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if self.enabled:
            try:
                GPIO.cleanup()
                print("[INFO] GPIO cleanup complete")
            except Exception as e:
                print(f"[ERROR] GPIO cleanup failed: {e}")
    
    def is_enabled(self):
        """Check if garage control is available."""
        return self.enabled


# Singleton instance
_garage_controller = None

def get_garage_controller():
    """Get or create the global garage controller instance."""
    global _garage_controller
    if _garage_controller is None:
        _garage_controller = GarageController()
    return _garage_controller
