# Home Access Control System

Modern PyQt5 touchscreen interface for secure home access control, including door access management and garage door control.

## Features

- RFID-based access control
- User management with admin privileges
- Blackout schedule configuration
- Garage door control via GPIO relay
- Physical garage button monitoring
- Access logs and history
- Touchscreen-friendly interface

## Documentation

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

## Quick Start

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment:
   - Windows: `. .\.venv\Scripts\Activate.ps1`
   - Linux/macOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set admin password: `export GATEWISE_ADMIN_PASSWORD="your-password"`
6. Run application: `python main.py`

## Requirements

- Python 3.11 or 3.12
- PyQt5
- Optional: Raspberry Pi with MFRC522 RFID reader
- Optional: GPIO relay module for garage control

## Security

- Admin password is configured via environment variable `GATEWISE_ADMIN_PASSWORD`
- Never commit passwords or secrets to version control
- Keep backup copies of `users.json` and `blackout.json`

## License

See repository for license information.

