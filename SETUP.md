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
SETUP.md — GateWise UI

Purpose
-------
This document explains how to set up, install, and run the GateWise UI desktop application from this repository. It covers a Windows PowerShell-focused developer setup, optional hardware (Raspberry Pi / MFRC522) notes, running tests, persistence file locations, a short security note about the hard-coded admin password, and troubleshooting tips.

Prerequisites
-------------
- Supported Python: 3.11 or 3.12 (the repo contains a Python 3.12 virtual environment example). Use the system Python or install from python.org.
- Tools: git, pip
- OS: Windows (primary), Linux / Raspberry Pi supported for hardware usage

Repository layout (important files)
----------------------------------
- `main.py` — application entry point
- `ui/gatewise_ui.py` — primary UI and app logic (contains persistence and admin password.)
- `requirements.txt` — Python dependencies
- `users.json`, `blackout.json` — runtime-persisted data files created in the repository root when the app is first run

1) Clone the repo
-----------------
Open PowerShell and clone the repository (if you haven't already):

```powershell
git clone <repo-url> C:\Personal\gatewise_ui
cd C:\Personal\gatewise_ui
```

2) Create & activate a virtual environment (Windows PowerShell)
-------------------------------------------------------------
From the project root run:

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
Notes:
- If PowerShell blocks execution of scripts you'll see an error about the execution policy. Fix it (for the current user) with an elevated PowerShell prompt:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

- Alternative shells:
  - cmd.exe: `.venv\Scripts\activate.bat`
  - macOS / Linux: `source .venv/bin/activate`

Verify Python and pip are the ones from the venv:

```powershell
python --version
pip --version
```

3) Install Python dependencies
------------------------------
Install the project's Python requirements from the repository root:

```powershell
pip install -r requirements.txt
```

Optional: if you modify dependencies, update `requirements.txt` and commit the change.

4) Optional hardware dependencies — MFRC522 (Raspberry Pi / SPI RFID)
-------------------------------------------------------------------
The application imports `mfrc522` for RFID support. On Linux / Raspberry Pi you'll likely need additional system packages and to enable SPI.

Recommended steps for Raspberry Pi (Debian/Raspbian):

```bash
# enable SPI via raspi-config or use the GUI
sudo raspi-config # -> Interface Options -> SPI -> enable
sudo apt update && sudo apt install -y build-essential python3-dev python3-pip
# install runtime python packages
pip3 install mfrc522 spidev RPi.GPIO
```

Notes:
- Running with hardware usually requires either running the app as root or adding your user to the gpio/spi groups. Consult Raspberry Pi docs for permissions.
- On other Linux systems you may need equivalent packages and to enable or configure SPI.

---

## Raspberry Pi 4 — permanent interface
If your Raspberry Pi 4 will be the permanent interface for the GateWise UI (kiosk or always-on home interface), follow these Pi-specific steps to prepare the OS, enable hardware access, install dependencies into a virtualenv, and auto-launch the UI when the Pi boots into the desktop.

This expanded section assumes a fresh Pi image and includes a reproducible install flow you can run interactively or script for deploying the UI to multiple devices.

Supported OS
- Raspberry Pi OS (Bullseye or later) with Desktop is recommended for a GUI-based permanent interface.

PyQt5 on the Pi — recommended (apt)

On Raspberry Pi OS it's easiest and most reliable to install PyQt5 from the distribution packages instead of building it with pip. This avoids long native builds and missing Qt tools.

Run these commands on the Pi before creating the venv:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebengine
```

Two ways to proceed after installing the OS package:

- Option 1 (recommended): create a venv that can see system site packages so the apt-installed PyQt5 is available inside the venv.

```bash
# create venv that inherits system site-packages
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
# install remaining Python dependencies but skip PyQt5 (see next step)
```

- Option 2: run the app with system Python (no venv). Not recommended for development.

If your `requirements.txt` includes `PyQt5`, avoid pip attempting to install it by creating a Pi-specific requirements file that excludes PyQt5. From the repo root you can run:

```bash
grep -v -i '^PyQt5' requirements.txt > requirements-pi.txt
pip install --no-deps -r requirements-pi.txt
```

Verification (after the venv is active):

```bash
python3 -c "import PyQt5; print(PyQt5.QtCore.QT_VERSION_STR, PyQt5.QtCore.PYQT_VERSION_STR)"
```

If that prints version numbers PyQt5 is available and you can run the UI normally:

```bash
python3 main.py
```

Notes:
- Using apt for PyQt5 simplifies fleet deployment and avoids having to install Qt build tools. If you prefer fully isolated pip installs on each device, see the alternate (build-from-source) approach in the earlier troubleshooting notes (or ask me to add it to SETUP.md).
- Keep a Pi-specific `requirements-pi.txt` in your deployment scripts or provisioning tooling to avoid repeated pip build attempts for PyQt5.

A. Fresh install & recommended directory layout

Recommended locations (pick one and stay consistent for all devices):
- User-installed (default for single-user installs): `/home/pi/gatewise_ui`
- System-wide (shared location for multiple users or locked-down installs): `/opt/gatewise_ui`

We recommend keeping runtime data separate from the application code. Example layout:

- /home/pi/gatewise_ui/           # git repo, code, venv
  - .venv/
  - main.py
  - ui/
  - resources/
  - data/                         # runtime files
    - users.json
    - blackout.json
  - logs/                         # application logs

B. Clone & initial setup (interactive)

Run these commands on the Pi (adjust `GATEWISE_DIR` and `GIT_URL`):

```bash
# variables - adjust as needed
GIT_URL="https://github.com/<your-org-or-user>/gatewise_ui.git"
GATEWISE_DIR="/home/pi/gatewise_ui"

