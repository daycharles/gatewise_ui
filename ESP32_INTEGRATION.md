# ESP32 RFID Integration Test

Test the HTTP endpoint that ESP32 will use for authorization.

## Test with curl (Windows PowerShell)

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8080/health" -Method GET

# Test authorization with valid UID (replace with actual UID from users.json)
$body = @{
    uid = "1234567890"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/rfid" -Method POST -Body $body -ContentType "application/json"

# Test with hex format (uppercase, as ESP32 sends)
$body = @{
    uid = "ABCDEF12"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/rfid" -Method POST -Body $body -ContentType "application/json"
```

## ESP32 Configuration Update

Update your ESP32 code to point to the Raspberry Pi:

```c
// Change this line in your ESP32 code:
String piServer = "http://192.168.1.34:8080/rfid";  // Use port 8080 for testing

// On Raspberry Pi with sudo/root, you can use port 80:
// String piServer = "http://192.168.1.34/rfid";
```

## Running on Raspberry Pi

### With port 80 (requires sudo):

```bash
export GATEWISE_ADMIN_PASSWORD="your_password"
export RFID_SERVER_PORT="80"
sudo -E python3 main.py
```

### With port 8080 (no sudo needed):

```bash
export GATEWISE_ADMIN_PASSWORD="your_password"
export RFID_SERVER_PORT="8080"
python3 main.py
```

## Testing Authorization Flow

1. Make sure `users.json` exists with test users:

```json
[
  {
    "uid": "ABCDEF12",
    "name": "Test User",
    "isAdmin": false
  }
]
```

2. Test from command line:

```bash
curl -X POST http://localhost:8080/rfid \
  -H "Content-Type: application/json" \
  -d '{"uid":"ABCDEF12"}'
```

Expected response:

```json
{
  "authorized": true,
  "duration": 3000
}
```

3. Test with unauthorized UID:

```bash
curl -X POST http://localhost:8080/rfid \
  -H "Content-Type: application/json" \
  -d '{"uid":"UNKNOWN"}'
```

Expected response:

```json
{
  "authorized": false,
  "duration": 0
}
```

## Blackout Schedule Testing

If `blackout.json` has entries for current day/time, authorized users will be denied:

```json
{
  "Monday": [{ "start": "00:00", "end": "06:00" }]
}
```

## Network Setup Notes

1. Find your Pi's IP address:

   ```bash
   hostname -I
   ```

2. Update ESP32 with the correct IP and port:

   ```c
   String piServer = "http://<PI_IP_ADDRESS>:<PORT>/rfid";
   ```

3. Make sure firewall allows the port (if running on Pi):
   ```bash
   sudo ufw allow 8080/tcp
   # or for port 80:
   sudo ufw allow 80/tcp
   ```

## Troubleshooting

- **"Permission denied" on port 80**: Either run with `sudo` or use port 8080+
- **ESP32 can't connect**: Check network connectivity, firewall, and IP address
- **Always denied**: Check users.json format and UID matching (case-insensitive)
- **Server not starting**: Check if port is already in use with `netstat -ano | findstr :8080`
