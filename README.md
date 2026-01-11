# GateWise Access Control System

Modern PyQt5 touchscreen interface for secure gym access control with RFID-based member verification.

## Features

- **RFID Access Control**: Manage authorized gym members with MFRC522 RFID reader
- **User Management**: Add, edit, and remove authorized users with admin privileges
- **Class Access**: "Unlock for Class" functionality with configurable duration
- **Blackout Schedules**: Configure time periods when access is restricted
- **Access Logs**: Track all entry attempts and member activity
- **Touch-Friendly UI**: Designed for touchscreen displays (800x480 default)
- **Network Sync**: Push user data to remote door control modules
- **Secure Configuration**: Environment-based configuration with no hardcoded passwords

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

### Basic Installation

```bash
# Clone repository
git clone https://github.com/daycharles/gatewise_ui.git
cd gatewise_ui

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Set admin password (IMPORTANT!)
export GATEWISE_ADMIN_PASSWORD="your-strong-password"

# Run application
python main.py
```

## Hardware Requirements

### Minimum Setup
- Raspberry Pi 3B+ or newer (or any PC for development)
- MFRC522 RFID reader module
- Touchscreen display (optional, can use desktop monitor)

### Recommended for Gym Deployment
- Raspberry Pi 4
- MFRC522 RFID reader with RFID cards/fobs for members
- 7" or 10" touchscreen display
- Weatherproof enclosure (for outdoor installations)
- Door strike or magnetic lock (controlled by network module)

## Configuration

All configuration is done via environment variables or a `.env` file. Copy `config.example` to `.env` and customize:

```bash
cp config.example .env
nano .env
```

Key settings:
- `GATEWISE_ADMIN_PASSWORD`: Admin password (REQUIRED)
- `RFID_ENABLED`: Enable RFID reader (true/false)
- `DOOR_MODULE_IPS`: Comma-separated list of door controller IPs
- `APP_TITLE`: Application title
- `PRIMARY_COLOR`: Primary UI color (hex format)

See [SETUP.md](SETUP.md) for complete configuration options.

## Project Structure

```
gatewise_ui/
├── main.py                 # Application entry point
├── ui/
│   └── gatewise_ui.py     # Main UI implementation
├── core/
│   ├── config.py          # Configuration management
│   ├── logger.py          # Event logging
│   ├── network_listener.py   # Network communication
│   └── override_controls.py  # Access override logic
├── resources/
│   └── icons/             # UI icons and images
├── SETUP.md               # Detailed setup guide
└── config.example         # Configuration template
```

## Usage

### For Gym Members
1. Present RFID card/fob to reader
2. System verifies membership and access permissions
3. Door unlocks if authorized

### For Gym Staff
- **Access Logs**: View member entry history
- **Settings**: Configure blackout schedules and class access duration
- **User Management**: Add/remove members, manage admin privileges
- **Class Mode**: Use "Unlock for Class" button to temporarily unlock door for scheduled classes

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never use the default admin password** - Set `GATEWISE_ADMIN_PASSWORD` immediately
2. **Protect configuration files** - Ensure `.env` and data files have restricted permissions (chmod 600)
3. **Secure remote access** - Use VPN instead of port forwarding
4. **Regular backups** - Backup `users.json` and `blackout.json` regularly
5. **Physical security** - Protect the Raspberry Pi from unauthorized physical access

## Development

### Mock Hardware for Desktop Development

The application automatically uses mock hardware when not running on a Raspberry Pi, allowing development and testing on any platform.

### Contributing

Contributions welcome! Please:
- Test changes before submitting pull requests
- Follow existing code style and conventions
- Update documentation for new features

## License

[Add your license here]

## Support

For issues, questions, or feature requests:
1. Check [SETUP.md](SETUP.md) for troubleshooting
2. Open an issue on GitHub with details

## Acknowledgments

- Built with PyQt5
- RFID support via [MFRC522-python](https://github.com/pimylifeup/MFRC522-python)
- GPIO support via RPi.GPIO
