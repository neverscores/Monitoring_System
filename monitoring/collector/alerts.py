import time
import logging
from datetime import datetime, timedelta
import yaml
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed


# Load configuration
load_dotenv()

def load_config():
    config_path = Path(__file__).parent/"config"/"config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# Alert cooldown tracking
last_alert_times = {}

def check_cooldown(metric_name):
    """Check if alert is within cooldown window"""
    cooldown = config['alerts']['cooldown']
    last_alert = last_alert_times.get(metric_name)
    
    if last_alert and (datetime.now() - last_alert) < timedelta(seconds=cooldown):
        return True
    return False

def send_email_alert(metric, value, threshold):
    if not config['alerts']['email']['enabled']:
        return
    
    try:
        msg = EmailMessage()
        msg.set_content(
            f"ALERT: {metric} usage {value}% exceeds threshold {threshold}%\n"
            f"Host: {config['hostname']}\n"
            f"Time: {datetime.now()}"
        )
        msg['Subject'] = f"[ALERT] High {metric} usage on {config['hostname']}"
        msg['From'] = config['alerts']['email']['sender']
        msg['To'] = config['alerts']['email']['recipient']

        with smtplib.SMTP(
            config['alerts']['email']['smtp_server'],
            config['alerts']['email']['smtp_port']
        ) as server:
            server.starttls()
            server.login(
                config['alerts']['email']['sender'],
                os.getenv('SMTP_password')
            )
            server.send_message(msg)
        
        logging.info(f"Email alert sent for {metric}")
    except Exception as e:
        logging.error(f"Failed to send email alert: {str(e)}")
        
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_slack_alert(metric, value, threshold):
    if not config['alerts']['slack']['enabled']:
        return
    
    try:
        message = {
            "text": f":warning: ALERT: {metric} usage {value}% exceeds threshold {threshold}%",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*ALERT* on {config['hostname']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Metric:*\n{metric}"},
                        {"type": "mrkdwn", "text": f"*Value:*\n{value}%"},
                        {"type": "mrkdwn", "text": f"*Threshold:*\n{threshold}%"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{datetime.now()}"}
                    ]
                }
            ]
        }
        
        requests.post(
            os.getenv('slack_webhook_url'),
            json=message,
            timeout=5
        )
        
        logging.info(f"Slack alert sent for {metric}")
    except Exception as e:
        logging.error(f"Failed to send Slack alert: {str(e)}")

def log_alert(metric, value, threshold):
    logging.warning(
        f"Threshold exceeded - {metric}: {value}% (threshold: {threshold}%)",
        extra={
            "alert": {
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "host": config['hostname'],
                "timestamp": datetime.now().isoformat()
            }
        }
    )

def check_thresholds(metrics,config):
    """Check metrics against configured thresholds"""
    thresholds = config['alerts']['thresholds']
    
    for metric, value in metrics.items():
        if metric not in thresholds:
            continue
            
        threshold = thresholds[metric]
        if value >= threshold and not check_cooldown(metric):
            # Trigger alerts
            if config['alerts']['email']['enabled']:
                send_email_alert(metric, value, threshold)
            
            if config['alerts']['slack']['enabled']:
                send_slack_alert(metric, value, threshold)
            
            log_alert(metric, value, threshold)
            
            # Update last alert time
            last_alert_times[metric] = datetime.now()

if __name__ == "__main__":
    # Test all alerts
    print("Testing alerts...")
    check_thresholds({'cpu': 90, 'memory': 85, 'disk': 95})            