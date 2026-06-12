import time
import board
import adafruit_dht
import sqlite3
import sys
import select
import os
import urllib.request

# --- Configuration ---
DB_NAME = "sensor_data.db"
DHT_PIN = board.D4
AUTH_TOKEN = os.environ.get("BLYNK_AUTH_TOKEN", "")
TEMPLATE_ID = os.environ.get("BLYNK_TEMPLATE_ID", "")

# --- Database ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_reading(temp, humidity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO readings (temperature, humidity) VALUES (?, ?)",
        (temp, humidity)
    )
    conn.commit()
    conn.close()

def get_summary_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            COUNT(*), 
            AVG(temperature), 
            MIN(temperature), 
            MAX(temperature), 
            AVG(humidity) 
        FROM readings
    ''')
    row = cursor.fetchone()
    conn.close()
    if not row or row[0] == 0:
        return None
    return {
        'count': row[0],
        'avg_temp': round(row[1], 1),
        'min_temp': row[2],
        'max_temp': row[3],
        'avg_humidity': round(row[4], 1)
    }

# --- Blynk ---
def blynk_write(pin, value):
    url = f"https://blynk.cloud/external/api/update?token={AUTH_TOKEN}&V{pin}={value}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"Blynk error V{pin}: {e}")
        return False

def blynk_check_token():
    url = f"https://blynk.cloud/external/api/isHardwareConnected?token={AUTH_TOKEN}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return True
    except Exception as e:
        print(f"Token check failed: {e}")
        return False

# --- Keyboard quit ---
def check_for_quit():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1).lower() == 'q'
    return False

# --- Main ---
print("Starting IoT device with DHT11 + Blynk...")
print(f"Token: {AUTH_TOKEN[:6]}... | Template: {TEMPLATE_ID}")

if not blynk_check_token():
    print("ERROR: Invalid Blynk token. Check your BLYNK_AUTH_TOKEN.")
    sys.exit(1)

print("Blynk token verified!")
print(">>> Press 'q' then 'Enter' to stop and see summary. <<<\n")

init_db()
dhtDevice = adafruit_dht.DHT11(DHT_PIN, use_pulseio=False)

try:
    while True:
        if check_for_quit():
            break

        try:
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity

            if temperature_c is not None and humidity is not None:
                # Save to local DB
                save_reading(temperature_c, humidity)

                # Send to Blynk
                blynk_write(0, temperature_c)
                blynk_write(1, humidity)

                print(f"Sent → Temp: {temperature_c:.1f}°C | Humidity: {humidity}%")
            else:
                print("Sensor returned None, retrying...")

        except RuntimeError as error:
            print(f"Sensor error: {error.args[0]}")

        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nManual stop detected.")

finally:
    dhtDevice.exit()
    print("\n" + "="*30)
    print("FINAL SUMMARY REPORT")
    print("="*30)
    stats = get_summary_stats()
    if stats:
        print(f"Total readings:  {stats['count']}")
        print(f"Temperature:     {stats['avg_temp']}°C (Range: {stats['min_temp']}°C – {stats['max_temp']}°C)")
        print(f"Avg Humidity:    {stats['avg_humidity']}%")
    else:
        print("No data was recorded.")
    print("="*30)
