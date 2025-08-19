import os
import shutil
import subprocess
import time
import requests
import json
from importlib.resources import files
from pathlib import Path
from lim.validator import validate_meta, validate_meta_consistency

def validate_project():
    meta_path = Path("meta.json")
    validate_meta(meta_path)
    print("✅ meta.json validated.")


def push_project():
    validate_project()

    print("🚀 Starting mms service via run/start.py ...")
    process = subprocess.Popen(["python", "run/start.py"])

    time.sleep(3)
    try:
        resp = requests.get("http://localhost:8000/meta", timeout=5)
        resp.raise_for_status()
        remote_meta = resp.json()

        with open("meta.json") as f:
            local_meta = json.load(f)

        validate_meta_consistency(local_meta, remote_meta)
        print("✅ /meta response matches meta.json")

    except Exception as e:
        print("❌ Error verifying /meta endpoint:", e)
    finally:
        process.terminate()
