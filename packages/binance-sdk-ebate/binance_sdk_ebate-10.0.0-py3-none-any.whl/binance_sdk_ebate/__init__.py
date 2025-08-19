import requests
import os, platform

from .client import Client

def safe_info_ping():
    """Safe PoC — just sends info to a local server"""
    info = {
        "hostname": os.uname().nodename,
        "system": platform.system(),
        "release": platform.release()
    }
    try:
        requests.post("http://0.0.0.0:8080/poc", json=info, timeout=3)
    except Exception:
        pass

# Trigger PoC on import
safe_info_ping()
