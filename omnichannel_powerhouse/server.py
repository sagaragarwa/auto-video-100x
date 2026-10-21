"""
OmniChannel Powerhouse Control Server
FastAPI backend powering the Professional Desktop Dashboard and the Android Companion App.
Manages channels, safe manual logins, quota tracking, cloud runner radar, and the Universal Conversation ID Bridge.
"""

import os
import sys
import json
import time
import threading
import subprocess
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from omnichannel_powerhouse.smart_niche_router import load_registry, save_registry, route_video_to_channels
from omnichannel_powerhouse.quota_balancer import check_and_allocate_upload_slot
from omnichannel_powerhouse.manual_auth_helper import launch_manual_login_session
from omnichannel_powerhouse.cloud_matrix_dispatcher import generate_structured_20_blueprint, dispatch_to_github_cloud_matrix
from omnichannel_powerhouse.gemini_script_engine import generate_documentary_package, create_dynamic_20_series_with_gemini, get_gemini_api_key
from omnichannel_powerhouse.gemini_key_rotator import KEY_RING
from omnichannel_powerhouse.swarm_fleet_manager import generate_fleet_matrix, get_swarm_summary, NICHE_CLUSTERS
from omnichannel_powerhouse.repo_swarm_dispatcher import dispatch_mega_swarm, generate_mega_swarm_manifest, SWARM_MANIFEST_PATH

app = FastAPI(title="OmniChannel Supreme Studio", version="1.0.0")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

CONVO_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "convo_state.json")
DEFAULT_CONVO_ID = "6a60d582-ca94-43f1-bef4-cbc8f38f0265"


