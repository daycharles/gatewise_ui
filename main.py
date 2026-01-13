import os
import sys
from ui.gatewise_ui import launch_ui
from core.rfid_server import start_rfid_server

if __name__ == "__main__":
    # Start RFID authorization server for ESP32 communication
    # Port 80 requires root/admin on Linux; use 8080 for dev or run with sudo
    rfid_port = int(os.environ.get('RFID_SERVER_PORT', '8080'))
    
    try:
        print(f"[MAIN] Starting RFID authorization server on port {rfid_port}")
        rfid_server = start_rfid_server(
            host='0.0.0.0',
            port=rfid_port,
            users_file='users.json',
            blackout_file='blackout.json',
            default_unlock_ms=3000  # 3 seconds default unlock time
        )
        print(f"[MAIN] RFID server running - ESP32 should connect to http://<this_pi_ip>:{rfid_port}/rfid")
    except Exception as e:
        print(f"[MAIN ERROR] Failed to start RFID server: {e}")
        print("[MAIN] Continuing without RFID server...")
    
    # Launch the UI
    launch_ui()
