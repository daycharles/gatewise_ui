# SETUP.md — GateWise UI

## Purpose
This document explains how to set up, install, and run the GateWise UI application for gym access control.

## Prerequisites
- Supported Python: 3.11 or 3.12
- Tools: git, pip
- OS: Windows (development), Linux/Raspberry Pi (production deployment)

## Repository Layout
- `main.py` — application entry point
- `ui/gatewise_ui.py` — primary UI and app logic
- `core/config.py` — configuration management
- `requirements.txt` — Python dependencies
- `users.json`, `blackout.json` — runtime-persisted data files (created on first run)

## 1) Clone the Repository
```bash
git clone https://github.com/daycharles/gatewise_ui.git
cd gatewise_ui
```

## 2) Create & Activate Virtual Environment

### Windows PowerShell
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

If PowerShell blocks execution:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Verify:
```bash
python --version
pip --version
```

## 3) Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 4) Optional Hardware Dependencies — MFRC522 (Raspberry Pi)

For Raspberry Pi with RFID reader:

```bash
# Enable SPI via raspi-config
sudo raspi-config  # -> Interface Options -> SPI -> enable

# Install system packages
sudo apt update && sudo apt install -y build-essential python3-dev python3-pip

# Install RFID library
pip3 install mfrc522 spidev RPi.GPIO
```

**Note**: RFID hardware requires proper permissions. Add user to gpio/spi groups:
```bash
sudo usermod -aG gpio,spi $USER
sudo reboot
```

## 5) Configuration

### Admin Password (REQUIRED)

**Option A: Environment Variable (Recommended)**

Windows PowerShell:
```powershell
$env:GATEWISE_ADMIN_PASSWORD = "your-strong-password"
```

Linux/macOS:
```bash
export GATEWISE_ADMIN_PASSWORD="your-strong-password"
```

**Option B: .env File**

Copy `config.example` to `.env`:
```bash
cp config.example .env
nano .env
```

Set your password in `.env`:
```
GATEWISE_ADMIN_PASSWORD=your-strong-password
```

### Additional Configuration Options

Edit `.env` file to customize:
- `APP_TITLE`: Application window title
- `PRIMARY_COLOR`: UI color scheme (hex format)
- `RFID_ENABLED`: Enable/disable RFID reader
- `DOOR_MODULE_IPS`: Comma-separated door controller IPs
- `WINDOW_SIZE`: Display resolution (e.g., 800x480)

See `config.example` for full list of options.

## 6) Run the Application

From project root:
```bash
python main.py
```

First run creates `users.json` and `blackout.json` in the repository root.

## 7) Run Tests

```bash
pip install pytest  # if not already installed
pytest -q
```

Run specific test file:
```bash
pytest tests/test_ui.py -q
```

## Raspberry Pi Deployment

### PyQt5 Installation on Pi

Install PyQt5 from system packages (recommended):
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebengine
```

Create venv with system site packages:
```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
```

Install remaining dependencies (excluding PyQt5):
```bash
grep -v -i '^PyQt5' requirements.txt > requirements-pi.txt
pip install -r requirements-pi.txt
```

### Autostart on Pi

Create autostart entry:
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/gatewise-ui.desktop <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=GateWise Access Control
Exec=/home/pi/gatewise_ui/.venv/bin/python /home/pi/gatewise_ui/main.py
WorkingDirectory=/home/pi/gatewise_ui
X-GNOME-Autostart-enabled=true
DESKTOP
```

Set environment variables for GUI session:
```bash
# Add to /etc/profile.d/gatewise.sh (as root)
export GATEWISE_ADMIN_PASSWORD='your-password'
```

Reboot for changes to take effect.

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
Stores blackout schedule:
```json
{
  "Monday": [
    {"start": "04:00", "end": "10:00"}
  ]
}
```

**Important**: Keep regular backups of these files!

## Troubleshooting

### Application won't start
- Ensure virtual environment is activated
- Verify dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11 or 3.12)

### RFID reader not working
- Verify SPI is enabled on Raspberry Pi
- Check wiring connections
- Test with: `sudo python -c "from mfrc522 import SimpleMFRC522; r = SimpleMFRC522(); print(r.read())"`

### Permission errors on Raspberry Pi
- Add user to required groups: `sudo usermod -aG gpio,spi $USER`
- Log out and log back in

### Admin password not working
- Verify environment variable: `echo $GATEWISE_ADMIN_PASSWORD`
- Restart application after setting the variable
- Check `.env` file for typos

## Security Best Practices

- **Never commit secrets** to version control
- Use strong, unique passwords for admin access
- Keep `users.json` and `blackout.json` backed up securely
- Limit network access to the application
- Use HTTPS/VPN if exposing remotely
- Regularly update dependencies for security patches

## Support

For issues or questions:
1. Check troubleshooting section above
2. Open an issue on GitHub with details (OS, Python version, error messages)
