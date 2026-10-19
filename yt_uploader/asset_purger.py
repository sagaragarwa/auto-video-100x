import os
import sys
import shutil
import time
from typing import Optional, List, Dict, Any

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root_dir, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from loguru import logger

def format_bytes(num_bytes: int) -> str:
    """Formats bytes into human readable string (KB, MB, GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KB"
    elif num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_dir_size(dir_path: str) -> int:
    """Calculates total size of all files in a directory recursively."""
    total = 0
    try:
        for root, _, files in os.walk(dir_path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except Exception:
        pass
    return total

def safe_remove_file(file_path: str, max_retries: int = 3) -> bool:
    """Safely removes a file, with retries for Windows locks."""
    if not os.path.exists(file_path):
        return True
    for attempt in range(max_retries):
        try:
            os.remove(file_path)
            return True
        except OSError as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)
            else:
                logger.warning(f"Could not remove file {file_path}: {e}")
                return False
    return False

def find_associated_task_dir(video_path: str, task_id: Optional[str] = None) -> Optional[str]:
    """
    Finds the working task directory in storage/tasks associated with this video.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tasks_base = os.path.join(root_dir, "storage", "tasks")

    if not os.path.exists(tasks_base):
        return None

    # 1. Direct task_id if provided
    if task_id:
        target = os.path.join(tasks_base, task_id)
        if os.path.exists(target):
            return target

    # 2. Check if video_path itself is inside storage/tasks/<task_id>/
    norm_video = os.path.normpath(os.path.abspath(video_path))
    norm_tasks = os.path.normpath(tasks_base)
    if norm_video.startswith(norm_tasks):
        rel = os.path.relpath(norm_video, norm_tasks)
        parts = rel.split(os.sep)
        if parts:
            candidate = os.path.join(tasks_base, parts[0])
            if os.path.isdir(candidate):
                return candidate

    # 3. Check if any task dir contains files referencing or matching this video
    video_base = os.path.splitext(os.path.basename(video_path))[0]
    try:
        for entry in os.listdir(tasks_base):
            cand_path = os.path.join(tasks_base, entry)
            if not os.path.isdir(cand_path):
                continue
            # If task folder name matches video base
            if entry in video_base or video_base in entry:
                return cand_path
    except Exception:
        pass

    return None

def purge_video_assets(
    video_path: str,
    thumbnail_path: Optional[str] = None,
    task_id: Optional[str] = None,
    delete_output_video: bool = True,
    delete_task_dir: bool = True
) -> Dict[str, Any]:
    """
    Permanently deletes all assets associated with an uploaded video to reclaim 100% disk space:
    1. The rendered final video file (.mp4)
    2. The generated ultra thumbnail (.jpg / .png)
    3. Any sibling intermediate exports (e.g. _with_outro.mp4, temp clips)
    4. The entire working task directory in storage/tasks/<task_id> (contains audio.mp3, subtitle.srt, combined-*.mp4, materials)
    
    Returns a comprehensive cleanup summary with total bytes and MB/GB freed.
    """
    logger.info(f"🧹 Initiating Post-Upload Asset Purge for: {os.path.basename(video_path)}")
    
    freed_bytes = 0
    deleted_files: List[str] = []
    deleted_dirs: List[str] = []
    errors: List[str] = []

    abs_video = os.path.abspath(video_path) if video_path else ""
    video_dir = os.path.dirname(abs_video) if abs_video else ""
    video_name = os.path.basename(abs_video) if abs_video else ""
    video_stem = os.path.splitext(video_name)[0] if video_name else ""

    # Target 1: The main video file
    if delete_output_video and abs_video and os.path.exists(abs_video):
        try:
            sz = os.path.getsize(abs_video)
            if safe_remove_file(abs_video):
                freed_bytes += sz
                deleted_files.append(abs_video)
                logger.info(f"  🗑️ Deleted final video: {video_name} ({format_bytes(sz)})")
        except Exception as e:
            errors.append(f"Failed to delete video file {abs_video}: {e}")

    # Target 2: Explicit thumbnail file
    thumb_candidates = []
    if thumbnail_path:
        thumb_candidates.append(os.path.abspath(thumbnail_path))

    # Auto-detect sibling thumbnail / companion files
    if video_dir and video_stem:
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            thumb_candidates.append(os.path.join(video_dir, f"{video_stem}_thumb{ext}"))
            thumb_candidates.append(os.path.join(video_dir, f"{video_stem}{ext}"))
        
        # Sibling companion video files (e.g. with_outro, temp)
        if os.path.exists(video_dir):
            try:
                for fname in os.listdir(video_dir):
                    if fname == video_name:
                        continue
                    # Match sibling files sharing this video prefix
                    if fname.startswith(video_stem) and any(fname.endswith(sfx) for sfx in [".mp4", "_with_outro.mp4", "_thumb.jpg", "_thumb.png", ".srt"]):
                        fpath = os.path.join(video_dir, fname)
                        if os.path.isfile(fpath):
                            thumb_candidates.append(fpath)
            except Exception:
                pass

    for tf in set(thumb_candidates):
        if os.path.exists(tf) and os.path.isfile(tf):
            try:
                sz = os.path.getsize(tf)
                if safe_remove_file(tf):
                    freed_bytes += sz
                    deleted_files.append(tf)
                    logger.info(f"  🗑️ Deleted companion asset: {os.path.basename(tf)} ({format_bytes(sz)})")
            except Exception as e:
                errors.append(f"Failed to delete companion file {tf}: {e}")

    # Target 3: Associated task working directory in storage/tasks/<task_id>
    if delete_task_dir:
        target_task_dir = find_associated_task_dir(video_path, task_id)
        if target_task_dir and os.path.exists(target_task_dir):
            try:
                task_sz = get_dir_size(target_task_dir)
                shutil.rmtree(target_task_dir, ignore_errors=True)
                # Verify removal
                if not os.path.exists(target_task_dir):
                    freed_bytes += task_sz
                    deleted_dirs.append(target_task_dir)
                    logger.info(f"  🗑️ Deleted task working directory: {os.path.basename(target_task_dir)} ({format_bytes(task_sz)})")
            except Exception as e:
                errors.append(f"Failed to delete task directory {target_task_dir}: {e}")

    # Guarantee User Mandate: At least 5 GB free disk space must remain
    try:
        from yt_uploader.disk_governor import enforce_5gb_disk_headroom, get_disk_usage
        disk_guard_stats = enforce_5gb_disk_headroom(min_free_gb=5.0)
        if disk_guard_stats.get("purge_executed"):
            additional_freed = disk_guard_stats["purge_details"].get("freed_bytes", 0)
            freed_bytes += additional_freed
            logger.info(f"🛡️ Smart Disk Governor freed an additional {format_bytes(additional_freed)} to enforce 5 GB minimum headroom!")
        cur_free_gb = disk_guard_stats.get("free_gb", 0)
    except Exception as d_exc:
        logger.warning(f"Disk governor check bypassed: {d_exc}")
        cur_free_gb = None

    summary = {
        "success": len(errors) == 0,
        "freed_bytes": freed_bytes,
        "freed_human": format_bytes(freed_bytes),
        "deleted_files_count": len(deleted_files),
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
        "free_disk_gb": cur_free_gb,
        "errors": errors
    }

    headroom_msg = f" | Current Drive Free: {cur_free_gb} GB (Safe >= 5 GB)" if cur_free_gb is not None else ""
    logger.success(f"✅ Asset Purge Complete! Total Reclaimed Disk Space: {summary['freed_human']} ({len(deleted_files)} files, {len(deleted_dirs)} dirs){headroom_msg}")
    return summary
