"""
GPIO Abstraction Layer

Provides a unified interface for GPIO operations that works on Raspberry Pi
and provides mock implementations for development on other platforms.
"""

import sys
from typing import Callable, Optional


class GPIOInterface:
    """Base interface for GPIO operations."""
    
    # Pin modes
    IN = "IN"
    OUT = "OUT"
    
    # Pin states
    HIGH = 1
    LOW = 0
    
    # Pull resistors
    PUD_UP = "PUD_UP"
    PUD_DOWN = "PUD_DOWN"
    PUD_OFF = "PUD_OFF"
    
    # Edge detection
    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"
    
    def setup(self, pin: int, mode: str, pull_up_down: Optional[str] = None):
        """Configure a GPIO pin."""
        raise NotImplementedError
    
    def output(self, pin: int, state: int):
        """Set output pin state."""
        raise NotImplementedError
    
    def input(self, pin: int) -> int:
        """Read input pin state."""
        raise NotImplementedError
    
    def add_event_detect(self, pin: int, edge: str, callback: Callable, bouncetime: int = 200):
        """Add edge detection callback."""
        raise NotImplementedError
    
    def remove_event_detect(self, pin: int):
        """Remove edge detection from pin."""
        raise NotImplementedError
    
    def cleanup(self, pin: Optional[int] = None):
        """Clean up GPIO resources."""
        raise NotImplementedError
    
    def setmode(self, mode):
        """Set pin numbering mode."""
        raise NotImplementedError


class RPiGPIO(GPIOInterface):
    """Raspberry Pi GPIO implementation using RPi.GPIO."""
    
    def __init__(self):
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.BCM = GPIO.BCM
            self.BOARD = GPIO.BOARD
            print("[INFO] RPi.GPIO loaded successfully")
        except ImportError:
            raise ImportError("RPi.GPIO not available. Install with: pip install RPi.GPIO")
    
    def setup(self, pin: int, mode: str, pull_up_down: Optional[str] = None):
        gpio_mode = self.GPIO.IN if mode == self.IN else self.GPIO.OUT
        kwargs = {}
        if pull_up_down:
            if pull_up_down == self.PUD_UP:
                kwargs['pull_up_down'] = self.GPIO.PUD_UP
            elif pull_up_down == self.PUD_DOWN:
                kwargs['pull_up_down'] = self.GPIO.PUD_DOWN
        self.GPIO.setup(pin, gpio_mode, **kwargs)
    
    def output(self, pin: int, state: int):
        self.GPIO.output(pin, state)
    
    def input(self, pin: int) -> int:
        return self.GPIO.input(pin)
    
    def add_event_detect(self, pin: int, edge: str, callback: Callable, bouncetime: int = 200):
        gpio_edge = {
            self.RISING: self.GPIO.RISING,
            self.FALLING: self.GPIO.FALLING,
            self.BOTH: self.GPIO.BOTH
        }[edge]
        self.GPIO.add_event_detect(pin, gpio_edge, callback=callback, bouncetime=bouncetime)
    
    def remove_event_detect(self, pin: int):
        self.GPIO.remove_event_detect(pin)
    
    def cleanup(self, pin: Optional[int] = None):
        if pin:
            self.GPIO.cleanup(pin)
        else:
            self.GPIO.cleanup()
    
    def setmode(self, mode):
        self.GPIO.setmode(mode)


class GPIOZero(GPIOInterface):
    """GPIO implementation using gpiozero (simpler high-level library)."""
    
    def __init__(self):
        try:
            import gpiozero
            self.gpiozero = gpiozero
            self.devices = {}
            self.BCM = "BCM"  # gpiozero always uses BCM
            self.BOARD = "BCM"
            print("[INFO] gpiozero loaded successfully")
        except ImportError:
            raise ImportError("gpiozero not available. Install with: pip install gpiozero")
    
    def setup(self, pin: int, mode: str, pull_up_down: Optional[str] = None):
        if mode == self.OUT:
            self.devices[pin] = self.gpiozero.OutputDevice(pin)
        else:
            pull = None
            if pull_up_down == self.PUD_UP:
                pull = True
            elif pull_up_down == self.PUD_DOWN:
                pull = False
            self.devices[pin] = self.gpiozero.Button(pin, pull_up=pull)
    
    def output(self, pin: int, state: int):
        device = self.devices.get(pin)
        if device:
            if state == self.HIGH:
                device.on()
            else:
                device.off()
    
    def input(self, pin: int) -> int:
        device = self.devices.get(pin)
        if device:
            return self.HIGH if device.is_pressed else self.LOW
        return self.LOW
    
    def add_event_detect(self, pin: int, edge: str, callback: Callable, bouncetime: int = 200):
        device = self.devices.get(pin)
        if device and hasattr(device, 'when_pressed'):
            bounce_time = bouncetime / 1000.0  # Convert ms to seconds
            if edge == self.RISING or edge == self.BOTH:
                device.when_pressed = callback
            if edge == self.FALLING or edge == self.BOTH:
                device.when_released = callback
            device.bounce_time = bounce_time
    
    def remove_event_detect(self, pin: int):
        device = self.devices.get(pin)
        if device:
            if hasattr(device, 'when_pressed'):
                device.when_pressed = None
            if hasattr(device, 'when_released'):
                device.when_released = None
    
    def cleanup(self, pin: Optional[int] = None):
        if pin:
            device = self.devices.get(pin)
            if device:
                device.close()
                del self.devices[pin]
        else:
            for device in self.devices.values():
                device.close()
            self.devices.clear()
    
    def setmode(self, mode):
        pass  # gpiozero doesn't need mode setting