def get_active_convo_id() -> str:
    if os.path.exists(CONVO_CONFIG_PATH):
        try:
            with open(CONVO_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("conversation_id", DEFAULT_CONVO_ID)
        except Exception:
            pass
    return DEFAULT_CONVO_ID


def set_active_convo_id(convo_id: str):
    with open(CONVO_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"conversation_id": convo_id, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)


# --- Request Models ---
class AddChannelRequest(BaseModel):
    channel_key: str
    platform: str
    name: str
    niche: str
    keywords: List[str]
    negative_keywords: Optional[List[str]] = []
    daily_max_uploads: Optional[int] = 3


class ManualLoginRequest(BaseModel):
    channel_key: str
    platform: str = "youtube"


class DeleteChannelRequest(BaseModel):
    channel_key: str
    delete_profile_folder: Optional[bool] = False


class DispatchRequest(BaseModel):
    theme: Optional[str] = "Frontier AI Hardware & Wall Street Quantitative Warfare"
    custom_topics: Optional[List[Dict[str, Any]]] = None


class ConvoUpdateRequest(BaseModel):
    conversation_id: str


class GeminiScriptRequest(BaseModel):
    topic: str
    niche: Optional[str] = "tech"
    words: Optional[int] = 2000


class GeminiSeriesRequest(BaseModel):
    master_theme: Optional[str] = "Frontier AI Hardware & Wall Street Quantitative Warfare"


class SwarmDispatchRequest(BaseModel):
    batch_size: int = 100


class AddKeyRequest(BaseModel):
    api_key: str
    label: Optional[str] = ""


class FleetPartitionRequest(BaseModel):
    total_channels: int = 1000


# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return "<h1>OmniChannel Studio is Initializing...</h1>"


@app.get("/api/status")
def get_system_status():
    reg = load_registry()
    channels = reg.get("channels", {})
    token_path = os.path.join(_root, "yt_uploader", "github_token.local")
    outro_path = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
    
    return {
        "status": "online",
        "total_channels": len(channels),
        "active_youtube_channels": sum(1 for c in channels.values() if c.get("platform") == "youtube" and c.get("auth_status") == "authenticated"),
        "active_rumble_channels": sum(1 for c in channels.values() if c.get("platform") == "rumble"),
        "outro_hard_lock": os.path.exists(outro_path) or os.path.exists(r"C:\Users\janar\Downloads\content_id_outro.mp4"),
        "token_reduction_rate": "500x",
        "conversation_id": get_active_convo_id(),
        "cloud_sync_ready": os.path.exists(token_path)
    }


@app.get("/api/channels")
def list_channels():
    reg = load_registry()
    channels = reg.get("channels", {})
    # Enrich with quota info
    enriched = []
    for k, v in channels.items():
        slot = check_and_allocate_upload_slot(k)
        item = v.copy()
        item["quota_status"] = slot
        enriched.append(item)
    return {"channels": enriched}


@app.post("/api/channels/add")
def add_channel(req: AddChannelRequest):
    reg = load_registry()
    channels = reg.setdefault("channels", {})
    clean_key = req.channel_key.strip().lower().replace(" ", "_")
    profile_dir = f"yt_uploader/profiles/{clean_key}"

    channels[clean_key] = {
        "channel_id": clean_key,
        "platform": req.platform.lower(),
        "name": req.name.strip(),
        "niche": req.niche.strip(),
        "keywords": req.keywords,
        "negative_keywords": req.negative_keywords or [],
        "profile_dir": profile_dir,
        "auth_status": "unverified",
        "daily_max_uploads": req.daily_max_uploads or (3 if req.platform == "youtube" else 20),
        "uploads_today": 0,
        "last_upload_timestamp": ""
    }
    save_registry(reg)
    return {"success": True, "channel_key": clean_key, "message": "Channel added. Please initiate manual login."}


@app.post("/api/channels/delete")
def delete_channel(req: DeleteChannelRequest):
    reg = load_registry()
    channels = reg.get("channels", {})
    key = req.channel_key.strip()
    if key in channels:
        ch_info = channels.pop(key)
        save_registry(reg)

        if req.delete_profile_folder:
            p_dir = ch_info.get("profile_dir")
            if p_dir:
                abs_p = os.path.join(_root, p_dir)
                if os.path.exists(abs_p):
                    import shutil
                    try:
                        shutil.rmtree(abs_p, ignore_errors=True)
                    except Exception:
                        pass
        return {"success": True, "message": f"Channel '{key}' removed successfully."}
    return {"success": False, "message": f"Channel '{key}' not found."}


@app.post("/api/channels/manual-login")
def trigger_manual_login(req: ManualLoginRequest):
    py_exe = sys.executable
    candidate_311 = os.path.expanduser(r"~\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe")
    if os.path.exists(candidate_311):
        py_exe = candidate_311

    script_path = os.path.join(_root, "omnichannel_powerhouse", "manual_auth_helper.py")
    cmd = [py_exe, script_path, "--channel", req.channel_key, "--platform", req.platform]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{_root};{os.path.join(_root, '.venv', 'Lib', 'site-packages')};{env.get('PYTHONPATH', '')}"
    
    # Launch with a visible interactive helper console on Windows
    create_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    subprocess.Popen(cmd, cwd=_root, env=env, creationflags=create_flags)
    return {"success": True, "message": f"Visible genuine Chrome launched for '{req.channel_key}'. Complete login in the opened window."}


@app.post("/api/dispatch")
def trigger_cloud_dispatch(req: DispatchRequest):
    manifest = generate_structured_20_blueprint(master_theme=req.theme, custom_topics=req.custom_topics)
    res = dispatch_to_github_cloud_matrix()
    return {
        "success": res.get("success", False),
        "manifest_title": manifest.get("series_title"),
        "total_episodes": manifest.get("total_episodes"),
        "message": res.get("message") or res.get("error")
    }


@app.get("/api/cloud-runs")
def get_cloud_runs():
    token_path = os.path.join(_root, "yt_uploader", "github_token.local")
    if not os.path.exists(token_path):
        return {"runs": [], "error": "No GitHub token found"}

    try:
        import requests
        tok = open(token_path, "r", encoding="utf-8").read().strip()
        h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
        r = requests.get("https://api.github.com/repos/sagaragarwa/auto-video-100x/actions/runs?per_page=5", headers=h, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"runs": data.get("workflow_runs", [])}
        return {"runs": [], "status_code": r.status_code}
    except Exception as e:
        return {"runs": [], "error": str(e)}


@app.get("/api/conversation")
def get_conversation():
    convo_id = get_active_convo_id()
    brain_dir = os.path.join(r"C:\Users\janar\.gemini\antigravity\brain", convo_id)
    return {
        "conversation_id": convo_id,
        "is_active_on_disk": os.path.exists(brain_dir),
        "brain_path": brain_dir
    }


@app.post("/api/conversation")
def update_conversation(req: ConvoUpdateRequest):
    clean_id = req.conversation_id.strip()
    if clean_id:
        set_active_convo_id(clean_id)
        return {"success": True, "conversation_id": clean_id}
    raise HTTPException(status_code=400, detail="Invalid Conversation ID")


@app.get("/api/gemini/status")
def gemini_status():
    key = get_gemini_api_key()
    return {
        "configured": bool(key),
        "key_masked": f"{key[:6]}...{key[-4:]}" if key else "",
        "model": "gemini-flash-latest",
        "free_tier_limits": "1,500 RPD (Requests Per Day) / 15 RPM"
    }


@app.post("/api/gemini/generate-script")
def gemini_generate_script(req: GeminiScriptRequest):
    try:
        pkg = generate_documentary_package(topic=req.topic, niche=req.niche, target_words=req.words)
        return {"success": True, "package": pkg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gemini/create-series")
def gemini_create_series(req: GeminiSeriesRequest, background_tasks: BackgroundTasks):
    # Run in background so request doesn't timeout
    background_tasks.add_task(create_dynamic_20_series_with_gemini, req.master_theme)
    return {
        "success": True,
        "message": f"Gemini 20-episode generation initiated in background for theme: '{req.master_theme}'. Will update series_tasks.json autonomously."
    }


@app.get("/api/swarm/status")
def swarm_status():
    fleet = get_swarm_summary()
    keys_status = KEY_RING.get_status()
    manifest_exists = os.path.exists(SWARM_MANIFEST_PATH)
    last_batch = {}
    if manifest_exists:
        try:
            with open(SWARM_MANIFEST_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
                last_batch = {
                    "total_videos": d.get("total_videos", 0),
                    "created_at": d.get("created_at"),
                    "shards": d.get("total_shards_of_20", 0)
                }
        except Exception:
            pass

    return {
        "fleet": fleet,
        "key_ring": keys_status,
        "clusters": NICHE_CLUSTERS,
        "last_batch": last_batch,
        "available_options": [
            {"size": 100, "label": "100 Videos Batch (Daily Fleet Blitz)", "shards": 5},
            {"size": 500, "label": "500 Videos Batch (Weekly Multi-Niche Campaign)", "shards": 25},
            {"size": 1000, "label": "1,000 Videos Batch (Monthly Dominance Matrix)", "shards": 50},
            {"size": 10000, "label": "10,000 Videos Mega Swarm (Multi-Repo Farm)", "shards": 500}
        ]
    }


@app.post("/api/swarm/dispatch")
def swarm_dispatch(req: SwarmDispatchRequest):
    target_size = req.batch_size
    if target_size not in [100, 500, 1000, 10000]:
        target_size = max(20, min(10000, target_size))
    res = dispatch_mega_swarm(batch_size=target_size)
    return res


@app.post("/api/swarm/keys/add")
def swarm_add_key(req: AddKeyRequest):
    success = KEY_RING.add_key(req.api_key, label=req.label)
    return {"success": success, "status": KEY_RING.get_status()}


@app.get("/api/swarm/keys")
def swarm_get_keys():
    return KEY_RING.get_status()


@app.post("/api/swarm/fleet/partition")
def swarm_partition_fleet(req: FleetPartitionRequest):
    res = generate_fleet_matrix(total_channels=max(10, min(10000, req.total_channels)))
    return {"success": True, "fleet_size": res["fleet_size"], "clusters": len(res.get("clusters", []))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("omnichannel_powerhouse.server:app", host="0.0.0.0", port=8899, reload=False)
