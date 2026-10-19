import os
import sys
import shutil
import time
from typing import Optional, Dict, Any, List, Tuple

# Ensure root dir and .venv are on sys.path
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

_venv_site = os.path.join(_root_dir, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from loguru import logger
from yt_uploader.asset_purger import format_bytes, safe_remove_file, get_dir_size

DEFAULT_MIN_FREE_GB = 5.0  # User mandate: At least 5 GB must ALWAYS be free

def get_disk_usage(check_path: str = ".") -> Dict[str, Any]:
    """
    Returns exact disk usage stats for the partition where check_path lives.
    """
    abs_path = os.path.abspath(check_path)
    # On Windows, drive letter root, e.g. C:\
    drive_root = os.path.splitdrive(abs_path)[0] + os.sep
    usage = shutil.disk_usage(drive_root)

    total_gb = usage.total / (1024 ** 3)
    used_gb = usage.used / (1024 ** 3)
    free_gb = usage.free / (1024 ** 3)
    free_percent = (usage.free / usage.total) * 100 if usage.total > 0 else 0

    return {
        "drive": drive_root,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
        "free_percent": round(free_percent, 1),
        "free_human": format_bytes(usage.free),
        "is_safe": free_gb >= DEFAULT_MIN_FREE_GB
    }

def is_disk_space_safe(min_free_gb: float = DEFAULT_MIN_FREE_GB, check_path: str = ".") -> Tuple[bool, float]:
    """
    Checks if current free disk space is at least min_free_gb.
    Returns (is_safe, current_free_gb).
    """
    stats = get_disk_usage(check_path)
    return stats["free_gb"] >= min_free_gb, stats["free_gb"]

def deep_clean_stale_caches(
    target_free_gb: float = DEFAULT_MIN_FREE_GB,
    aggressive: bool = False
) -> Dict[str, Any]:
    """
    Smart Multi-Tier Cache & Storage Purger:
    Automatically sweeps temporary, orphaned, and cached video materials
    to ensure free disk space stays above target_free_gb (5 GB minimum).
    
    Tiers of Cleanup:
    1. storage/temp/ (all temporary files)
    2. storage/cache_material_search/ (expired query caches)
    3. Old/orphaned folders in storage/tasks/ (older than 2h or without active processes)
    4. storage/cache_videos/ (Pexels/Pixabay cached clips, sorted oldest first)
    """
    logger.info(f"🛡️ Smart Disk Governor: Checking disk headroom (Target: >= {target_free_gb} GB Free)...")
    
    init_stats = get_disk_usage(_root_dir)
    cur_free_gb = init_stats["free_gb"]
    
    freed_bytes = 0
    deleted_files = []
    deleted_dirs = []

    # If already plenty of space and not aggressive, log and return
    if cur_free_gb >= target_free_gb and not aggressive:
        return {
            "needed_cleanup": False,
            "freed_bytes": 0,
            "freed_human": "0 B",
            "current_free_gb": cur_free_gb,
            "status": "Safe"
        }

    logger.warning(f"⚠️ Low disk headroom detected! Current Free: {cur_free_gb} GB (Goal: >= {target_free_gb} GB). Starting Tiered Purge...")

    # Tier 1: storage/temp
    temp_dir = os.path.join(_root_dir, "storage", "temp")
    if os.path.exists(temp_dir):
        for f in os.listdir(temp_dir):
            fp = os.path.join(temp_dir, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                if safe_remove_file(fp):
                    freed_bytes += sz
                    deleted_files.append(fp)

    # Tier 2: storage/cache_material_search
    search_cache_dir = os.path.join(_root_dir, "storage", "cache_material_search")
    if os.path.exists(search_cache_dir):
        for f in os.listdir(search_cache_dir):
            fp = os.path.join(search_cache_dir, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                if safe_remove_file(fp):
                    freed_bytes += sz
                    deleted_files.append(fp)

    # Check space after Tier 1 & 2
    cur_free_gb = get_disk_usage(_root_dir)["free_gb"]
    if cur_free_gb >= target_free_gb and not aggressive:
        logger.success(f"✅ Disk headroom restored to {cur_free_gb} GB after Tier 1/2 cleanup.")
        return {
            "needed_cleanup": True,
            "freed_bytes": freed_bytes,
            "freed_human": format_bytes(freed_bytes),
            "current_free_gb": cur_free_gb,
            "status": "Safe"
        }

    # Tier 3: Old / Completed folders in storage/tasks
    tasks_dir = os.path.join(_root_dir, "storage", "tasks")
    if os.path.exists(tasks_dir):
        now = time.time()
        for t_folder in os.listdir(tasks_dir):
            tp = os.path.join(tasks_dir, t_folder)
            if not os.path.isdir(tp):
                continue
            # If older than 1 hour or aggressive
            try:
                mtime = os.stat(tp).st_mtime
                if aggressive or (now - mtime > 3600):
                    sz = get_dir_size(tp)
                    shutil.rmtree(tp, ignore_errors=True)
                    if not os.path.exists(tp):
                        freed_bytes += sz
                        deleted_dirs.append(tp)
            except Exception:
                pass

    # Check space after Tier 3
    cur_free_gb = get_disk_usage(_root_dir)["free_gb"]
    if cur_free_gb >= target_free_gb and not aggressive:
        logger.success(f"✅ Disk headroom restored to {cur_free_gb} GB after Tier 3 cleanup.")
        return {
            "needed_cleanup": True,
            "freed_bytes": freed_bytes,
            "freed_human": format_bytes(freed_bytes),
            "current_free_gb": cur_free_gb,
            "status": "Safe"
        }

    # Tier 4: storage/cache_videos (Stock clips - sorted oldest first)
    cache_videos_dir = os.path.join(_root_dir, "storage", "cache_videos")
    if os.path.exists(cache_videos_dir):
        video_files = []
        for root, _, files in os.walk(cache_videos_dir):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    video_files.append((fp, os.path.getmtime(fp), os.path.getsize(fp)))
                except OSError:
                    pass

        # Sort by mtime ascending (oldest first)
        video_files.sort(key=lambda x: x[1])

        for fp, _, sz in video_files:
            if safe_remove_file(fp):
                freed_bytes += sz
                deleted_files.append(fp)
            cur_free_gb = get_disk_usage(_root_dir)["free_gb"]
            # Stop once we have reached target_free_gb + 1 GB buffer
            if not aggressive and cur_free_gb >= (target_free_gb + 1.0):
                break

    final_stats = get_disk_usage(_root_dir)
    logger.success(f"🎉 Smart Disk Governor Purge Complete: Reclaimed {format_bytes(freed_bytes)} | Current Free: {final_stats['free_gb']} GB")
    
    return {
        "needed_cleanup": True,
        "freed_bytes": freed_bytes,
        "freed_human": format_bytes(freed_bytes),
        "deleted_files_count": len(deleted_files),
        "deleted_dirs_count": len(deleted_dirs),
        "current_free_gb": final_stats["free_gb"],
        "status": "Safe" if final_stats["free_gb"] >= target_free_gb else "LowSpaceAlert"
    }

def enforce_5gb_disk_headroom(min_free_gb: float = DEFAULT_MIN_FREE_GB) -> Dict[str, Any]:
    """
    Enforces that at least 5 GB of free space is available.
    If below 5 GB, automatically triggers smart tiered cache purge.
    Returns the final disk health status.
    """
    stats = get_disk_usage(_root_dir)
    if stats["free_gb"] < min_free_gb:
        logger.warning(f"🚨 Free disk space ({stats['free_gb']} GB) is below the {min_free_gb} GB safety limit! Initiating automatic recovery...")
        purge_res = deep_clean_stale_caches(target_free_gb=min_free_gb)
        stats = get_disk_usage(_root_dir)
        stats["purge_executed"] = True
        stats["purge_details"] = purge_res
    else:
        stats["purge_executed"] = False

    return stats
