import os
import re
import shutil
import subprocess
import time
from typing import Any, Dict, Iterable, List, Tuple
import requests
import json
from importlib.resources import files
from pathlib import Path
from mm.validator import validate_meta, validate_meta_consistency


def get_template_path():
    return files("mm.template")


TEMPLATE_DIR = get_template_path()

_slug_rx = re.compile(r"[^a-z0-9\-._]")


def _slug(s: str) -> str:
    s = s.strip().lower().replace(" ", "-")
    s = s.replace("/", "-")
    s = _slug_rx.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "untitled"


def _find_meta_path(cwd: Path = Path(".")) -> Path:
    candidates = [cwd / "meta.json"]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("meta.json not found (looked in ./meta.json)")


def _iter_lim_targets(meta: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
    """(kept for backwards-compat) Yield (base_url, path) for each domain."""
    lim_list = meta.get("lim")
    if not isinstance(lim_list, list):
        return

    for entry in lim_list:
        if not isinstance(entry, dict):
            continue

        base = (entry.get("url") or "").rstrip("/")
        if not base:
            continue

        domains = entry.get("domain") or meta.get("domain") or []
        if not isinstance(domains, list):
            continue

        for item in domains:
            if not isinstance(item, (list, tuple)) or not item:
                continue
            segs = [_slug(str(x))
                    for x in item if isinstance(x, (str, int, float))]
            segs = [s for s in segs if s]
            if not segs:
                continue
            lim_path = "/models/mm/" + "/".join(segs)
            yield (base, lim_path)


def _iter_lim_bases(meta: Dict[str, Any]) -> Iterable[str]:
    """Yield unique base URLs from meta.lim[*].url (trim trailing '/')."""
    lim_list = meta.get("lim")
    if not isinstance(lim_list, list):
        return
    seen = set()
    for entry in lim_list:
        if not isinstance(entry, dict):
            continue
        base = (entry.get("url") or "").rstrip("/")
        if base and base not in seen:
            seen.add(base)
            yield base


def _post_with_retries(
    session: requests.Session,
    url: str,
    json_body: Dict[str, Any],
    headers: Dict[str, str],
    retries: int = 3,
    timeout: int = 20,
) -> requests.Response:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.post(url, headers=headers,
                                json=json_body, timeout=timeout)
            if resp.status_code >= 500:
                raise requests.HTTPError(
                    f"Server {resp.status_code}: {resp.text}")
            return resp
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * attempt)
            else:
                raise last_err


def init_project(name: str):
    dest = Path(name)
    if dest.exists():
        raise FileExistsError(f"Project directory '{name}' already exists.")
    shutil.copytree(TEMPLATE_DIR, dest)
    print(f"✅ Project '{name}' created at {dest.resolve()}")


def validate_project():
    meta_path = _find_meta_path()
    validate_meta(meta_path)
    print("✅ meta.json validated.")


def push_project():
    meta_path = _find_meta_path()
    print(f"Validating meta.json at {meta_path.resolve()}")
    validate_meta(meta_path)
    meta: Dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))

    token = os.getenv("MM_TOKEN") or os.getenv("LIM_TOKEN")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    bases = list(_iter_lim_bases(meta))
    if not bases:
        print("ℹ️  No 'lim' targets found in meta.json; nothing to push.")
        return

    print("🚀 Pushing meta.json to LIM service(s)...")
    session = requests.Session()
    ok = 0
    errs: List[str] = []

    for base_url in bases:
        push_url = f"{base_url}/push"
        payload = {"meta": meta}  # server expands per-lim domains
        try:
            resp = _post_with_retries(session, push_url, payload, headers)
            if resp.status_code in (200, 201):
                print(f"✅ {base_url} - stored")
                ok += 1
            else:
                msg = f"❌ {base_url} - HTTP {resp.status_code} {resp.text[:200]}"
                print(msg)
                errs.append(msg)
        except Exception as e:
            msg = f"❌ {base_url} - {e}"
            print(msg)
            errs.append(msg)

    if errs:
        print(f"\n⚠️  Completed with {len(errs)} error(s).")
    print(f"✅ Successfully pushed to {ok}/{len(bases)} target(s).")


def start_project():
    validate_project()
    print("🚀 Starting mms service via run/start.py ...")
    try:
        process = subprocess.Popen(["python", "run/start.py"])
        print("✅ process started successfully.")
    except Exception as e:
        print("❌ Error verifying /meta endpoint:", e)
    finally:
        process.terminate()
