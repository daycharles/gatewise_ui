"""Small, optional TCP listener for testing door pushes.

This module implements a tiny threaded TCP server that prints any JSON
payloads it receives. It is not wired into the main UI by default — it is
meant as a developer helper for testing `push_to_door_modules()`.
"""
import socketserver
import json


class _Handler(socketserver.BaseRequestHandler):
	def handle(self):
		data = b""
		# Read until client closes
		try:
			while True:
				chunk = self.request.recv(4096)
				if not chunk:
					break
				data += chunk
		except Exception:
			pass

		try:
			text = data.decode('utf-8')
			payload = json.loads(text)
			print(f"[network_listener] Received payload from {self.client_address}: {payload}")
		except Exception:
			print(f"[network_listener] Received raw data from {self.client_address}: {data}")


def start_server(host='0.0.0.0', port=5006):
	with socketserver.ThreadingTCPServer((host, port), _Handler) as srv:
		print(f"Listening on {host}:{port} (Ctrl-C to stop)")
		try:
			srv.serve_forever()
		except KeyboardInterrupt:
			print("Shutting down")


if __name__ == '__main__':
	start_server()