# clone repo and enter directory
git clone "$GIT_URL" "$GATEWISE_DIR"
cd "$GATEWISE_DIR"

# create directories for runtime files and logs
mkdir -p data logs

# create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
# Pi-specific hardware packages
pip install mfrc522 spidev RPi.GPIO gpiozero
```

C. Single-command deploy script (run as pi or via SSH)

Save this example as `deploy_pi.sh`, `chmod +x deploy_pi.sh` and run it on each device (or include in your provisioning tooling). It will clone (or pull), create runtime dirs, create a venv, and install Python deps.

```bash
#!/bin/bash
set -e

GIT_URL="https://github.com/<your-org-or-user>/gatewise_ui.git"
GATEWISE_DIR="/home/pi/gatewise_ui"

# clone or update
if [ -d "$GATEWISE_DIR/.git" ]; then
  echo "Updating existing repo"
  cd "$GATEWISE_DIR" && git pull
else
  git clone "$GIT_URL" "$GATEWISE_DIR"
fi

cd "$GATEWISE_DIR"
mkdir -p data logs

# venv (recreate if missing)
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install mfrc522 spidev RPi.GPIO gpiozero || true

# ensure correct ownership (run as root if needed)
chown -R $USER:$USER "$GATEWISE_DIR"

echo "Deployment complete. You can configure autostart as described in SETUP.md"
```

D. Permissions, groups & reboot

After installing add the user to hardware groups for GPIO/SPI access and reboot:

```bash
sudo usermod -aG gpio,spi,i2c,video,adm $USER
sudo reboot
```

E. Autostart (GUI session) — reproducible method

Create an autostart `.desktop` file for the user that will run the desktop session (adjust paths for `/opt` installs or different usernames):

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/gatewise-ui.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=GateWise UI (Home)
Exec=/home/pi/gatewise_ui/.venv/bin/python /home/pi/gatewise_ui/main.py
WorkingDirectory=/home/pi/gatewise_ui
X-GNOME-Autostart-enabled=true
EOF
```

Notes:
- Replace `/home/pi/gatewise_ui` with your chosen install directory. For `/opt/gatewise_ui` ensure the autostart user has read/execute access to the venv and files.
- For mass deployments, your `deploy_pi.sh` can create this `.desktop` file automatically (ensure correct Exec path).

F. Optional: systemd user service for autostart (alternate)

If you prefer systemd-managed autostart (per-user), create a `~/.config/systemd/user/gatewise-ui.service` file. This approach is useful if you want restart policies but still run within the user's graphical session (enable linger or run as a system user carefully).

Example (user service):

```ini
[Unit]
Description=GateWise UI (per-user)

[Service]
Type=simple
ExecStart=/home/pi/gatewise_ui/.venv/bin/python /home/pi/gatewise_ui/main.py
WorkingDirectory=/home/pi/gatewise_ui
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable and start (run as the user):

```bash
systemctl --user daemon-reload
systemctl --user enable --now gatewise-ui.service
```

G. SSH / remote provisioning notes (deploying to many UIs)

- Enable SSH on the Pi (`sudo raspi-config` -> Interface Options -> SSH) and use `ssh`/`scp` or configuration management (Ansible) to run the `deploy_pi.sh` script remotely.
- Use a host-specific configuration (hostname or /etc/hosts) and set a unique UI name in a config file if you want each device to identify itself to other services.
- Consider using SSH keys for passwordless automated installs.

H. Logs, backups & data persistence

- Application runtime files (`data/users.json`, `data/blackout.json`) should live in the repo `data/` directory so they persist across code updates.
- Rotate or back up `logs/` periodically (logrotate or cron) if you expect long-term operation.

I. Garage door relay and button wiring notes

If you plan to add a garage door relay and physical garage door button to the Pi, follow these safety and implementation notes:

- Use a proper relay module or a solid-state relay rated for the garage door opener's control input. Many garage door openers use a low-voltage momentary switch; you should not switch mains voltage directly with the Pi or a simple relay module without proper isolation.
- Recommended wiring pattern:
  - Relay IN pin -> chosen GPIO (e.g., GPIO17)
  - Relay VCC -> 5V (or 3.3V depending on relay module specs)
  - Relay GND -> GND
  - Button -> GPIO input pin with appropriate pull-up or pull-down (use internal pull-up/pull-down or external resistor). Example button GPIO: GPIO27
- Use a transistor or a commercial relay board with optocoupler and separate power supply if the relay draws more current than the Pi's GPIO can supply.
- Example GPIO pin choices (BCM numbering):
  - RELAY_PIN = 17
  - BUTTON_PIN = 27
- Debounce and safety: debounce the physical button in software and implement timeout logic to avoid accidentally re-triggering the opener.

Example Python sketch (concept only — put this logic into a new module and import it from the UI):

```python
# ...example-only code - adapt and isolate in a new module
from gpiozero import Button, DigitalOutputDevice
from signal import pause

