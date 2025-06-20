# influx_client.py
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import os

load_dotenv()

# InfluxDB credentials 
INFLUXDB_URL = os.getenv("influxdb_url")
INFLUXDB_TOKEN = os.getenv("influxdb_token")
INFLUXDB_ORG = os.getenv("influxdb_org")
INFLUXDB_BUCKET = os.getenv("influxdb_bucket")

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, timeout = 30_000)
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_metrics(metrics: dict):
    point = Point("system_metrics") \
        .tag("host", metrics["hostname"]) \
        .field("cpu_avg", metrics["cpu"]["average"]) \
        .field("memory_used", metrics["memory"]["used"]) \
        .field("memory_total", metrics["memory"]["total"]) \
        .time(metrics["timestamp"], WritePrecision.S)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
