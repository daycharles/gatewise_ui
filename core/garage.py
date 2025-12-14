"""
Garage Door Controller Module

Handles garage door control via relay and button input with safety features.
"""

import time
import threading
import json
import os
from datetime import datetime
from typing import Optional, Callable
from core.gpio_abstraction import GPIOInterface, get_gpio
from core.config import get_config


class GarageDoorState:
    """Garage door state enumeration."""
    UNKNOWN = "unknown"
    OPEN = "open"
    CLOSED = "closed"
    OPENING = "opening"
    CLOSING = "closing"


class GarageDoorController:
    """
    Manages garage door control with relay and button input.
    
    Features:
    - Relay pulse for door trigger (simulates button press)
    - Button input with debouncing
    - Optional door state sensor
    - Safety checks and timeouts
    - Event logging
    - State persistence
    """
    
    def __init__(self, 
                 gpio: Optional[GPIOInterface] = None,
                 config = None,
                 event_callback: Optional[Callable] = None):
        """
        Initialize garage door controller.
        
        Args:
            gpio: GPIO interface (if None, auto-detected)
            config: Configuration object (if None, loaded from global config)
            event_callback: Callback for events (door opened, closed, etc.)
        """
        self.config = config or get_config()
        self.gpio = gpio or get_gpio()
        self.event_callback = event_callback
        
        # Configuration
        self.relay_pin = self.config.garage_relay_pin
        self.button_pin = self.config.garage_button_pin
        self.sensor_pin = self.config.garage_sensor_pin
        self.relay_active_low = self.config.garage_relay_active_low
        self.sensor_active_low = self.config.garage_sensor_active_low
        self.pulse_duration_ms = self.config.garage_relay_pulse_ms
        self.auto_close_seconds = self.config.garage_auto_close_seconds
        
        # State
        self.current_state = GarageDoorState.UNKNOWN
        self.last_trigger_time = None
        self.auto_close_timer = None
        self._lock = threading.Lock()
        
        # Initialize GPIO
        self._init_gpio()
        
        # Load persisted state
        self._load_state()
        
        print(f"[GARAGE] Controller initialized")
        print(f"[GARAGE] Relay pin: GPIO{self.relay_pin}, Button pin: GPIO{self.button_pin}")
        if self.sensor_pin:
            print(f"[GARAGE] Sensor pin: GPIO{self.sensor_pin}")
    
    def _init_gpio(self):
        """Initialize GPIO pins."""
        try:
            # Set BCM pin numbering
            self.gpio.setmode(self.gpio.BCM)
            
            # Setup relay pin (output)
            self.gpio.setup(self.relay_pin, self.gpio.OUT)
            # Set relay to inactive state
            inactive_state = self.gpio.LOW if self.relay_active_low else self.gpio.HIGH
            self.gpio.output(self.relay_pin, inactive_state)
            
            # Setup button pin (input with pull-up)
            self.gpio.setup(self.button_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
            # Add button press detection (falling edge for active-low button)
            self.gpio.add_event_detect(
                self.button_pin,
                self.gpio.FALLING,
                callback=self._button_callback,
                bouncetime=300  # 300ms debounce
            )
            
            # Setup sensor pin if configured
            if self.sensor_pin:
                self.gpio.setup(self.sensor_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
                # Add sensor change detection
                self.gpio.add_event_detect(
                    self.sensor_pin,
                    self.gpio.BOTH,
                    callback=self._sensor_callback,
                    bouncetime=100
                )
                # Read initial state
                self._update_state_from_sensor()
            
            print("[GARAGE] GPIO initialized successfully")
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to initialize GPIO: {e}")
            raise
    
    def _update_state_from_sensor(self):
        """Update door state from sensor reading."""
        if not self.sensor_pin:
            return
        
        try:
            sensor_value = self.gpio.input(self.sensor_pin)
            # If sensor is active-low, invert the reading
            is_closed = (sensor_value == self.gpio.LOW) if self.sensor_active_low else (sensor_value == self.gpio.HIGH)
            
            new_state = GarageDoorState.CLOSED if is_closed else GarageDoorState.OPEN
            if new_state != self.current_state:
                old_state = self.current_state
                self.current_state = new_state
                self._log_event(f"Door state changed: {old_state} -> {new_state}")
                self._save_state()
                if self.event_callback:
                    self.event_callback("state_changed", new_state)
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to read sensor: {e}")
    
    def _sensor_callback(self, channel):
        """Callback for sensor state change."""
        self._update_state_from_sensor()
    
    def _button_callback(self, channel):
        """Callback for button press."""
        print(f"[GARAGE] Manual button pressed on GPIO{channel}")
        self._log_event("Manual button pressed")
        # Trigger the relay when button is pressed
        threading.Thread(target=self.trigger, args=("manual_button",), daemon=True).start()
    
    def trigger(self, source: str = "manual") -> bool:
        """
        Trigger the garage door relay.
        
        Args:
            source: Source of trigger (e.g., "manual", "ui", "automation")
        
        Returns:
            True if triggered successfully, False otherwise
        """
        with self._lock:
            # Safety check: don't trigger too frequently
            if self.last_trigger_time:
                elapsed = time.time() - self.last_trigger_time
                if elapsed < 1.0:  # Minimum 1 second between triggers
                    print(f"[GARAGE] Trigger ignored (too soon after last trigger)")
                    return False
            
            try:
                print(f"[GARAGE] Triggering relay (source: {source})")
                
                # Pulse the relay
                active_state = self.gpio.LOW if self.relay_active_low else self.gpio.HIGH
                inactive_state = self.gpio.HIGH if self.relay_active_low else self.gpio.LOW
                
                # Activate relay
                self.gpio.output(self.relay_pin, active_state)
                time.sleep(self.pulse_duration_ms / 1000.0)
                # Deactivate relay
                self.gpio.output(self.relay_pin, inactive_state)
                
                self.last_trigger_time = time.time()
                self._log_event(f"Door triggered by {source}")
                
                # Update state
                if self.current_state == GarageDoorState.CLOSED:
                    self.current_state = GarageDoorState.OPENING
                elif self.current_state == GarageDoorState.OPEN:
                    self.current_state = GarageDoorState.CLOSING
                
                self._save_state()
                
                if self.event_callback:
                    self.event_callback("triggered", source)
                
                # Schedule auto-close if enabled and door is opening
                if self.auto_close_seconds > 0 and self.current_state == GarageDoorState.OPENING:
                    self._schedule_auto_close()
                
                return True
            
            except Exception as e:
                print(f"[GARAGE ERROR] Failed to trigger relay: {e}")
                self._log_event(f"ERROR: Failed to trigger relay: {e}")
                return False
    
    def _schedule_auto_close(self):
        """Schedule automatic door close."""
        # Cancel existing timer
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
        
        print(f"[GARAGE] Scheduling auto-close in {self.auto_close_seconds} seconds")
        self.auto_close_timer = threading.Timer(
            self.auto_close_seconds,
            self._auto_close_callback
        )
        self.auto_close_timer.daemon = True
        self.auto_close_timer.start()
    
    def _auto_close_callback(self):
        """Callback for auto-close timer."""
        print("[GARAGE] Auto-close triggered")
        if self.current_state == GarageDoorState.OPEN:
            self.trigger("auto_close")
        else:
            print("[GARAGE] Auto-close skipped (door not open)")
    
    def cancel_auto_close(self):
        """Cancel scheduled auto-close."""
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
            self.auto_close_timer = None
            print("[GARAGE] Auto-close cancelled")
            self._log_event("Auto-close cancelled")
    
    def get_state(self) -> str:
        """Get current door state."""
        return self.current_state
    
    def is_open(self) -> bool:
        """Check if door is open."""
        return self.current_state == GarageDoorState.OPEN
    
    def is_closed(self) -> bool:
        """Check if door is closed."""
        return self.current_state == GarageDoorState.CLOSED
    
    def _log_event(self, message: str):
        """Log garage event."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        print(f"[GARAGE LOG] {message}")
        
        # Append to log file
        try:
            log_file = "garage_events.log"
            with open(log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to write log: {e}")
    
    def _save_state(self):
        """Save current state to file."""
        try:
            state_data = {
                "state": self.current_state,
                "last_trigger_time": self.last_trigger_time,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.config.garage_state_file, "w") as f:
                json.dump(state_data, f, indent=4)
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to save state: {e}")
    
    def _load_state(self):
        """Load persisted state from file."""
        try:
            if os.path.exists(self.config.garage_state_file):
                with open(self.config.garage_state_file, "r") as f:
                    state_data = json.load(f)
                    self.current_state = state_data.get("state", GarageDoorState.UNKNOWN)
                    self.last_trigger_time = state_data.get("last_trigger_time")
                    print(f"[GARAGE] Loaded state: {self.current_state}")
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to load state: {e}")
    
    def get_recent_events(self, count: int = 10) -> list:
        """
        Get recent garage events from log.
        
        Args:
            count: Number of recent events to retrieve
        
        Returns:
            List of recent event strings
        """
        try:
            log_file = "garage_events.log"
            if not os.path.exists(log_file):
                return []
            
            with open(log_file, "r") as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-count:]]
        except Exception as e:
            print(f"[GARAGE ERROR] Failed to read events: {e}")
            return []
    
    def cleanup(self):
        """Clean up GPIO resources."""
        print("[GARAGE] Cleaning up...")
        
        # Cancel auto-close timer
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
        
        # Clean up GPIO
        try:
            self.gpio.cleanup(self.relay_pin)
            self.gpio.cleanup(self.button_pin)
            if self.sensor_pin:
                self.gpio.cleanup(self.sensor_pin)
            print("[GARAGE] Cleanup completed")
        except Exception as e:
            print(f"[GARAGE ERROR] Cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
