# collector/metrics.py
import psutil
import socket
import time

def collect_metrics():
    timestamp = int(time.time())
    hostname = socket.gethostname()

    # CPU (simulate per-core and average)
    per_core = psutil.cpu_percent(interval=None, percpu=True)
    average = sum(per_core) / len(per_core) if per_core else 0.0
    cpu = {
        "per_core": per_core,
        "average": average
    }

    # Memory
    mem = psutil.virtual_memory()
    memory = {
        "total": mem.total,
        "used": mem.used,
        "free": mem.available,
        "percent": mem.percent,
    }

    # Disk (assume root '/' partition only)
    usage = psutil.disk_usage('/')
    disk = {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent,
    }

    return {
        "timestamp": timestamp,
        "hostname": hostname,
        "cpu": {
            "per_core": per_core,
            "average": average
        },
        "memory": memory,
        "disk": disk
    }