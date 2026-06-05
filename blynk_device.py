import os
import sys
import BlynkLib
import time

# ── Read credentials from environment variables ──────────────────────────
AUTH_TOKEN = os.environ.get("BLYNK_AUTH_TOKEN")
TEMPLATE_ID = os.environ.get("BLYNK_TEMPLATE_ID")

if not AUTH_TOKEN:
    print("ERROR: BLYNK_AUTH_TOKEN environment variable is not set.")
    sys.exit(1)

if not TEMPLATE_ID:
    print("ERROR: BLYNK_TEMPLATE_ID environment variable is not set.")
    sys.exit(1)

print(f"Connecting to Blynk with template: {TEMPLATE_ID}")

# ── Connection state tracking ─────────────────────────────────────────────
connected = False
connection_failed = False

blynk = BlynkLib.Blynk(AUTH_TOKEN)

@blynk.on("connected")
def blynk_connected(ping):
    global connected
    connected = True
    print(f"SUCCESS: Connected to Blynk! Ping: {ping}ms")

    # Send a test value to virtual pin V0
    blynk.virtual_write(0, "CI-OK")
    print("Sent 'CI-OK' to virtual pin V0")

@blynk.on("disconnected")
def blynk_disconnected():
    global connection_failed
    if not connected:
        connection_failed = True
    print("Disconnected from Blynk.")

# ── Run for a short window, then exit ────────────────────────────────────
TIMEOUT_SECONDS = 15
start = time.time()

while time.time() - start < TIMEOUT_SECONDS:
    blynk.run()
    if connected:
        # Give it a moment to send the virtual write, then exit clean
        time.sleep(1)
        print("Done. Exiting successfully.")
        sys.exit(0)

# If we reach here, we never connected
print("ERROR: Could not connect to Blynk within timeout. Invalid token or network issue.")
sys.exit(1)
