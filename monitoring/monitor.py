#!/usr/bin/env python3
# monitor.py

import time
import yaml
import requests
import logging
import json
from collector.metrics import collect_metrics
from collector.alerts import check_thresholds
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def load_config():
    config_path = Path(__file__).parent/"config"/"config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.FileHandler("logs/monitor.log"), logging.StreamHandler()]
    )

def json_log(level, message, **kwargs):
    log_entry = {"level": level, "message": message, "timestamp": time.time()}
    log_entry.update(kwargs)
    logging.info(json.dumps(log_entry))

def send_to_cloud(endpoint, data, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    try:
        print("Payload to send:\n", json.dumps(data, indent=2))
        response = requests.post(endpoint, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        json_log("info", "Metrics sent to cloud", status=response.status_code)
    except requests.RequestException as e:
        json_log("error", "Failed to send metrics", error=str(e))

def main():
    setup_logging()
    config = load_config()
    interval = config.get("interval", 10)
    endpoint = config["cloud"]["endpoint"]
    token = os.getenv("auth_token","")
    thresholds = config["alerts"]["thresholds"]

    json_log("info", "Monitoring service started")

    while True:
        collected = collect_metrics()
        print("Collected metrics:", collected)

        send_to_cloud(endpoint, collected, token)
        # Flatten metrics for alerting
        flat_metrics = {
            "cpu": collected["cpu"]["average"],
            "memory": collected["memory"]["percent"],
            "disk": collected["disk"]["percent"]
        }
        check_thresholds(flat_metrics,config)
        time.sleep(interval)
        


if __name__ == "__main__":
    main()
