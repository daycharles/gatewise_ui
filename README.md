# GateWise UI

Modern PyQt5 touchscreen interface for secure home access control with garage door integration.

## Features

- **RFID Access Control**: Manage authorized users with MFRC522 RFID reader
- **Garage Door Control**: Relay-based garage door opener with manual button support
- **User Management**: Add, edit, and remove authorized users with admin privileges
- **Access Schedules**: Configure blackout periods and timed access windows
- **Event Logging**: Track all access attempts and garage door operations
- **Touch-Friendly UI**: Designed for touchscreen displays (800x480 default)
- **Network Sync**: Push user data to remote door control modules
- **Secure Configuration**: Environment-based configuration with no hardcoded passwords

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

### Basic Installation

```bash
# Clone repository
git clone https://github.com/yourusername/gatewise_ui.git
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

### Minimum (RFID only)
- Raspberry Pi 3B+ or newer (or any PC for development)
- MFRC522 RFID reader module
- Touchscreen display (optional, can use desktop monitor)

### Full Setup (with Garage Control)
- Raspberry Pi 3B+ or newer
- MFRC522 RFID reader module
- Relay module (1-channel, opto-isolated recommended)
- Push button (momentary, normally-open)
- Optional: magnetic reed switch for door position sensing
- Touchscreen display or HDMI monitor

## Configuration

All configuration is done via environment variables or a `.env` file. Copy `config.example` to `.env` and customize:

```bash
cp config.example .env
nano .env
```

Key settings:
- `GATEWISE_ADMIN_PASSWORD`: Admin password (REQUIRED)
- `GARAGE_ENABLED`: Enable garage door features (true/false)
- `GARAGE_RELAY_PIN`: GPIO pin for relay control (BCM numbering)
- `GARAGE_BUTTON_PIN`: GPIO pin for manual button input

See [SETUP.md](SETUP.md) for complete configuration options.

## Project Structure

```
gatewise_ui/
├── main.py                 # Application entry point
├── ui/
│   └── gatewise_ui.py     # Main UI implementation
├── core/
│   ├── config.py          # Configuration management
│   ├── garage.py          # Garage door controller
│   ├── gpio_abstraction.py  # GPIO platform abstraction
│   ├── logger.py          # Event logging
│   ├── network_listener.py   # Network communication
│   └── override_controls.py  # Access override logic
├── resources/
│   └── icons/             # UI icons and images
├── SETUP.md               # Detailed setup guide
├── IMPLEMENTATION_PLAN.md # Development roadmap
└── config.example         # Configuration template
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never use the default admin password** - Set `GATEWISE_ADMIN_PASSWORD` immediately
2. **Protect configuration files** - Ensure `.env` and data files have restricted permissions (chmod 600)
3. **Secure remote access** - Use VPN instead of port forwarding; enable TLS if exposing to internet
4. **Regular backups** - Backup `users.json`, `blackout.json`, and `.env` regularly
5. **Physical security** - Protect the Raspberry Pi from unauthorized physical access

## Development

### Mock GPIO for Desktop Development

The application automatically uses mock GPIO when not running on a Raspberry Pi, allowing development and testing on any platform.

### Contributing

Contributions welcome! Please see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for planned features and improvements.

## License

[Add your license here]

## Support

For issues, questions, or feature requests, please:
1. Check [SETUP.md](SETUP.md) for troubleshooting
2. Review [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for planned features
3. Open an issue on GitHub with details

## Acknowledgments

- Built with PyQt5
- RFID support via [MFRC522-python](https://github.com/pimylifeup/MFRC522-python)
- GPIO support via RPi.GPIO / gpiozero
