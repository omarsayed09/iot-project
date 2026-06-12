import time
import random
import os
import urllib.request

AUTH_TOKEN = os.environ.get("BLYNK_AUTH_TOKEN", "")
TEMPLATE_ID = os.environ.get("BLYNK_TEMPLATE_ID", "")

print(f"Token: {AUTH_TOKEN[:6]}...")
print(f"Template: {TEMPLATE_ID}")
print("Starting IoT dummy device...")

def blynk_write(pin, value):
    url = f"https://blynk.cloud/external/api/update?token={AUTH_TOKEN}&V{pin}={value}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"Error writing V{pin}: {e}")
        return False

def blynk_check_token():
    url = f"https://blynk.cloud/external/api/isHardwareConnected?token={AUTH_TOKEN}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return True
    except Exception as e:
        print(f"Token check failed: {e}")
        return False

# Verify token on startup
if not blynk_check_token():
    print("ERROR: Could not connect to Blynk. Check your token.")
    exit(1)

print("Connected to Blynk!")

while True:
    temp = round(random.uniform(20.0, 35.0), 1)
    humidity = round(random.uniform(40.0, 80.0), 1)

    ok_t = blynk_write(0, temp)
    ok_h = blynk_write(1, humidity)

    if ok_t and ok_h:
        print(f"Sent → Temp: {temp}°C | Humidity: {humidity}%")
    
    time.sleep(3)
