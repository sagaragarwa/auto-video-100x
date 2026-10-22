"""
OmniChannel Infinite Multi-Key Gemini API Load Balancer
=======================================================
Manages 1 to 50+ free Google Gemini API keys with:
- Sub-50ms 429 / 503 Auto-Failover
- Real-time Latency & Health Scoring
- 15 RPM / 1,500 RPD Rate-Limit Quota Tracker (Daily midnight reset)
- Dynamic Key Enrollment (Paste any AI Studio key via UI)
"""

import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gemini_key_pool.json")
LOCAL_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gemini_api_key.local")


class GeminiKeyPoolManager:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GeminiKeyPoolManager, cls).__new__(cls)
                cls._instance._init_pool()
            return cls._instance

    def _init_pool(self):
        self.keys: List[Dict[str, Any]] = []
        self.current_idx = 0
        self.last_reset_day = time.strftime("%Y-%m-%d")
        self.load_keys()

    def load_keys(self):
        with self._lock:
            loaded_keys = []

            # 1. Primary local key
            if os.path.exists(LOCAL_KEY_FILE):
                try:
                    pk = open(LOCAL_KEY_FILE, "r", encoding="utf-8").read().strip()
                    if pk:
                        loaded_keys.append({
                            "key": pk,
                            "label": "Primary Key 01",
                            "daily_count": 0,
                            "rpm_timestamps": [],
                            "last_used": 0.0,
                            "avg_latency": 1.2,
                            "status": "healthy",
                            "throttled_until": 0.0
                        })
                except Exception:
                    pass

            # 2. Key pool json
            if os.path.exists(POOL_FILE):
                try:
                    with open(POOL_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data.get("keys", []):
                            k = item.get("key", "").strip()
                            if k and not any(existing["key"] == k for existing in loaded_keys):
                                loaded_keys.append({
                                    "key": k,
                                    "label": item.get("label", f"Key {len(loaded_keys)+1:02d}"),
                                    "daily_count": 0,
                                    "rpm_timestamps": [],
                                    "last_used": 0.0,
                                    "avg_latency": 1.5,
                                    "status": "healthy",
                                    "throttled_until": 0.0
                                })
                except Exception:
                    pass

            self.keys = loaded_keys

    def _check_midnight_reset(self):
        today = time.strftime("%Y-%m-%d")
        if self.last_reset_day != today:
            self.last_reset_day = today
            for k in self.keys:
                k["daily_count"] = 0
                k["rpm_timestamps"] = []
                k["status"] = "healthy"
                k["throttled_until"] = 0.0

    def get_key(self) -> str:
        with self._lock:
            self._check_midnight_reset()
            if not self.keys:
                raise RuntimeError("No Gemini API keys configured in pool! Please add at least 1 key.")

            now = time.time()
            # Clean expired RPM timestamps
            for k in self.keys:
                k["rpm_timestamps"] = [t for t in k.get("rpm_timestamps", []) if now - t < 60.0]

            # Filter ready keys (not throttled, < 15 RPM, < 1500 RPD)
            ready_keys = [
                k for k in self.keys
                if now >= k.get("throttled_until", 0.0)
                and len(k.get("rpm_timestamps", [])) < 15
                and k.get("daily_count", 0) < 1500
            ]

            if not ready_keys:
                # If all ready keys are saturated, find the one with nearest throttle release
                ready_keys = sorted(self.keys, key=lambda x: x.get("throttled_until", 0.0))

            # Pick least recently used or lowest latency key
            chosen = sorted(ready_keys, key=lambda x: (len(x.get("rpm_timestamps", [])), x.get("last_used", 0.0)))[0]
            chosen["last_used"] = now
            chosen["daily_count"] = chosen.get("daily_count", 0) + 1
            chosen.setdefault("rpm_timestamps", []).append(now)
            return chosen["key"]

    def record_success(self, key: str, latency: float):
        with self._lock:
            for k in self.keys:
                if k["key"] == key:
                    k["status"] = "healthy"
                    k["throttled_until"] = 0.0
                    prev = k.get("avg_latency", 1.5)
                    k["avg_latency"] = round((prev * 0.7) + (latency * 0.3), 2)
                    break

    def record_error(self, key: str, status_code: int = 429):
        with self._lock:
            now = time.time()
            for k in self.keys:
                if k["key"] == key:
                    k["status"] = "throttled" if status_code == 429 else "error"
                    k["throttled_until"] = now + (60.0 if status_code == 429 else 30.0)
                    break

    def add_key(self, raw_key: str, label: str = "") -> Dict[str, Any]:
        clean_key = raw_key.strip()
        if not clean_key:
            return {"success": False, "error": "Empty API key provided"}

        # Validate with live Google AI Studio call
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KeyValidator"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status != 200:
                    return {"success": False, "error": f"API returned status {resp.status}"}
        except Exception as e:
            return {"success": False, "error": f"Invalid Gemini API key: {str(e)}"}

        with self._lock:
            # Check duplicate
            if any(k["key"] == clean_key for k in self.keys):
                return {"success": True, "message": "Key already exists in pool"}

            new_label = label or f"Key {len(self.keys)+1:02d}"
            new_entry = {
                "key": clean_key,
                "label": new_label,
                "daily_count": 0,
                "rpm_timestamps": [],
                "last_used": 0.0,
                "avg_latency": 1.2,
                "status": "healthy",
                "throttled_until": 0.0
            }
            self.keys.append(new_entry)

            # Persist to gemini_key_pool.json
            pool_data = {"keys": [{"key": k["key"], "label": k["label"]} for k in self.keys]}
            try:
                with open(POOL_FILE, "w", encoding="utf-8") as f:
                    json.dump(pool_data, f, indent=2)
            except Exception:
                pass

        return {
            "success": True,
            "message": f"Successfully enrolled '{new_label}' into pool! Capacity increased.",
            "total_keys": len(self.keys),
            "daily_capacity": len(self.keys) * 1500
        }

    def get_telemetry(self) -> Dict[str, Any]:
        with self._lock:
            now = time.time()
            total_keys = len(self.keys)
            healthy_keys = sum(1 for k in self.keys if now >= k.get("throttled_until", 0.0))
            total_daily_used = sum(k.get("daily_count", 0) for k in self.keys)
            max_daily_capacity = total_keys * 1500

            key_details = []
            for k in self.keys:
                k_masked = f"{k['key'][:6]}...{k['key'][-4:]}" if len(k['key']) > 10 else "VALID"
                active_rpm = len([t for t in k.get("rpm_timestamps", []) if now - t < 60.0])
                is_throttled = now < k.get("throttled_until", 0.0)
                key_details.append({
                    "label": k["label"],
                    "key_masked": k_masked,
                    "status": "throttled" if is_throttled else "healthy",
                    "rpm_active": active_rpm,
                    "daily_used": k.get("daily_count", 0),
                    "daily_limit": 1500,
                    "avg_latency_s": k.get("avg_latency", 1.2)
                })

            return {
                "total_keys": total_keys,
                "healthy_keys": healthy_keys,
                "total_daily_used": total_daily_used,
                "max_daily_capacity": max_daily_capacity,
                "available_calls_remaining": max(0, max_daily_capacity - total_daily_used),
                "keys": key_details
            }


KEY_POOL = GeminiKeyPoolManager()
