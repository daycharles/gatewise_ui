# GateWise UI Setup Guide

This guide covers installation, configuration, and hardware setup for repurposing GateWise UI for home use with garage door control.

## Table of Contents

1. [Software Installation](#software-installation)
2. [Configuration](#configuration)
3. [Hardware Setup (Raspberry Pi)](#hardware-setup-raspberry-pi)
4. [Garage Door Integration](#garage-door-integration)
5. [Running the Application](#running-the-application)
6. [Security Considerations](#security-considerations)

## Software Installation

### Prerequisites

- Python 3.8 or higher
- For Raspberry Pi: Raspbian/Raspberry Pi OS with GPIO support

### Windows Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/yourusername/gatewise_ui.git
   cd gatewise_ui
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   If you encounter execution policy errors, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Linux/Raspberry Pi Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gatewise_ui.git
   cd gatewise_ui
   ```

2. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-dev python3-pip python3-venv build-essential
   ```

3. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

4. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **For Raspberry Pi with GPIO support:**
   ```bash
   pip install RPi.GPIO gpiozero
   ```

## Configuration

### Admin Password

**IMPORTANT:** The application uses a hardcoded admin password by default ("admin"). You must change this for security.

#### Option A: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:GATEWISE_ADMIN_PASSWORD = "your-strong-password"
```

To make it permanent, add to your PowerShell profile or set as a system environment variable.

**Linux/Raspberry Pi (Bash):**
```bash
export GATEWISE_ADMIN_PASSWORD="your-strong-password"
```

Add this line to `~/.bashrc` or `~/.profile` to make it permanent.

#### Option B: Create a `.env` file (Alternative)

Create a `.env` file in the project root (this file is gitignored):

```bash
GATEWISE_ADMIN_PASSWORD=your-strong-password
```

### Garage Door Configuration

If using garage door control features, configure GPIO pins via environment variables:

```bash
# Relay pin (BCM numbering)
GARAGE_RELAY_PIN=17

# Button input pin (BCM numbering)
GARAGE_BUTTON_PIN=27

# Relay logic (true for active-low relays, false for active-high)
GARAGE_RELAY_ACTIVE_LOW=true

# Door sensor pin (optional, for detecting door state)
GARAGE_SENSOR_PIN=22
```

## Hardware Setup (Raspberry Pi)

### Enable SPI for RFID Reader

The application uses an MFRC522 RFID reader that requires SPI:

1. Run the configuration tool:
   ```bash
   sudo raspi-config
   ```

2. Navigate to: **Interface Options → SPI → Enable**

3. Reboot:
   ```bash
   sudo reboot
   ```

### GPIO Permissions

Add your user to the GPIO group to access GPIO pins without sudo:

```bash
sudo usermod -a -G gpio $USER
sudo usermod -a -G spi $USER
```

Log out and back in for changes to take effect.

## Garage Door Integration

### Hardware Requirements

- **Relay Module:** Opto-isolated relay module rated for 5V/3.3V control signal
  - Recommended: 1-channel relay module with optocoupler
  - Must handle the garage opener's input voltage (typically 12-24V DC or dry contact)
- **Push Button:** Momentary push button (normally open) for manual control
- **Optional:** Magnetic reed switch or contact sensor for door position detection
- **Connecting Wires:** Jumper wires for GPIO connections

### Wiring Diagram

#### Relay Connection (GPIO → Garage Opener)

```
Raspberry Pi GPIO    →    Relay Module    →    Garage Opener
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO 17 (BCM)       →    IN/Signal       
3.3V or 5V          →    VCC             
GND                 →    GND             
                         COM (Common)    →    Opener Terminal 1
                         NO (Norm. Open) →    Opener Terminal 2
```

**Notes:**
- The relay simulates a button press by closing the circuit momentarily
- Most garage openers use dry contact (no voltage) input
- Verify your opener's specifications before connecting
- Use an opto-isolated relay to protect the Pi from electrical noise

#### Button Connection (Manual Control)

```
Raspberry Pi GPIO    →    Push Button
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO 27 (BCM)       →    Button Terminal 1
GND                 →    Button Terminal 2
```

**Notes:**
- Configure GPIO 27 as INPUT with internal pull-up resistor
- Button connects GPIO to GND when pressed (active-low)
- Software debouncing is implemented in the code

#### Optional Door Sensor

```
Raspberry Pi GPIO    →    Reed Switch/Contact Sensor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO 22 (BCM)       →    Sensor Terminal 1
GND                 →    Sensor Terminal 2
```

### Safety Warnings

⚠️ **CRITICAL SAFETY INFORMATION:**

1. **Never work with mains voltage (120V/240V AC)** unless you are qualified and certified
2. **Use isolated relays** to prevent electrical feedback to the Raspberry Pi
3. **Test the garage door sensor** to prevent closing on people or vehicles
4. **Maintain manual override** - ensure physical buttons still work
5. **Add visual/audio warnings** before automatic door operation
6. **Keep clear zones** marked around the garage door
7. **Regular testing** - verify safety sensors and auto-reverse features monthly
8. **Consider fail-safe defaults** - door should remain closed or stop if power is lost

### Relay Pulse Duration

The default relay pulse duration is **500ms** (half a second), which simulates a momentary button press. Most garage door openers require a pulse between 100-1000ms. Adjust in the configuration if needed:

```python
GARAGE_RELAY_PULSE_MS=500
```

## Running the Application

### Development Mode (Desktop)

From the project root directory:

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Run the application
python main.py
```

### Production Mode (Raspberry Pi)

For headless operation, create a systemd service:

1. **Create service file:**
   ```bash
   sudo nano /etc/systemd/system/gatewise.service
   ```

2. **Add configuration:**
   ```ini
   [Unit]
   Description=GateWise Home Access Control
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/gatewise_ui
   Environment="GATEWISE_ADMIN_PASSWORD=your-strong-password"
   Environment="GARAGE_RELAY_PIN=17"
   Environment="GARAGE_BUTTON_PIN=27"
   Environment="GARAGE_RELAY_ACTIVE_LOW=true"
   ExecStart=/home/pi/gatewise_ui/.venv/bin/python /home/pi/gatewise_ui/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gatewise.service
   sudo systemctl start gatewise.service
   ```

4. **Check status:**
   ```bash
   sudo systemctl status gatewise.service
   ```

5. **View logs:**
   ```bash
   sudo journalctl -u gatewise.service -f
   ```

## Security Considerations

### Authentication

- **Replace default password immediately** - use a strong, unique password
- **Limit network access** - bind to localhost only if not accessing remotely
- **Use strong passwords** - minimum 12 characters with mixed case, numbers, symbols

### Network Security

If enabling remote access:

1. **Use VPN** instead of port forwarding when possible
2. **Enable HTTPS/TLS** for encrypted communication
3. **Implement rate limiting** to prevent brute-force attacks
4. **Use fail2ban** or similar tools to block repeated failed attempts
5. **Keep software updated** - regularly update dependencies

### File Permissions

Restrict access to sensitive files:

```bash
chmod 600 .env
chmod 600 users.json
chmod 600 blackout.json
```

### Backup

Regularly backup your configuration and user data:

```bash
# Create backup
tar -czf gatewise_backup_$(date +%Y%m%d).tar.gz users.json blackout.json .env

# Restore backup
tar -xzf gatewise_backup_YYYYMMDD.tar.gz
```

## Troubleshooting

### RFID Reader Not Working

- Verify SPI is enabled: `lsmod | grep spi`
- Check wiring connections
- Test with: `sudo python -c "from mfrc522 import SimpleMFRC522; reader = SimpleMFRC522(); print(reader.read())"`

### GPIO Permission Denied

- Add user to gpio group: `sudo usermod -a -G gpio $USER`
- Log out and back in
- Check group membership: `groups`

### Display Issues

- Ensure DISPLAY environment variable is set
- For SSH sessions with X11 forwarding: `ssh -X user@hostname`
- For touchscreen: configure Qt to use the correct display

### Application Won't Start

- Check Python version: `python --version` (must be 3.8+)
- Verify all dependencies: `pip list`
- Check for error messages: `python main.py`
- Ensure you're in the project root directory
- Verify virtual environment is activated

## Additional Resources

- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/computers/gpio.html)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [MFRC522 Python Library](https://github.com/pimylifeup/MFRC522-python)
- [gpiozero Documentation](https://gpiozero.readthedocs.io/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Open an issue on GitHub with detailed error messages
