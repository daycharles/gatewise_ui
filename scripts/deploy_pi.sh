#!/bin/bash
# scripts/deploy_pi.sh
# Deploy GateWise UI to a Raspberry Pi (fresh or update).
# - Installs apt packages (PyQt5, build tools for optional components)
# - Clones or updates the repo
# - Creates data/logs directories
# - Creates a venv that inherits system site-packages (so apt PyQt is usable)
# - Installs Pi-specific pip requirements from requirements-pi.txt
# - Optionally creates an autostart .desktop for the user

set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
  -g GIT_URL        Git repo URL (default: https://github.com/daycharles/gatewise_ui)
  -g GIT_URL        Git repo URL (default: https://github.com/<your-org-or-user>/gatewise_ui.git)
  -d DIR            Install directory (default: /home/pi/gatewise_ui)
  -u USER           System user to own files and create autostart for (default: current user)
  -n                Do not create autostart .desktop (disable)
  -h                Show this help

Example:
  ./deploy_pi.sh -g https://github.com/daycharles/gatewise_ui -d /opt/gatewise_ui -u pi
  ./deploy_pi.sh -g https://github.com/you/gatewise_ui.git -d /opt/gatewise_ui -u pi
EOF
}

# Defaults - override with flags
GIT_URL="https://github.com/daycharles/gatewise_ui"
GIT_URL="https://github.com/<your-org-or-user>/gatewise_ui.git"
GATEWISE_DIR="/home/pi/gatewise_ui"
CREATE_AUTOSTART=true
AUTOSTART_USER="${SUDO_USER:-${USER:-pi}}"

while getopts ":g:d:u:nh" opt; do
  case ${opt} in
    g ) GIT_URL="$OPTARG" ;;
    d ) GATEWISE_DIR="$OPTARG" ;;
    u ) AUTOSTART_USER="$OPTARG" ;;
    n ) CREATE_AUTOSTART=false ;;
    h ) usage; exit 0 ;;
    \? ) echo "Invalid option: -$OPTARG" 1>&2; usage; exit 1 ;;
    : ) echo "Invalid option: -$OPTARG requires an argument" 1>&2; usage; exit 1 ;;
  esac
done

echo "Deploying GateWise UI"
echo "  Repo: $GIT_URL"
echo "  Install dir: $GATEWISE_DIR"
echo "  Autostart for user: $AUTOSTART_USER (create: $CREATE_AUTOSTART)"

# Apt packages needed for a GUI + PyQt via apt, plus common build/runtime tools
# Apt packages needed for a GUI + PyQt via apt, plus common build tools
APT_PACKAGES=(
  python3-pyqt5
  python3-pyqt5.qtwebengine
  build-essential
  python3-dev
  python3-venv
  python3-pip
  python3-rpi.gpio
  python3-spidev
  python3-venv
  python3-pip
  git
)

echo "Installing apt packages (may prompt for sudo)..."
sudo apt update && sudo apt install -y "${APT_PACKAGES[@]}"

# Clone or update repository
if [ -d "$GATEWISE_DIR/.git" ]; then
  echo "Updating existing repo at $GATEWISE_DIR"
  cd "$GATEWISE_DIR"
  git fetch --all --prune
  git reset --hard origin/HEAD || git pull --rebase || true
else
  echo "Cloning repo to $GATEWISE_DIR"
  sudo mkdir -p "$GATEWISE_DIR"
  sudo chown "$AUTOSTART_USER":"$AUTOSTART_USER" "$GATEWISE_DIR"
  git clone "$GIT_URL" "$GATEWISE_DIR"
fi

cd "$GATEWISE_DIR"

# Create runtime directories
mkdir -p data logs

# Create venv that can see system site packages (so apt-installed PyQt is available)
if [ ! -d .venv ]; then
  echo "Creating virtualenv (.venv) with system-site-packages"
  python3 -m venv .venv --system-site-packages
fi

# Activate venv
# shellcheck source=/dev/null
source .venv/bin/activate

pip install --upgrade pip setuptools wheel || true

# Install Pi-specific pip requirements file if present, otherwise fallback
if [ -f requirements-pi.txt ]; then
  echo "Installing Python packages from requirements-pi.txt"
  pip install --no-deps -r requirements-pi.txt || true
else
  echo "requirements-pi.txt not found. Installing common Pi packages via pip"
  pip install mfrc522 spidev RPi.GPIO gpiozero || true
fi

# Ensure correct ownership for the install directory
sudo chown -R "$AUTOSTART_USER":"$AUTOSTART_USER" "$GATEWISE_DIR" || true

# Add user to hardware groups if available
echo "Adding $AUTOSTART_USER to gpio/spi/i2c groups (if they exist)"
for g in gpio spi i2c; do
  if getent group "$g" >/dev/null 2>&1; then
    echo " - adding to group $g"
    sudo usermod -aG "$g" "$AUTOSTART_USER" || true
  fi
done

# Create autostart .desktop for GUI session if requested
if [ "$CREATE_AUTOSTART" = true ]; then
  AUTOSTART_DIR="/home/$AUTOSTART_USER/.config/autostart"
  sudo -u "$AUTOSTART_USER" mkdir -p "$AUTOSTART_DIR"
  AUTOSTART_FILE="$AUTOSTART_DIR/gatewise-ui.desktop"
  echo "Creating autostart desktop entry at $AUTOSTART_FILE"
  cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=GateWise UI (Home)
Exec=$GATEWISE_DIR/.venv/bin/python $GATEWISE_DIR/main.py
WorkingDirectory=$GATEWISE_DIR
X-GNOME-Autostart-enabled=true
EOF
  sudo chown "$AUTOSTART_USER":"$AUTOSTART_USER" "$AUTOSTART_FILE" || true
  sudo chmod 644 "$AUTOSTART_FILE" || true
fi

echo "Deployment complete. You may need to reboot for group changes to take effect."

echo "To run now: sudo -u $AUTOSTART_USER bash -c 'source $GATEWISE_DIR/.venv/bin/activate && python3 $GATEWISE_DIR/main.py'"
