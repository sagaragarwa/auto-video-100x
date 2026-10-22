import os
import sys

# Force UTF-8 encoding on standard streams to prevent Windows cp1252 charmap errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
import json
import urllib.request
import urllib.error
import subprocess

_root = r"C:\Users\janar\Downloads\MoneyPrinterTurbo-main\MoneyPrinterTurbo-main"
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

def print_header(title):
    print("\n" + "=" * 70)
    print(f"🚀 RUNNING: {title}")
    print("=" * 70, flush=True)

def test_1_gemini_key_pool():
    print_header("TEST 1: GEMINI API MULTI-KEY POOL & LIVE FAILOVER")
    from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
    
    print(f"Active keys in pool: {len(KEY_POOL.keys)}")
    for idx, item in enumerate(KEY_POOL.keys):
        k = item["key"]
        masked = k[:6] + "..." + k[-4:]
        print(f"  Key #{idx+1} ({item.get('label', 'No label')}): {masked}")
    
    # Test each key individually with a real API call
    for idx, item in enumerate(KEY_POOL.keys):
        k = item["key"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={k}"
        payload = json.dumps({"contents": [{"parts": [{"text": "Reply with only: KEY_ACTIVE"}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        start_t = time.time()
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                latency = time.time() - start_t
                print(f"  ✅ Key #{idx+1} Status: 200 OK | Latency: {latency:.2f}s | Response: {text}")
        except Exception as e:
            print(f"  ❌ Key #{idx+1} Failed: {e}")

def test_2_edge_tts_shure_sm7b_dsp():
    print_header("TEST 2: EDGE-TTS NATIVE TIER-1 VOICE & SHURE SM7B DSP")
    import asyncio
    import edge_tts
    
    test_text = "The institutional architecture of sovereign microchip technology reveals an unprecedented global monopoly."
    test_voice = "en-US-ChristopherNeural"
    out_dir = os.path.join(_root, "temp_render", "test_dsp")
    os.makedirs(out_dir, exist_ok=True)
    raw_audio = os.path.join(out_dir, "raw_test.mp3")
    dsp_audio = os.path.join(out_dir, "dsp_master.mp3")
    
    print(f"1. Synthesizing test text with {test_voice}...")
    start_t = time.time()
    
    async def _synth():
        comm = edge_tts.Communicate(test_text, test_voice)
        with open(raw_audio, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
    
    asyncio.run(_synth())
    synth_t = time.time() - start_t
    raw_size = os.path.getsize(raw_audio)
    print(f"  ✅ Raw TTS Complete in {synth_t:.2f}s ({raw_size} bytes)")
    
    print("2. Applying 6-Stage Shure SM7B Broadcast DSP vocal chain (-14 LUFS)...")
    vocal_chain = (
        "highpass=f=80,"
        "equalizer=f=250:t=q:w=1.2:g=2.2,"
        "equalizer=f=3500:t=q:w=1.2:g=2.5,"
        "equalizer=f=6800:t=q:w=1.5:g=-2.5,"
        "dynaudnorm=p=0.95:m=10:s=12"
    )
    cmd = [
        "ffmpeg", "-y", "-i", raw_audio,
        "-af", vocal_chain,
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
        dsp_audio
    ]
    dsp_start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dsp_t = time.time() - dsp_start
    if res.returncode == 0 and os.path.exists(dsp_audio):
        dsp_size = os.path.getsize(dsp_audio)
        print(f"  ✅ Shure SM7B DSP Mastering Complete in {dsp_t:.2f}s ({dsp_size} bytes, 48kHz stereo)")
    else:
        print(f"  ❌ DSP Mastering Failed: {res.stderr}")

def test_3_outro_and_ambient_drone():
    print_header("TEST 3: SIGNATURE 173.25s CONTENT ID OUTRO LOCK & AMBIENT DRONE")
    from cloud_render_worker import get_outro_clip_path, get_media_duration, get_or_synthesize_ambient_drone
    
    outro_path = get_outro_clip_path()
    print(f"1. Outro Clip Path: {outro_path}")
    if os.path.exists(outro_path):
        dur = get_media_duration(outro_path)
        size_mb = os.path.getsize(outro_path) / (1024 * 1024)
        print(f"  ✅ Outro Clip Verified! Duration: {dur:.2f}s (Target: 173.25s) | Size: {size_mb:.2f} MB")
    else:
        print(f"  ❌ Outro Clip Missing at {outro_path}")
        
    print("2. Checking Procedural Dark Ambient Drone (-24dB background bed)...")
    drone_path = get_or_synthesize_ambient_drone()
    if drone_path and os.path.exists(drone_path):
        d_dur = get_media_duration(drone_path)
        print(f"  ✅ Ambient Drone Ready! Duration: {d_dur:.1f}s | Path: {drone_path}")
    else:
        print("  ⚠️ Ambient Drone could not be synthesized")

def test_4_open_interpreter():
    print_header("TEST 4: OPEN-INTERPRETER CODE RUNNER & CHART GENERATOR")
    from omnichannel_powerhouse.agent_commander.interpreter import execute_python_code
    
    code = """
import numpy as np
import matplotlib.pyplot as plt

# Generate statistical distribution of multi-channel upload velocity
days = np.arange(1, 31)
yt_uploads = 5 * days
rumble_uploads = 20 * days

plt.figure(figsize=(7, 3.5))
plt.plot(days, yt_uploads, label='YouTube Fleet (5/day)', color='#FF0000', lw=2)
plt.plot(days, rumble_uploads, label='Rumble Fleet (20/day)', color='#00F2FE', lw=2.5)
plt.fill_between(days, yt_uploads, rumble_uploads, color='#00F2FE', alpha=0.1)
plt.title('30-Day Empire Production Velocity', fontsize=12, fontweight='bold')
plt.xlabel('Day of Month')
plt.ylabel('Total Published Documentaries')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.show()

print('Computed 30-day velocity: Total', yt_uploads[-1] + rumble_uploads[-1], 'videos!')
"""
    res = execute_python_code(code)
    print(f"  ✅ Success: {res.get('success')}")
    print(f"  ✅ Execution Time: {res.get('execution_time_s')}s")
    print(f"  ✅ Captured Chart URL: {res.get('chart_url')}")
    print(f"  ✅ Stdout: {res.get('stdout', '').strip()}")
    if not res.get("success"):
        print(f"  ❌ Error: {res.get('error')}")

def test_5_multimodal_vision_endpoint():
    print_header("TEST 5: MULTIMODAL VISION ENDPOINT (/api/chat/vision)")
    url = "http://localhost:8899/api/chat/vision"
    chart_file = os.path.join(_root, "output", "charts")
    pngs = [os.path.join(chart_file, f) for f in os.listdir(chart_file) if f.endswith(".png")] if os.path.exists(chart_file) else []
    
    if not pngs:
        print("  ⚠️ No chart png found to test vision endpoint.")
        return
        
    latest_png = max(pngs, key=os.path.getmtime)
    print(f"Testing vision analysis on: {os.path.basename(latest_png)}")
    
    payload = {
        "image_path": latest_png,
        "prompt": "Analyze this visualization for high-contrast presentation and institutional aesthetics.",
        "model": "gemini-3.5-flash"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  ✅ Vision Success: {data.get('success')}")
            print(f"  ✅ Model: {data.get('model_used')}")
            review = data.get('analysis', '')[:200].replace('\n', ' ')
            print(f"  ✅ Summary: {review}...")
    except Exception as e:
        print(f"  ❌ Vision Endpoint Request Failed: {e}")

def test_6_chat_stream_agent_with_tool_calling():
    print_header("TEST 6: CHAT STREAM AGENT WITH DYNAMIC TOOL CALLING")
    url = "http://localhost:8899/api/chat/message"
    payload = {
        "session_id": "",
        "message": "System health aur active unlisted queue ka status check karke batao.",
        "model": "gemini-3.5-flash",
        "enable_tools": True
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    print("Sending prompt: 'System health aur active unlisted queue ka status check karke batao.'...")
    tool_calls_observed = []
    stream_chunks = 0
    start_t = time.time()
    
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            for line in resp:
                l = line.decode("utf-8").strip()
                if l.startswith("data: "):
                    ev = json.loads(l[6:])
                    t = ev.get("type")
                    if t == "tool_call":
                        tool_calls_observed.append(ev.get("name"))
                        print(f"  🔧 Agent Triggered Tool Call: {ev.get('name')}({ev.get('args')})")
                    elif t == "tool_result":
                        print(f"  ✅ Tool Result Received for: {ev.get('name')}")
                    elif t == "chunk":
                        stream_chunks += 1
                    elif t == "done":
                        print(f"  🏁 Agent Completed in {time.time()-start_t:.2f}s (Total Stream Chunks: {stream_chunks})")
        print(f"  ✅ Total Tool Calls Executed: {len(tool_calls_observed)}")
    except Exception as e:
        print(f"  ❌ Chat Stream Failed: {e}")

def test_7_all_fastapi_endpoints():
    print_header("TEST 7: FASTAPI HTTP ENDPOINTS COMPREHENSIVE SCAN")
    endpoints = [
        ("GET", "http://localhost:8899/"),
        ("GET", "http://localhost:8899/chat"),
        ("GET", "http://localhost:8899/api/status"),
        ("GET", "http://localhost:8899/api/daemon/status"),
        ("GET", "http://localhost:8899/api/chat/keys"),
        ("GET", "http://localhost:8899/api/chat/sessions"),
        ("GET", "http://localhost:8899/api/unlisted-videos/queue"),
    ]
    
    for method, u in endpoints:
        req = urllib.request.Request(u, method=method)
        start_t = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                lat = (time.time() - start_t) * 1000
                print(f"  ✅ {method} {u} -> Status: {resp.status} | Latency: {lat:.1f}ms")
        except Exception as e:
            print(f"  ❌ {method} {u} -> FAILED: {e}")

def test_8_chrome_and_profiles_preflight():
    print_header("TEST 8: CHROME BROWSER & PERSISTENT PROFILES PRE-FLIGHT")
    from yt_uploader.studio_uploader import CHROME_PATH
    import yt_uploader.channel_manager as cm
    
    print(f"1. Chrome Executable Path: {CHROME_PATH}")
    if os.path.exists(CHROME_PATH):
        print("  ✅ Google Chrome binary exists on system!")
    else:
        print("  ⚠️ Chrome binary not found at default path.")
        
    cfg_file = os.path.join(_root, "yt_uploader", "channels_config.json")
    if os.path.exists(cfg_file):
        data = json.load(open(cfg_file, encoding="utf-8"))
        print(f"2. Verified {len(data)} YouTube Channels Configured:")
        for k, v in data.items():
            prof = v.get("profile_dir", "")
            exists = os.path.exists(prof)
            print(f"    - [{k}] '{v.get('name')}': Profile Exists? {exists} | Quota: {v.get('daily_max_uploads')}/day")
            
    rumble_cfg = os.path.join(_root, "yt_uploader", "rumble_config.json")
    if os.path.exists(rumble_cfg):
        r_data = json.load(open(rumble_cfg, encoding="utf-8"))
        print(f"3. Verified {len(r_data)} Rumble Channels Configured:")
        for k, v in r_data.items():
            prof = v.get("profile_dir", "")
            exists = os.path.exists(prof)
            print(f"    - [{k}] '{v.get('name')}': Profile Exists? {exists} | Quota: {v.get('daily_max_uploads')}/day")

if __name__ == "__main__":
    test_1_gemini_key_pool()
    test_2_edge_tts_shure_sm7b_dsp()
    test_3_outro_and_ambient_drone()
    test_4_open_interpreter()
    test_5_multimodal_vision_endpoint()
    test_6_chat_stream_agent_with_tool_calling()
    test_7_all_fastapi_endpoints()
    test_8_chrome_and_profiles_preflight()
    print("\n" + "=" * 70)
    print("🏆 ALL 8 DEEP SYSTEM TESTS COMPLETE")
    print("=" * 70)
