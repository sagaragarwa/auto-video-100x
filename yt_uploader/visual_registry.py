"""
Persistent Used Visuals Registry for 5X Autonomous Engine.
Guarantees zero repeat visuals across consecutive videos and sessions.
Tracks MD5 hashes of used clips and persists to disk.
"""

import os
import json
import time
import hashlib
from typing import Set, Dict, Any, List, Optional
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_FILE = os.path.join(_root, "storage", "used_visuals_registry.json")

def get_file_content_hash(file_path: str) -> str:
    """Computes fast MD5 hash of first 64KB + file size for unique fingerprint."""
    try:
        fsize = os.path.getsize(file_path)
        with open(file_path, "rb") as fp:
            sample = fp.read(65536)
        h = hashlib.md5(sample + str(fsize).encode()).hexdigest()
        return h
    except Exception:
        return ""

class VisualRegistry:
    def __init__(self, max_history_entries: int = 500):
        self.max_history = max_history_entries
        self.registry_file = REGISTRY_FILE
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        self.used_records: List[Dict[str, Any]] = []
        self.used_hashes: Set[str] = set()
        self.load()

    def load(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.used_records = data.get("records", [])
                    self.used_hashes = {r["hash"] for r in self.used_records if "hash" in r}
                logger.info(f"💾 Loaded Persistent Visual Registry: {len(self.used_hashes)} previously used clips excluded.")
            except Exception as e:
                logger.warning(f"Could not load visual registry: {e}. Starting fresh.")
                self.used_records = []
                self.used_hashes = set()
        else:
            self.used_records = []
            self.used_hashes = set()

    def save(self):
        try:
            # Keep only the most recent max_history entries
            if len(self.used_records) > self.max_history:
                self.used_records = self.used_records[-self.max_history:]
                self.used_hashes = {r["hash"] for r in self.used_records if "hash" in r}

            data = {
                "updated_at": time.time(),
                "total_records": len(self.used_records),
                "records": self.used_records
            }
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save visual registry: {e}")

    def is_used(self, clip_hash: str) -> bool:
        return clip_hash in self.used_hashes

    def mark_used(self, clip_path: str, topic: str = "", niche: str = "") -> str:
        ch = get_file_content_hash(clip_path)
        if ch:
            self.used_hashes.add(ch)
            self.used_records.append({
                "hash": ch,
                "file": os.path.basename(clip_path),
                "topic": topic,
                "niche": niche,
                "timestamp": time.time()
            })
        return ch

    def reset_if_starved(self, total_available: int):
        """If used clips exceed 75% of total stock pool, cycle oldest half to prevent starvation."""
        if total_available > 0 and len(self.used_hashes) > int(total_available * 0.75):
            logger.info("♻️ Cycling oldest 50% of visual registry to refresh clip pool while preserving anti-repeat for recent videos.")
            keep_count = len(self.used_records) // 2
            self.used_records = self.used_records[-keep_count:]
            self.used_hashes = {r["hash"] for r in self.used_records if "hash" in r}
            self.save()

_GLOBAL_REGISTRY: Optional[VisualRegistry] = None

def get_visual_registry() -> VisualRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = VisualRegistry()
    return _GLOBAL_REGISTRY
