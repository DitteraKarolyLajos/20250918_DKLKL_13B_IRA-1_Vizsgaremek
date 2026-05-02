import requests
import urllib3
import csv
from datetime import datetime
import time


def run_cpu_check():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    HOST = "sbx-nxos-mgmt.cisco.com"
    PORT = 443
    USERNAME = "kovaacslevi"
    PASSWORD = "02-Mu_H2nNrSmt"

    CPU_THRESHOLD = 80
    LOG_FILE = "nexus_cpu_log.csv"
    WEBHOOK_URL = "[DISCORD_WEBHOOK_LINK]"

    URL = f"https://{HOST}:{PORT}/ins"

    HEADERS = {
        "Content-Type": "application/json"
    }

    payload = {
        "ins_api": {
            "version": "1.0",
            "type": "cli_show",
            "chunk": "0",
            "sid": "1",
            "input": "show system resources",
            "output_format": "json"
        }
    }

    print("Connecting to Nexus NX-API...")

    response = requests.post(
        URL,
        auth=(USERNAME, PASSWORD),
        headers=HEADERS,
        json=payload,
        verify=False,
        timeout=10
    )

    if response.status_code != 200:
        print(f"NX-API error: {response.status_code}")
        print(response.text)
        exit()

    try:
        data = response.json()
        body = data["ins_api"]["outputs"]["output"]["body"]

        idle = float(body["cpu_state_idle"])
        cpu_usage = round(100 - idle, 2)

    except Exception as e:
        print("JSON parsing failed:", e)
        print("Raw response:", response.text)
        exit()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] CPU Usage: {cpu_usage}%")

    # SAVE TO CSV
    try:
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            # Write header only once
            if f.tell() == 0:
                writer.writerow(["timestamp", f"cpu_usage_percent"])

            writer.writerow([timestamp, f"{cpu_usage}%"])

    except Exception as e:
        print("CSV write failed:", e)

    # ALERT LOGIC
    if cpu_usage > CPU_THRESHOLD:
        print("WARNING: CPU threshold exceeded!")

        if WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL":
            payload = {
                "content": (
                    f"⚠ Nexus CPU Alert ⚠\n"
                    f"Time: {timestamp}\n"
                    f"CPU Usage: {cpu_usage}%\n"
                    f"Threshold: {CPU_THRESHOLD}%"
                )
            }
            try:
                requests.post(WEBHOOK_URL, json=payload)
                print("Alert sent.")
            except Exception as e:
                print("Failed to send alert:", e)
    else:
        print("CPU is normal.")



while True:
    # Run the CPU check
    run_cpu_check()

    print("Waiting 5 minutes before next check...")
    time.sleep(300)
