"""
OmniChannel Agentic Tool Registry
=================================
Executable Python functions for Gemini Function Calling schema.
Permits the AI Commander to 100% control the entire video empire:
- Video manufacturing, Shure SM7B voice, Content ID outro lock
- Playwright YouTube Studio unlisted upload & comment pinning
- Persistent Rumble uploader
- Channel fleet configuration & quota management
- Elastic Multi-Repo Swarm dispatching (1 to unlimited runners)
- Sandboxed Python Code Interpreter
- Repository file inspection & git operations
- Dynamic Gemini API key pool management
"""

import os
import sys
import json
import time
import shutil
import subprocess
from typing import Dict, Any, List, Optional

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
YT_CHANNELS_FILE = os.path.join(_root, "yt_uploader", "channels_config.json")
RUMBLE_CHANNELS_FILE = os.path.join(_root, "yt_uploader", "rumble_config.json")
QUEUE_FILE = os.path.join(_root, "omnichannel_powerhouse", "unlisted_queue.json")
PYTHON_EXE = os.path.expanduser(r"~\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable


# --- 1. DAEMON CONTROL TOOL ---
def tool_daemon_control(action: str) -> Dict[str, Any]:
    """Control the 24/7 Perpetual Autonomous Video Daemon. Actions: 'status', 'start', 'stop'."""
    from omnichannel_powerhouse.perpetual_genius_daemon import get_daemon
    daemon = get_daemon()
    action = action.lower().strip()
    if action == "start":
        return daemon.start()
    elif action in ("stop", "pause"):
        return daemon.stop()
    else:
        return daemon.get_status()


# --- 2. TIER-1 VIDEO MANUFACTURING TOOL ---
def tool_manufacture_video(channel_key: str, topic: Optional[str] = None, duration_min: int = 40) -> Dict[str, Any]:
    """
    Manufactures an institutional 30-60 min Tier-1 English documentary:
    - 5-Act Deep Research Script via Gemini 3.5 Flash
    - Edge-TTS Tier-1 Voice + 6-Stage Shure SM7B DSP (-14 LUFS)
    - Zero-Repeat 1080p B-roll Stream + 173.25s Vintage Blue Laser Content ID Outro Lock
    - 98/100 God-Tier SEO + Pinned Comment
    - Registers in Unlisted Queue for thumbnail review
    """
    from omnichannel_powerhouse.tier1_producer import (
        synthesize_tier1_script_and_seo,
        render_tier1_master_video,
        research_channel_topics
    )

    yt_channels = {}
    if os.path.exists(YT_CHANNELS_FILE):
        try:
            yt_channels = json.load(open(YT_CHANNELS_FILE, encoding="utf-8"))
        except Exception:
            pass

    ch_data = yt_channels.get(channel_key, {
        "name": channel_key,
        "niche": "technology",
        "voice_preferred": "en-US-ChristopherNeural"
    })

    niche = ch_data.get("niche", "technology")
    ch_name = ch_data.get("name", channel_key)
    voice = ch_data.get("voice_preferred", "en-US-ChristopherNeural")

    # If topic not provided, research dynamically
    if not topic:
        topics = research_channel_topics(niche, ch_name, count=2)
        topic = topics[0]["topic"]

    # 1. Synthesize Script & SEO
    script_data = synthesize_tier1_script_and_seo(topic, niche, ch_name, duration_min=duration_min)

    # 2. Render Master Video with Outro Lock
    master_path = render_tier1_master_video(script_data, channel_key, voice=voice)

    # 3. Add to Unlisted Queue
    vid_id = f"yt_{int(time.time())}"
    clean_rel = f"/output/{os.path.basename(master_path)}"
    new_entry = {
        "id": vid_id,
        "video_id": "pending_upload",
        "title": script_data.get("title", topic),
        "seo_score": script_data.get("seo_score", 98),
        "channel_id": channel_key,
        "channel_name": ch_name,
        "platform": "youtube",
        "language": "en",
        "local_video_path": clean_rel,
        "master_abs_path": master_path,
        "status": "unlisted_pending_thumbnail",
        "duration_sec": script_data.get("duration_sec", duration_min * 60),
        "duration_formatted": f"{duration_min}:00",
        "thumbnail_punchline": script_data.get("thumbnail_punchline", "THE HIDDEN WAR"),
        "tags": script_data.get("tags", []),
        "description": script_data.get("description", ""),
        "pinned_comment": script_data.get("pinned_comment", ""),
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        q_data = {"videos": []}
        if os.path.exists(QUEUE_FILE):
            q_data = json.load(open(QUEUE_FILE, encoding="utf-8"))
        q_data.setdefault("videos", []).insert(0, new_entry)
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(q_data, f, indent=2)
    except Exception:
        pass

    return {
        "success": True,
        "video_id": vid_id,
        "title": new_entry["title"],
        "master_video_path": master_path,
        "duration_minutes": duration_min,
        "seo_score": script_data.get("seo_score", 98),
        "status": "Ready in Unlisted Queue. You can upload now or attach custom thumbnail."
    }


# --- 3. AUTO-UPLOAD YOUTUBE UNLISTED TOOL ---
def tool_upload_youtube_unlisted(video_id: str, channel_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes zero-touch Playwright upload to YouTube Studio as UNLISTED:
    - Automatically attaches title, description, and tags
    - Pins engagement comment
    - Avoids duplicate upload modal & selector collisions
    """
    from omnichannel_powerhouse.studio_upload_manager import execute_video_upload
    res = execute_video_upload(video_id, channel_key, headless=False)
    return res


# --- 4. AUTO-UPLOAD RUMBLE TOOL ---
def tool_upload_rumble(channel_key: str, video_path: Optional[str] = None) -> Dict[str, Any]:
    """Uploads video to Rumble using persistent profile with selected licensing."""
    from yt_uploader.rumble_uploader import upload_video_to_rumble
    target_vid = video_path
    if not target_vid or not os.path.exists(target_vid):
        # Pick latest master video from output
        out_dir = os.path.join(_root, "output")
        mp4s = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".mp4")]
        if mp4s:
            target_vid = max(mp4s, key=os.path.getmtime)
        else:
            return {"success": False, "error": "No video file available for Rumble upload."}

    seo = {
        "title": "Institutional Documentary | High Finance & Silicon Technology",
        "description": "Exhaustive investigative masterclass into sovereign technology and financial systems.",
        "tags": ["Finance", "Technology", "AI", "Documentary", "Investigative"]
    }
    return upload_video_to_rumble(channel_key=channel_key, video_file_path=target_vid, seo_package=seo, headless=False)


# --- 5. CHANNEL FLEET MANAGEMENT TOOLS ---
def tool_list_channels() -> Dict[str, Any]:
    """Lists all configured YouTube and Rumble channels, their daily quotas, and uploads today."""
    yt = json.load(open(YT_CHANNELS_FILE, encoding="utf-8")) if os.path.exists(YT_CHANNELS_FILE) else {}
    rumble = json.load(open(RUMBLE_CHANNELS_FILE, encoding="utf-8")) if os.path.exists(RUMBLE_CHANNELS_FILE) else {}
    return {
        "youtube_fleet": yt,
        "rumble_fleet": rumble,
        "total_yt_channels": len(yt),
        "total_rumble_channels": len(rumble)
    }


def tool_update_channel_quota(platform: str, channel_key: str, new_daily_quota: int) -> Dict[str, Any]:
    """Updates daily upload quota for a YouTube or Rumble channel."""
    cfg_file = YT_CHANNELS_FILE if platform.lower() == "youtube" else RUMBLE_CHANNELS_FILE
    if not os.path.exists(cfg_file):
        return {"success": False, "error": f"Config file {cfg_file} not found"}

    try:
        data = json.load(open(cfg_file, encoding="utf-8"))
        if channel_key not in data:
            return {"success": False, "error": f"Channel '{channel_key}' not found in {platform} config"}
        data[channel_key]["daily_max_uploads"] = int(new_daily_quota)
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {"success": True, "message": f"Updated {platform} channel '{channel_key}' daily quota to {new_daily_quota} videos/day."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tool_add_channel(
    platform: str,
    channel_key: str,
    name: str,
    niche: str = "technology",
    preferred_voice: str = "en-US-ChristopherNeural",
    daily_quota: int = 5
) -> Dict[str, Any]:
    """Adds a new YouTube or Rumble channel to the fleet configuration."""
    cfg_file = YT_CHANNELS_FILE if platform.lower() == "youtube" else RUMBLE_CHANNELS_FILE
    profiles_base = os.path.join(_root, "yt_uploader", "profiles" if platform.lower() == "youtube" else "profiles_rumble")
    os.makedirs(profiles_base, exist_ok=True)
    prof_dir = os.path.join(profiles_base, channel_key)
    os.makedirs(prof_dir, exist_ok=True)

    data = {}
    if os.path.exists(cfg_file):
        try:
            data = json.load(open(cfg_file, encoding="utf-8"))
        except Exception:
            pass

    data[channel_key] = {
        "name": name,
        "profile_dir": prof_dir,
        "niche": niche,
        "platform": platform.lower(),
        "daily_max_uploads": int(daily_quota),
        "uploads_today": 0,
        "language": "en",
        "voice_preferred": preferred_voice,
        "visibility": "unlisted"
    }

    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {"success": True, "message": f"Successfully enrolled new {platform.upper()} channel '{name}' ({channel_key}) with daily quota {daily_quota}!"}


# --- 6. ELASTIC CLOUD SWARM DISPATCHER TOOL ---
def tool_dispatch_swarm(batch_size: int = 100) -> Dict[str, Any]:
    """
    Dispatches a massive cloud rendering matrix across GitHub Actions:
    - 20 concurrent runners per repo
    - Auto-spawns auxiliary worker repos (auto-video-100x-worker-1, worker-2...) when batch > 20
    - Achieves unlimited parallel threads
    """
    from omnichannel_powerhouse.repo_swarm_dispatcher import dispatch_mega_swarm
    return dispatch_mega_swarm(batch_size=batch_size)


# --- 7. PYTHON CODE INTERPRETER TOOL (SANDBOXED) ---
def tool_run_python(code: str) -> Dict[str, Any]:
    """
    Sandboxed Python Code Interpreter (ChatGPT Pro-Grade Advanced Data Analysis):
    Executes Python script locally, captures stdout/stderr, intercepts Matplotlib charts,
    and returns output + chart URLs.
    """
    try:
        from omnichannel_powerhouse.agent_commander.interpreter import execute_python_code
        return execute_python_code(code)
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- 8. WORKSPACE FILE & GIT TOOLS ---
def tool_read_file(relative_path: str) -> Dict[str, Any]:
    """Reads content of any file inside repository."""
    full_path = os.path.join(_root, relative_path)
    if not os.path.exists(full_path):
        return {"success": False, "error": f"File '{relative_path}' does not exist"}
    try:
        content = open(full_path, "r", encoding="utf-8", errors="replace").read()
        return {"success": True, "path": relative_path, "content": content[:8000], "total_chars": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tool_git_ops(action: str = "status", message: str = "", commit_message: str = "") -> Dict[str, Any]:
    """Executes Git operations ('status', 'commit', 'push')."""
    actual_msg = message or commit_message or "update from AI Commander"
    try:
        if action == "status":
            res = subprocess.run(["git", "status", "-s"], cwd=_root, capture_output=True, text=True)
            return {"success": True, "output": res.stdout}
        elif action == "commit":
            subprocess.run(["git", "add", "."], cwd=_root, check=True)
            res = subprocess.run(["git", "commit", "-m", actual_msg], cwd=_root, capture_output=True, text=True)
            return {"success": True, "output": res.stdout or res.stderr}
        elif action == "push":
            token_path = os.path.join(_root, "yt_uploader", "github_token.local")
            token = open(token_path, encoding="utf-8").read().strip() if os.path.exists(token_path) else ""
            remote = f"https://{token}@github.com/sagaragarwa/auto-video-100x.git" if token else "origin"
            res = subprocess.run(["git", "push", remote, "main"], cwd=_root, capture_output=True, text=True)
            return {"success": res.returncode == 0, "output": res.stdout or res.stderr}
        return {"success": False, "error": f"Unknown git action '{action}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tool_list_unlisted_queue() -> Dict[str, Any]:
    """Lists all videos in the Unlisted Queue waiting for thumbnail review or scheduled upload."""
    if not os.path.exists(QUEUE_FILE):
        return {"total_count": 0, "videos": []}
    try:
        q_data = json.load(open(QUEUE_FILE, encoding="utf-8"))
        vids = q_data.get("videos", [])
        summary_vids = []
        for v in vids:
            summary_vids.append({
                "id": v.get("id"),
                "title": v.get("title"),
                "channel": v.get("channel_name") or v.get("channel_id"),
                "platform": v.get("platform", "youtube"),
                "status": v.get("status"),
                "video_id": v.get("video_id"),
                "video_url": v.get("video_url"),
                "duration": v.get("duration_formatted"),
                "seo_score": v.get("seo_score", 98)
            })
        return {
            "total_count": len(vids),
            "updated_at": q_data.get("updated_at"),
            "videos": summary_vids
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- 9. GEMINI KEY POOL TOOLS ---
def tool_add_gemini_key(api_key: str, label: str = "") -> Dict[str, Any]:
    """Enrolls a new Google Gemini API key into the key pool with live health validation."""
    from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
    return KEY_POOL.add_key(api_key, label=label)


def tool_get_system_health() -> Dict[str, Any]:
    """Returns real-time system health: disk space, key pool capacity, active daemon status, queue count."""
    from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
    from omnichannel_powerhouse.perpetual_genius_daemon import get_daemon

    disk = shutil.disk_usage(_root)
    daemon = get_daemon()
    key_telem = KEY_POOL.get_telemetry()

    queue_count = 0
    if os.path.exists(QUEUE_FILE):
        try:
            q = json.load(open(QUEUE_FILE, encoding="utf-8"))
            queue_count = len(q.get("videos", []))
        except Exception:
            pass

    return {
        "daemon_status": daemon.get_status().get("state", {}).get("current_status", "Unknown"),
        "key_pool": {
            "total_keys": key_telem["total_keys"],
            "daily_capacity": key_telem["max_daily_capacity"],
            "remaining_calls_today": key_telem["available_calls_remaining"],
            "healthy_keys": key_telem["healthy_keys"]
        },
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "unlisted_queue_pending": queue_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# Tool Dispatch Table for Function Calling
TOOL_REGISTRY = {
    "tool_daemon_control": tool_daemon_control,
    "tool_manufacture_video": tool_manufacture_video,
    "tool_upload_youtube_unlisted": tool_upload_youtube_unlisted,
    "tool_upload_rumble": tool_upload_rumble,
    "tool_list_channels": tool_list_channels,
    "tool_list_unlisted_queue": tool_list_unlisted_queue,
    "tool_update_channel_quota": tool_update_channel_quota,
    "tool_add_channel": tool_add_channel,
    "tool_dispatch_swarm": tool_dispatch_swarm,
    "tool_run_python": tool_run_python,
    "tool_read_file": tool_read_file,
    "tool_git_ops": tool_git_ops,
    "tool_add_gemini_key": tool_add_gemini_key,
    "tool_get_system_health": tool_get_system_health
}


GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "tool_list_unlisted_queue",
        "description": "List all manufactured videos in the Unlisted Queue waiting for thumbnail review, upload, or publish.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "tool_daemon_control",
        "description": "Start, stop, pause, or get status of the 24/7 perpetual autonomous video manufacturing engine.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "'status', 'start', or 'stop'"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "tool_manufacture_video",
        "description": "Generate and render a complete 30-60 min Tier-1 English institutional documentary with Shure SM7B DSP voice and Content ID outro lock.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "channel_key": {"type": "STRING", "description": "Channel key (e.g. 'channel_trading', 'ai_and_tech')"},
                "topic": {"type": "STRING", "description": "Specific documentary topic (optional, bot will research if omitted)"},
                "duration_min": {"type": "INTEGER", "description": "Target duration in minutes (e.g. 40 or 45)"}
            },
            "required": ["channel_key"]
        }
    },
    {
        "name": "tool_upload_youtube_unlisted",
        "description": "Auto-upload a manufactured video from the queue to YouTube Studio as Unlisted via Playwright persistent Chrome profile.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "video_id": {"type": "STRING", "description": "ID of video in queue (e.g. 'yt_1792673800' or 'unlisted_001')"},
                "channel_key": {"type": "STRING", "description": "Optional channel key"}
            },
            "required": ["video_id"]
        }
    },
    {
        "name": "tool_upload_rumble",
        "description": "Upload a video to Rumble with automated licensing and metadata.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "channel_key": {"type": "STRING", "description": "Rumble channel key (e.g. 'rumble_trading')"},
                "video_path": {"type": "STRING", "description": "Path to video file"}
            },
            "required": ["channel_key"]
        }
    },
    {
        "name": "tool_list_channels",
        "description": "List all configured YouTube and Rumble channels, their niches, and daily quotas.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "tool_update_channel_quota",
        "description": "Update the daily upload quota for a YouTube or Rumble channel.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "platform": {"type": "STRING", "description": "'youtube' or 'rumble'"},
                "channel_key": {"type": "STRING", "description": "Channel identifier"},
                "new_daily_quota": {"type": "INTEGER", "description": "New daily video target count"}
            },
            "required": ["platform", "channel_key", "new_daily_quota"]
        }
    },
    {
        "name": "tool_add_channel",
        "description": "Enroll a brand-new YouTube or Rumble channel into the autonomous fleet.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "platform": {"type": "STRING", "description": "'youtube' or 'rumble'"},
                "channel_key": {"type": "STRING", "description": "Unique key (e.g. 'channel_crypto')"},
                "name": {"type": "STRING", "description": "Display name of the channel"},
                "niche": {"type": "STRING", "description": "Channel niche (e.g. 'trading', 'technology')"},
                "preferred_voice": {"type": "STRING", "description": "Edge-TTS voice (e.g. 'en-US-ChristopherNeural')"},
                "daily_quota": {"type": "INTEGER", "description": "Daily upload limit"}
            },
            "required": ["platform", "channel_key", "name"]
        }
    },
    {
        "name": "tool_dispatch_swarm",
        "description": "Dispatch a massive parallel video rendering swarm (100 to 1,000+ videos) across GitHub Actions runners.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "batch_size": {"type": "INTEGER", "description": "Total videos (e.g. 100, 500, 1000)"}
            },
            "required": ["batch_size"]
        }
    },
    {
        "name": "tool_run_python",
        "description": "Execute sandboxed Python code locally (Code Interpreter) to calculate math, analyze data, or run utilities.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "code": {"type": "STRING", "description": "Complete Python script to execute"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "tool_read_file",
        "description": "Read file contents from the codebase.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "relative_path": {"type": "STRING", "description": "Relative path to file"}
            },
            "required": ["relative_path"]
        }
    },
    {
        "name": "tool_git_ops",
        "description": "Check git status, make a commit, or push changes to GitHub.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "'status', 'commit', or 'push'"},
                "message": {"type": "STRING", "description": "Commit message if committing"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "tool_add_gemini_key",
        "description": "Add a new Google Gemini API key to the active key pool.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "api_key": {"type": "STRING", "description": "The AIzaSy... API key"},
                "label": {"type": "STRING", "description": "Optional label"}
            },
            "required": ["api_key"]
        }
    },
    {
        "name": "tool_get_system_health",
        "description": "Get real-time telemetry: disk space, key pool status, queue count, and daemon status.",
        "parameters": {"type": "OBJECT", "properties": {}}
    }
]
