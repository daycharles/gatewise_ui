"""
RFID Authorization HTTP Server

Provides HTTP endpoint for ESP32 RFID readers to query authorization status.
ESP32 POSTs {"uid": "<hex_uid>"} and receives {"authorized": true/false, "duration": <ms>}
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path


class RFIDAuthorizationHandler(BaseHTTPRequestHandler):
    """HTTP request handler for RFID authorization queries."""
    
    # Class variables to be set before server starts
    users_file = "users.json"
    blackout_file = "blackout.json"
    default_unlock_duration_ms = 3000  # 3 seconds default
    
    def _set_response(self, status_code=200, content_type="application/json"):
        """Set HTTP response headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _load_users(self):
        """Load users from JSON file."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[RFID SERVER ERROR] Failed to load users: {e}")
        return []
    
    def _load_blackout_schedule(self):
        """Load blackout schedule from JSON file."""
        try:
            if os.path.exists(self.blackout_file):
                with open(self.blackout_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[RFID SERVER ERROR] Failed to load blackout schedule: {e}")
        return {}
    
    def _is_in_blackout(self):
        """Check if current time is within a blackout period."""
        schedule = self._load_blackout_schedule()
        now = datetime.now()
        day_name = now.strftime("%A")  # Monday, Tuesday, etc.
        current_time = now.time()
        
        if day_name in schedule:
            for block in schedule[day_name]:
                try:
                    start_str = block.get("start", "00:00")
                    end_str = block.get("end", "23:59")
                    
                    # Parse time strings (HH:MM format)
                    start_parts = start_str.split(":")
                    end_parts = end_str.split(":")
                    
                    start_time = datetime.strptime(start_str, "%H:%M").time()
                    end_time = datetime.strptime(end_str, "%H:%M").time()
                    
                    # Check if current time falls within this block
                    if start_time <= current_time <= end_time:
                        return True
                except Exception as e:
                    print(f"[RFID SERVER ERROR] Failed to parse time block: {e}")
                    continue
        
        return False
    
    def _check_authorization(self, uid):
        """
        Check if a UID is authorized to unlock the door.
        
        Args:
            uid: The RFID UID string
            
        Returns:
            tuple: (authorized: bool, duration_ms: int)
        """
        # Load users
        users = self._load_users()
        
        # Check if UID exists in users list
        user = None
        for u in users:
            if u.get('uid', '').upper() == uid.upper():
                user = u
                break
        
        if not user:
            print(f"[RFID SERVER] UID {uid} not found in users database")
            return False, 0
        
        # Check blackout schedule
        if self._is_in_blackout():
            print(f"[RFID SERVER] Access denied for {user.get('name', 'Unknown')} - in blackout period")
            return False, 0
        
        # Authorized!
        print(f"[RFID SERVER] Access granted for {user.get('name', 'Unknown')} (UID: {uid})")
        return True, self.default_unlock_duration_ms
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self._set_response(200)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health' or self.path == '/':
            self._set_response(200)
            response = {
                "status": "ok",
                "service": "RFID Authorization Server",
                "endpoint": "/rfid"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests from ESP32."""
        if self.path != '/rfid':
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            uid = data.get('uid', '').strip()
            
            if not uid:
                self._set_response(400)
                response = {"error": "Missing UID", "authorized": False}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            print(f"[RFID SERVER] Received authorization request for UID: {uid}")
            
            # Check authorization
            authorized, duration = self._check_authorization(uid)
            
            # Build response
            response = {
                "authorized": authorized,
                "duration": duration
            }
            
            self._set_response(200)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            self._set_response(400)
            response = {"error": "Invalid JSON", "authorized": False}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[RFID SERVER ERROR] {e}")
            self._set_response(500)
            response = {"error": "Internal server error", "authorized": False}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[RFID SERVER] {self.address_string()} - {format % args}")


class RFIDAuthServer:
    """RFID Authorization HTTP Server"""
    
    def __init__(self, host='0.0.0.0', port=80, users_file='users.json', 
                 blackout_file='blackout.json', default_unlock_ms=3000):
        """
        Initialize RFID authorization server.
        
        Args:
            host: Host to bind to (default: 0.0.0.0 for all interfaces)
            port: Port to listen on (default: 80)
            users_file: Path to users.json
            blackout_file: Path to blackout.json
            default_unlock_ms: Default unlock duration in milliseconds
        """
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        
        # Set class variables for handler
        RFIDAuthorizationHandler.users_file = users_file
        RFIDAuthorizationHandler.blackout_file = blackout_file
        RFIDAuthorizationHandler.default_unlock_duration_ms = default_unlock_ms
    
    def start(self):
        """Start the HTTP server in a background thread."""
        try:
            self.server = HTTPServer((self.host, self.port), RFIDAuthorizationHandler)
            self.thread = Thread(target=self._run_server, daemon=True)
            self.thread.start()
            print(f"[RFID SERVER] Started on http://{self.host}:{self.port}")
            print(f"[RFID SERVER] ESP32 should POST to http://<pi_ip>:{self.port}/rfid")
        except Exception as e:
            print(f"[RFID SERVER ERROR] Failed to start server: {e}")
            raise
    
    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            print("[RFID SERVER] Listening for ESP32 requests...")
            self.server.serve_forever()
        except Exception as e:
            print(f"[RFID SERVER ERROR] Server stopped: {e}")
    
    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            print("[RFID SERVER] Stopping...")
            self.server.shutdown()
            self.server.server_close()
            if self.thread:
                self.thread.join(timeout=5)
            print("[RFID SERVER] Stopped")


def start_rfid_server(host='0.0.0.0', port=80, users_file='users.json', 
                     blackout_file='blackout.json', default_unlock_ms=3000):
    """
    Convenience function to start the RFID authorization server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        users_file: Path to users.json
        blackout_file: Path to blackout.json
        default_unlock_ms: Default unlock duration
        
    Returns:
        RFIDAuthServer instance
    """
    server = RFIDAuthServer(host, port, users_file, blackout_file, default_unlock_ms)
    server.start()
    return server


if __name__ == '__main__':
    # Test server standalone
    import sys
    
    port = 8080 if len(sys.argv) < 2 else int(sys.argv[1])
    
    print(f"Starting RFID Authorization Server on port {port}")
    print("Press Ctrl+C to stop")
    
    server = start_rfid_server(port=port)
    
    try:
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
