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

print(f"Connecting to Blynk with template: {TEMPLATE_ID}")

# Write value "CI-OK" to virtual pin V0
url = f"https://blynk.cloud/external/api/update?token={AUTH_TOKEN}&V0=CI-OK"

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode()
        status = response.status
        print(f"Response status: {status}")
        print(f"Response body: {body}")

        if status == 200:
            print("SUCCESS: Connected and wrote to Blynk!")
            sys.exit(0)
        else:
            print("ERROR: Unexpected response from Blynk.")
            sys.exit(1)

except urllib.error.HTTPError as e:
    print(f"ERROR: HTTP {e.code} - {e.reason}")
    sys.exit(1)

except urllib.error.URLError as e:
    print(f"ERROR: Could not reach Blynk - {e.reason}")
    sys.exit(1)