class MockGPIO(GPIOInterface):
    """Mock GPIO implementation for development on non-Pi systems."""
    
    def __init__(self):
        self.pin_states = {}
        self.pin_modes = {}
        self.callbacks = {}
        self.BCM = "BCM"
        self.BOARD = "BOARD"
        print("[INFO] Using MockGPIO (no real hardware)")
    
    def setup(self, pin: int, mode: str, pull_up_down: Optional[str] = None):
        self.pin_modes[pin] = mode
        self.pin_states[pin] = self.LOW
        print(f"[MOCK GPIO] Setup pin {pin} as {mode}" + 
              (f" with {pull_up_down}" if pull_up_down else ""))
    
    def output(self, pin: int, state: int):
        self.pin_states[pin] = state
        print(f"[MOCK GPIO] Set pin {pin} to {'HIGH' if state == self.HIGH else 'LOW'}")
    
    def input(self, pin: int) -> int:
        state = self.pin_states.get(pin, self.LOW)
        print(f"[MOCK GPIO] Read pin {pin}: {'HIGH' if state == self.HIGH else 'LOW'}")
        return state
    
    def add_event_detect(self, pin: int, edge: str, callback: Callable, bouncetime: int = 200):
        self.callbacks[pin] = (edge, callback, bouncetime)
        print(f"[MOCK GPIO] Added {edge} edge detection on pin {pin} (bounce={bouncetime}ms)")
    
    def remove_event_detect(self, pin: int):
        if pin in self.callbacks:
            del self.callbacks[pin]
            print(f"[MOCK GPIO] Removed edge detection from pin {pin}")
    
    def cleanup(self, pin: Optional[int] = None):
        if pin:
            self.pin_states.pop(pin, None)
            self.pin_modes.pop(pin, None)
            self.callbacks.pop(pin, None)
            print(f"[MOCK GPIO] Cleaned up pin {pin}")
        else:
            self.pin_states.clear()
            self.pin_modes.clear()
            self.callbacks.clear()
            print("[MOCK GPIO] Cleaned up all pins")
    
    def setmode(self, mode):
        print(f"[MOCK GPIO] Set mode to {mode}")
    
    def simulate_button_press(self, pin: int):
        """Simulate a button press (for testing)."""
        if pin in self.callbacks:
            edge, callback, _ = self.callbacks[pin]
            if edge in (self.FALLING, self.BOTH):
                print(f"[MOCK GPIO] Simulating button press on pin {pin}")
                callback(pin)


def get_gpio(prefer_gpiozero: bool = False) -> GPIOInterface:
    """
    Get appropriate GPIO implementation for the current platform.
    
    Args:
        prefer_gpiozero: If True, prefer gpiozero over RPi.GPIO when both available
    
    Returns:
        GPIOInterface implementation (RPiGPIO, GPIOZero, or MockGPIO)
    """
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            is_pi = 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except Exception:
        is_pi = False
    
    if not is_pi:
        print("[INFO] Not running on Raspberry Pi, using MockGPIO")
        return MockGPIO()
    
    # Try to load GPIO library
    if prefer_gpiozero:
        try:
            return GPIOZero()
        except ImportError:
            pass
        try:
            return RPiGPIO()
        except ImportError:
            pass
    else:
        try:
            return RPiGPIO()
        except ImportError:
            pass
        try:
            return GPIOZero()
        except ImportError:
            pass
    
    # Fallback to mock
    print("[WARNING] GPIO libraries not available, using MockGPIO")
    return MockGPIO()


# For convenience
def is_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except Exception:
        return False
