"""
OmniChannel Gemini Key-Ring Rotator
Multi-Key Pooling Engine for 10,000-Video Continuous Production.
Automatically rotates free Gemini API keys, balances 15 RPM / 1,500 RPD limits,
and handles auto-failover with 0 Antigravity token cost.
"""

import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("key_rotator")

POOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_key_pool.json")
LOCAL_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_api_key.local")


class GeminiKeyRing:
    def __init__(self):
        self._lock = threading.Lock()
        self.keys: List[Dict[str, Any]] = []
        self.current_idx = 0
        self.load_keys()

    def load_keys(self):
        with self._lock:
            self.keys = []
            # 1. Load primary key from gemini_api_key.local
            if os.path.exists(LOCAL_KEY_FILE):
                primary_key = open(LOCAL_KEY_FILE, "r", encoding="utf-8").read().strip()
                if primary_key:
                    self.keys.append({
                        "key": primary_key,
                        "label": "Primary Key 01",
                        "rpm_count": 0,
                        "daily_count": 0,
                        "last_used": 0.0,
                        "status": "active"
                    })

            # 2. Load additional keys from pool file if present
            if os.path.exists(POOL_FILE):
                try:
                    with open(POOL_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data.get("keys", []):
                            k = item.get("key", "").strip()
                            if k and not any(existing["key"] == k for existing in self.keys):
                                self.keys.append({
                                    "key": k,
                                    "label": item.get("label", f"Key {len(self.keys)+1:02d}"),
                                    "rpm_count": 0,
                                    "daily_count": 0,
                                    "last_used": 0.0,
                                    "status": "active"
                                })
                except Exception as e:
                    logger.warning(f"Error loading key pool: {e}")

            logger.info(f"🔑 Gemini Key-Ring loaded with {len(self.keys)} active API keys.")

    def add_key(self, api_key: str, label: str = "") -> bool:
        api_key = api_key.strip()
        if not api_key:
            return False

        with self._lock:
            if any(k["key"] == api_key for k in self.keys):
                return True

            new_label = label or f"Key {len(self.keys)+1:02d}"
            self.keys.append({
                "key": api_key,
                "label": new_label,
                "rpm_count": 0,
                "daily_count": 0,
                "last_used": 0.0,
                "status": "active"
            })
            self.save_pool()
            logger.success(f"Added new Gemini key to pool: {new_label} ({api_key[:6]}...{api_key[-4:]})")
            return True

    def save_pool(self):
        clean_keys = [{"key": k["key"], "label": k["label"]} for k in self.keys]
        with open(POOL_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_keys": len(clean_keys), "keys": clean_keys}, f, indent=2)

    def get_next_key(self) -> str:
        with self._lock:
            if not self.keys:
                raise ValueError("No Gemini keys available in Key-Ring!")

            now = time.time()
            # Reset RPM counters for keys not used in last 60 seconds
            for k in self.keys:
                if now - k["last_used"] > 60:
                    k["rpm_count"] = 0

            # Round-robin selection
            start_idx = self.current_idx
            for _ in range(len(self.keys)):
                cand = self.keys[self.current_idx]
                self.current_idx = (self.current_idx + 1) % len(self.keys)
                if cand["status"] == "active" and cand["rpm_count"] < 14:
                    cand["rpm_count"] += 1
                    cand["daily_count"] += 1
                    cand["last_used"] = now
                    return cand["key"]

            # If all at RPM limit, pick the one with oldest last_used and sleep briefly
            oldest = min(self.keys, key=lambda x: x["last_used"])
            wait_time = max(0.5, 61.0 - (now - oldest["last_used"]))
            logger.info(f"⏳ Rate-limit throttle: sleeping {wait_time:.1f}s for key reset...")
            time.sleep(wait_time)
            oldest["rpm_count"] = 1
            oldest["daily_count"] += 1
            oldest["last_used"] = time.time()
            return oldest["key"]

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_keys": len(self.keys),
                "total_capacity_rpd": len(self.keys) * 1500,
                "keys": [
                    {
                        "label": k["label"],
                        "masked": f"{k['key'][:6]}...{k['key'][-4:]}",
                        "rpm_used": k["rpm_count"],
                        "daily_used": k["daily_count"],
                        "status": k["status"]
                    }
                    for k in self.keys
                ]
            }


KEY_RING = GeminiKeyRing()


def call_gemini_rotator(prompt: str, model: str = "gemini-flash-latest", max_retries: int = 5) -> str:
    """Executes Gemini generation with automated key-ring failover and load balancing."""
    for attempt in range(max_retries):
        key = KEY_RING.get_next_key()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "topP": 0.95}
        }
        req_data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning(f"Key rate limit hit (429), rotating to next key...")
                time.sleep(1)
            else:
                logger.warning(f"Gemini API error (HTTP {e.code}): {e}")
                time.sleep(2)
        except Exception as e:
            logger.warning(f"Request exception on attempt {attempt+1}: {e}")
            time.sleep(2)

    raise RuntimeError(f"All Gemini Key-Ring attempts failed after {max_retries} retries!")


if __name__ == "__main__":
    status = KEY_RING.get_status()
    print("Gemini Key-Ring Status:", json.dumps(status, indent=2))
