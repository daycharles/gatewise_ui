# GateWise UI Setup Guide

## Purpose
This guide helps you set up and run the GateWise UI application for home access control, including garage door management.

## Prerequisites
- **Python**: Version 3.11 or 3.12 recommended
- **Operating System**: Windows, Linux, or macOS
- **Optional Hardware**: Raspberry Pi with MFRC522 RFID reader for physical card scanning

## Repository Layout
- `main.py` - Application entry point
- `ui/gatewise_ui.py` - Main UI logic and screens
- `core/` - Core modules (config, logger, network listener, override controls)
- `requirements.txt` - Python dependencies
- `resources/icons/` - UI icons and images
- `users.json` - User database (created at first run)
- `blackout.json` - Blackout schedule configuration (created at first run)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/daycharles/gatewise_ui.git
cd gatewise_ui
```

### 2. Create Virtual Environment

#### Windows PowerShell
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

**Note**: If you get an error about execution policies, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Optional: Hardware Setup (Raspberry Pi + MFRC522)

If using a Raspberry Pi with MFRC522 RFID reader:

1. Enable SPI interface:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > SPI > Enable
   ```

2. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install build-essential python3-dev
   ```

3. Install RFID libraries:
   ```bash
   pip3 install mfrc522 spidev RPi.GPIO
   ```

4. Wire the MFRC522 to your Raspberry Pi:
   - SDA → Pin 24 (GPIO 8)
   - SCK → Pin 23 (GPIO 11)
   - MOSI → Pin 19 (GPIO 10)
   - MISO → Pin 21 (GPIO 9)
   - GND → Ground
   - RST → Pin 22 (GPIO 25)
   - 3.3V → 3.3V

### 5. Configure Admin Password (Security)

**IMPORTANT**: The application uses an admin password to access settings. By default, it reads from an environment variable.

#### Set Admin Password

**Windows PowerShell (session only)**:
```powershell
$env:GATEWISE_ADMIN_PASSWORD = "your-strong-password"
```

**Linux/macOS (session only)**:
```bash
export GATEWISE_ADMIN_PASSWORD="your-strong-password"
```

**Permanent Configuration (Recommended)**:
Create a `.env` file in the project root (add to .gitignore):
```bash
GATEWISE_ADMIN_PASSWORD=your-strong-password
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

### 6. Garage Door Configuration (Optional)

If using GPIO for garage door control:

1. Connect relay module to GPIO pins (recommended: GPIO 17 for relay)
2. Connect physical garage button to GPIO input (recommended: GPIO 27)
3. Update configuration in code or config file with your GPIO pin numbers

**Safety Note**: Always test garage door control in a safe manner. Ensure proper electrical isolation and fail-safes.

## Running the Application

### Start the Application
From the project root directory:
```bash
python main.py
```

The application will:
- Create `users.json` and `blackout.json` in the project root if they don't exist
- Launch the PyQt5 GUI interface
- Listen for RFID card scans (if hardware is connected)

### First Launch
1. Click the settings icon (gear) on the main screen
2. Enter the admin password (from `GATEWISE_ADMIN_PASSWORD` environment variable)
3. Add users via "User Maintenance"
4. Configure blackout schedules if needed
5. Set up garage control (if applicable)

## Running Tests

### Install pytest (if not already installed)
```bash
pip install pytest
```

### Run all tests
```bash
pytest -q
```

### Run specific test file
```bash
pytest tests/test_ui.py -q
```

## Configuration Files

### users.json
Stores user database:
```json
[
  {
    "uid": "123456789",
    "name": "John Doe",
    "isAdmin": true
  }
]
```

### blackout.json
Stores blackout schedule (times when access is restricted):
```json
{
  "Monday": [
    {"start": "04:00", "end": "10:00"}
  ]
}
```

**Backup Recommendation**: Keep regular backups of `users.json` and `blackout.json`.

## Troubleshooting

### Application won't start
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11 or 3.12)

### RFID reader not working
- Verify SPI is enabled on Raspberry Pi
- Check wiring connections
- Test with: `sudo python -c "from mfrc522 import SimpleMFRC522; r = SimpleMFRC522(); print(r.read())"`

### Permission errors on Raspberry Pi
- Add user to required groups:
  ```bash
  sudo usermod -a -G gpio,spi $USER
  ```
- Log out and log back in for changes to take effect

### Admin password not working
- Verify environment variable is set: `echo $GATEWISE_ADMIN_PASSWORD` (Linux/macOS) or `$env:GATEWISE_ADMIN_PASSWORD` (PowerShell)
- Check for typos in the password
- Restart the application after setting the environment variable

### Garage door not responding
- Verify GPIO permissions
- Check relay wiring and power supply
- Test relay independently before integration
- Check for proper electrical isolation

## Quick Start Checklist
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Set admin password environment variable
- [ ] Run application
- [ ] Access settings and add users
- [ ] Test RFID scanning (if hardware connected)
- [ ] Configure garage control (if applicable)

## Contributing
- Do not commit secrets or passwords to the repository
- Update `requirements.txt` when adding new dependencies
- Test changes before submitting pull requests
- Follow existing code style and conventions

## Security Best Practices
- Never commit passwords or secrets to version control
- Use strong, unique passwords for admin access
- Keep `users.json` and `blackout.json` backed up securely
- Limit network access to the application
- Use HTTPS/VPN if exposing remotely
- Regularly update dependencies for security patches

## Support
For issues or questions, please open an issue on the GitHub repository.
