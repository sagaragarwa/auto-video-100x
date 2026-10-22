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
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
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

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

CONVO_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "convo_state.json")
DEFAULT_CONVO_ID = "6a60d582-ca94-43f1-bef4-cbc8f38f0265"


@app.get("/player", response_class=HTMLResponse)
def serve_player():
    convo_id = get_active_convo_id()
    brain_player = os.path.join(r"C:\Users\janar\.gemini\antigravity\brain", convo_id, "player_demo.html")
    if os.path.exists(brain_player):
        with open(brain_player, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Player not found</h1>"


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


class EditChannelRequest(BaseModel):
    channel_key: str
    name: Optional[str] = None
    niche: Optional[str] = None
    keywords: Optional[List[str]] = None
    negative_keywords: Optional[List[str]] = None
    daily_max_uploads: Optional[int] = None
    voice_preferred: Optional[str] = None
    handle: Optional[str] = None


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


class VoicePreviewRequest(BaseModel):
    text: str
    voice_name: Optional[str] = "Fenrir"
    apply_dsp: Optional[bool] = True
    mix_bg_score: Optional[bool] = False


class UnlistedStatusUpdateRequest(BaseModel):
    video_id: str
    status: str  # "thumbnail_attached" or "published_public"


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


@app.post("/api/channels/edit")
def edit_channel(req: EditChannelRequest):
    reg = load_registry()
    channels = reg.setdefault("channels", {})
    key = req.channel_key.strip()
    if key not in channels:
        raise HTTPException(status_code=404, detail=f"Channel '{key}' not found.")

    ch = channels[key]
    if req.name is not None:
        ch["name"] = req.name.strip()
    if req.niche is not None:
        ch["niche"] = req.niche.strip()
    if req.keywords is not None:
        ch["keywords"] = req.keywords
    if req.negative_keywords is not None:
        ch["negative_keywords"] = req.negative_keywords
    if req.daily_max_uploads is not None:
        ch["daily_max_uploads"] = max(1, req.daily_max_uploads)
    if req.voice_preferred is not None:
        ch["voice_preferred"] = req.voice_preferred.strip()
    if req.handle is not None:
        ch["handle"] = req.handle.strip()

    save_registry(reg)
    return {"success": True, "channel": ch, "message": f"Channel '{key}' updated successfully."}


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
    tok = open(token_path, "r", encoding="utf-8").read().strip() if os.path.exists(token_path) else ""

    h = {"Accept": "application/vnd.github+json", "User-Agent": "OmniChannel"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"

    try:
        import requests
        r = requests.get("https://api.github.com/repos/sagaragarwa/auto-video-100x/actions/runs?per_page=5", headers=h, timeout=10)
        runs = []
        artifacts = []
        if r.status_code == 200:
            runs = r.json().get("workflow_runs", [])
            # Find latest completed 20-matrix run to show downloadable artifacts
            target_run = next((run for run in runs if "20" in run.get("name", "") and run.get("conclusion") == "success"), None)
            if not target_run and runs:
                target_run = runs[0]
            if target_run:
                run_id = target_run.get("id")
                art_r = requests.get(f"https://api.github.com/repos/sagaragarwa/auto-video-100x/actions/runs/{run_id}/artifacts", headers=h, timeout=10)
                if art_r.status_code == 200:
                    artifacts = art_r.json().get("artifacts", [])
            return {"runs": runs, "artifacts": artifacts, "target_run": target_run}
        return {"runs": [], "artifacts": [], "status_code": r.status_code}
    except Exception as e:
        return {"runs": [], "artifacts": [], "error": str(e)}


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


@app.get("/api/voice/info")
def voice_info():
    return {
        "status": "HARD_LOCKED",
        "engine": "Microsoft Edge-TTS 48kHz Broadcast Engine (Zero Gemini Quota)",
        "models": {
            "hindi_male": "hi-IN-MadhurNeural (Documentary & Tech Gravitas)",
            "hindi_female": "hi-IN-SwaraNeural (Explainer & Educational)",
            "english_male": "en-US-ChristopherNeural (International Deep Dive)",
            "english_female": "en-US-AriaNeural (Broadcaster)"
        },
        "quota_impact": "0% Gemini Quota Consumed (100% of 4,500 daily requests reserved for Gemini Scripts)",
        "cost": "₹0.00 Lifetime Unlimited (No Cards, No Bills)",
        "sample_rate": "48kHz Broadcast Mastered MP3",
        "vocal_dsp_chain": [
            "1. 75Hz Highpass Filter (Room Rumble & Mic Boom Attenuation)",
            "2. 250Hz Chest Warmth EQ (+2.0dB Resonance)",
            "3. 3,500Hz Consonant Presence & Air EQ (+3.5dB Discovery Channel Clarity)",
            "4. Precision De-Esser (5kHz-6.5kHz Sibilance Suppression)",
            "5. Multiband Broadcast Compression (-18dB / 3.5:1 Ratio / 15ms Attack / 120ms Release)",
            "6. EBU R128 Loudness Normalization (-14 LUFS, -1.5 dBTP, YouTube & Rumble Certified)"
        ],
        "sidechain_ducking": "Dynamic -24dB Music Attenuation with +4dB Micro-Pause Swells",
        "phonetic_engine": "Devanagari Acronym Transliteration (TSMC, ASML, EUV, Blackwell, etc.)"
    }


@app.post("/api/voice/synthesize")
def voice_synthesize(req: VoicePreviewRequest):
    try:
        from omnichannel_powerhouse.gemini_tts_engine import synthesize_master_voice, mix_voice_with_dynamic_ducked_score
        out_name = f"voice_preview_{int(time.time())}.mp3"
        out_file = os.path.join(OUTPUT_DIR, out_name)
        synthesize_master_voice(req.text, out_file, voice_name=req.voice_name, apply_dsp=req.apply_dsp)

        ducked_url = None
        if req.mix_bg_score:
            bg_music = os.path.join(_root, "temp_demo_hindi", "scoring_15min.mp3")
            if os.path.exists(bg_music):
                ducked_name = f"voice_preview_{int(time.time())}_ducked.mp3"
                ducked_file = os.path.join(OUTPUT_DIR, ducked_name)
                mix_voice_with_dynamic_ducked_score(out_file, bg_music, ducked_file)
                ducked_url = f"/output/{ducked_name}"

        return {
            "success": True,
            "audio_url": f"/output/{out_name}",
            "ducked_audio_url": ducked_url,
            "voice": req.voice_name,
            "dsp_applied": req.apply_dsp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


UNLISTED_QUEUE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unlisted_queue.json")


@app.get("/api/unlisted-videos")
def get_unlisted_videos():
    if os.path.exists(UNLISTED_QUEUE_PATH):
        try:
            with open(UNLISTED_QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"videos": [], "error": str(e)}
    return {"videos": []}


class AutoUploadRequest(BaseModel):
    video_id: str
    channel_key: Optional[str] = None


@app.post("/api/unlisted-videos/update-status")
def update_unlisted_video_status(req: UnlistedStatusUpdateRequest):
    if not os.path.exists(UNLISTED_QUEUE_PATH):
        raise HTTPException(status_code=404, detail="Queue file not found")
    try:
        with open(UNLISTED_QUEUE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        found = False
        for v in data.get("videos", []):
            if v.get("id") == req.video_id or v.get("video_id") == req.video_id:
                v["status"] = req.status
                v["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                found = True
                break
        if not found:
            raise HTTPException(status_code=404, detail="Video not found in queue")
        with open(UNLISTED_QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {"success": True, "video_id": req.video_id, "new_status": req.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/unlisted-videos/auto-upload-now")
def trigger_auto_upload_now(req: AutoUploadRequest):
    try:
        from omnichannel_powerhouse.studio_upload_manager import launch_upload_in_background
        launch_upload_in_background(req.video_id, req.channel_key)
        return {"success": True, "message": f"Autonomous Playwright upload launched for {req.video_id}!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/daemon/status")
def get_daemon_telemetry():
    from omnichannel_powerhouse.perpetual_genius_daemon import get_daemon
    daemon = get_daemon()
    return daemon.get_status()


@app.post("/api/daemon/start")
def start_perpetual_daemon():
    from omnichannel_powerhouse.perpetual_genius_daemon import get_daemon
    daemon = get_daemon()
    return daemon.start()


@app.post("/api/daemon/stop")
def stop_perpetual_daemon():
    from omnichannel_powerhouse.perpetual_genius_daemon import get_daemon
    daemon = get_daemon()
    return daemon.stop()


# ==============================================================================
# CHATGPT PRO-GRADE AGENT COMMANDER ENDPOINTS
# ==============================================================================

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    model: Optional[str] = "gemini-3.5-flash"
    enable_tools: Optional[bool] = True


class ChatAddKeyRequest(BaseModel):
    api_key: str
    label: Optional[str] = ""


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Conversation"


@app.get("/chat", response_class=HTMLResponse)
def serve_chat_spa():
    chat_html = os.path.join(STATIC_DIR, "chat.html")
    if os.path.exists(chat_html):
        return HTMLResponse(content=open(chat_html, encoding="utf-8").read())
    return HTMLResponse(content="<h1>Chat SPA loading...</h1>")


@app.post("/api/chat/message")
def chat_stream_endpoint(req: ChatMessageRequest):
    from omnichannel_powerhouse.agent_commander.gemini_agent import stream_chat_response
    return StreamingResponse(
        stream_chat_response(
            session_id=req.session_id or "",
            user_prompt=req.message,
            model_name=req.model or "gemini-3.5-flash",
            enable_tools=req.enable_tools if req.enable_tools is not None else True
        ),
        media_type="text/event-stream"
    )


@app.get("/api/chat/sessions")
def get_chat_sessions():
    from omnichannel_powerhouse.agent_commander.memory import list_sessions
    return {"sessions": list_sessions()}


@app.get("/api/chat/sessions/{session_id}")
def get_chat_history(session_id: str):
    from omnichannel_powerhouse.agent_commander.memory import get_session_messages
    return {"session_id": session_id, "messages": get_session_messages(session_id)}


@app.post("/api/chat/sessions/new")
def new_chat_session(req: CreateSessionRequest):
    from omnichannel_powerhouse.agent_commander.memory import create_session
    s_id = create_session(title=req.title or "New Conversation")
    return {"session_id": s_id}


@app.get("/api/chat/keys")
def get_chat_keys_status():
    from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
    return KEY_POOL.get_telemetry()


@app.post("/api/chat/keys/add")
def add_chat_key(req: ChatAddKeyRequest):
    from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
    return KEY_POOL.add_key(req.api_key, label=req.label)


@app.post("/api/chat/code-interpreter")
def run_code_interpreter(req: Dict[str, Any]):
    from omnichannel_powerhouse.agent_commander.tools import tool_run_python
    code = req.get("code", "")
    return tool_run_python(code)


class VisionRequest(BaseModel):
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    prompt: Optional[str] = None
    model: Optional[str] = "gemini-3.5-flash"


@app.post("/api/chat/vision")
def run_vision_analysis(req: VisionRequest):
    from omnichannel_powerhouse.agent_commander.gemini_agent import analyze_visual_media
    return analyze_visual_media(
        image_base64=req.image_base64,
        image_path=req.image_path,
        prompt=req.prompt,
        model_name=req.model or "gemini-3.5-flash"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("omnichannel_powerhouse.server:app", host="0.0.0.0", port=8899, reload=False)