RELAY_PIN = 17
BUTTON_PIN = 27

relay = DigitalOutputDevice(RELAY_PIN, active_high=True, initial_value=False)
button = Button(BUTTON_PIN, pull_up=True)

# momentary relay trigger when button pressed
def trigger_gate():
    relay.on()
    sleep(0.3)
    relay.off()

button.when_pressed = trigger_gate
pause()
```

Warning: Do not connect the Pi directly to mains or to garage motor terminals. If you are unsure, hire an electrician.

8) Persisting the admin password on the Pi

For a permanent Pi install, prefer environment vars or a local untracked config file to keep the admin password out of source control. Example for setting a system-wide environment variable (add to `/etc/profile.d/gatewise.sh`):

```bash
# /etc/profile.d/gatewise.sh (create as root)
export GATEWISE_ADMIN_PASSWORD='your-strong-password-here'
```

Then reboot or re-login so the GUI session inherits the variable.

---

5) Run the application
----------------------
Start the app from the project root (this ensures `users.json` and `blackout.json` are created/used in the expected place):

```powershell
python main.py
```

What to expect:
- On first run the app will create `users.json` and `blackout.json` in the repository root if they don't exist.
- If you need to reset state, stop the app and remove or edit these JSON files.

6) Run tests
------------
This repository includes a small `tests/` folder. Run tests from the project root:

```powershell
pip install pytest  # if not already installed in the venv
pytest -q
```

Run a single test file:

```powershell
pytest tests/test_ui.py -q
```

7) Security note — admin password
---------------------------------
`ui/gatewise_ui.py` currently contains a `request_password()` implementation that uses a hard-coded password (`"admin"`). This is insecure for production. Two simple, safer options:

Option A — Environment variable (recommended for simple setups):
- Set an environment variable on the machine and read it from `gatewise_ui.py`.

PowerShell example (temporary for a session):
```powershell
$env:GATEWISE_ADMIN_PASSWORD = "your-strong-password"
```

In `ui/gatewise_ui.py` replace the hard-coded comparison with something like:

```python
import os
ADMIN_PASSWORD = os.environ.get("GATEWISE_ADMIN_PASSWORD", "admin")  # fallback for dev only
# then compare entered password to ADMIN_PASSWORD
```

Option B — External config (recommended for multi-developer setups):
- Add a `core/config.py` reader that loads secrets from a local, untracked file (e.g., `.env` or `config_local.json`). Ensure secrets are in `.gitignore`.

Important: do not commit secrets to the repository.

8) Persistence file locations and backups
----------------------------------------
- `users.json` and `blackout.json` are in the repository root and are used for runtime state. Keep backups of these files if you need to preserve users or blackout schedules.

9) Troubleshooting & tips
-------------------------
- "Activation failed" in PowerShell: run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force` and re-activate the venv.
- Wrong Python version: ensure `python --version` shows 3.11 or 3.12 from the venv.
- App can't open `users.json` or `blackout.json`: ensure you started the app from the project root and that file permissions allow read/write.
- Hardware (RFID) errors: verify SPI is enabled and the current user has access to SPI/GPIO; test using small hardware sample scripts for `spidev` or `mfrc522`.
- Network sync hook: `push_to_door_modules()` in `ui/gatewise_ui.py` is a placeholder. If your deployment requires syncing with door hardware over the network, implement non-blocking (async) network calls.

10) Quick-start checklist
-------------------------
- [ ] Clone repo and cd to project root
- [ ] Create & activate venv (`python -m venv .venv` + `Activate.ps1`)
- [ ] pip install -r requirements.txt
- [ ] (Optional) Install and configure MFRC522 and SPI on Raspberry Pi
- [ ] Run `python main.py` from project root and verify the UI launches
- [ ] Run `pytest` to validate test suite

11) Contributing notes
----------------------
- Do not commit secrets. Add local config files to `.gitignore`.
- If you add a dependency, update `requirements.txt`.

12) Further help
----------------
If you run into setup issues, open an issue in the repository and include:
- OS and Python version
- Steps you ran and their exact output (or screenshots)
- Any relevant log lines from the application

--
This file gives a compact walkthrough for setting up GateWise UI on Windows (developer) and an optional Raspberry Pi hardware setup. If you'd like, I can also:
- Add a small `scripts/` folder with helper PowerShell scripts to create/activate the venv and run the app.
- Add a sample `core/config.example.py` showing how to load an admin password from a file or env var.
