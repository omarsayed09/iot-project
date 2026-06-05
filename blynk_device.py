import os
import sys
import urllib.request
import json

AUTH_TOKEN = os.environ.get("BLYNK_AUTH_TOKEN")
TEMPLATE_ID = os.environ.get("BLYNK_TEMPLATE_ID")

if not AUTH_TOKEN:
    print("ERROR: BLYNK_AUTH_TOKEN is not set.")
    sys.exit(1)

if not TEMPLATE_ID:
    print("ERROR: BLYNK_TEMPLATE_ID is not set.")
    sys.exit(1)

print(f"Template ID: {TEMPLATE_ID}")
print(f"Token (first 6 chars): {AUTH_TOKEN[:6]}...")

# ── Step 1: Verify token is valid by checking device info ────────────────
print("\n[1] Verifying token with Blynk...")
url = f"https://blynk.cloud/external/api/isHardwareConnected?token={AUTH_TOKEN}"

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode().strip()
        print(f"Token valid. Device online: {body}")
        # body is "true" or "false" — both are valid responses meaning token works
        # We only fail if we get an HTTP error (400 = bad token, 404 = not found)

except urllib.error.HTTPError as e:
    error_body = e.read().decode().strip()
    print(f"ERROR: HTTP {e.code} - {e.reason}")
    print(f"Response: {error_body}")
    if e.code == 400:
        print("Token is invalid or device not provisioned correctly.")
    sys.exit(1)

except urllib.error.URLError as e:
    print(f"ERROR: Could not reach Blynk - {e.reason}")
    sys.exit(1)

# ── Step 2: Try writing to virtual pin (best effort, device may be offline) ──
print("\n[2] Writing CI status to virtual pin V0...")
write_url = f"https://blynk.cloud/external/api/update?token={AUTH_TOKEN}&V0=CI-OK"

try:
    with urllib.request.urlopen(write_url, timeout=10) as response:
        print(f"Virtual pin write: OK (status {response.status})")
except urllib.error.HTTPError as e:
    # 400 here just means device is offline — token already validated above
    print(f"Virtual pin write skipped (device offline, status {e.code}) — this is expected in CI.")

print("\nSUCCESS: Blynk token validated. CI passed.")
sys.exit(0)
