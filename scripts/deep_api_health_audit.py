import os
import sys
import json
import time
import urllib.request
import urllib.error

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

report = {}

# 1. TEST GROQ API
t0 = time.time()
try:
    from omnichannel_powerhouse.agent_commander.multi_brain import MULTI_BRAIN, call_openai_compatible_api
    k = MULTI_BRAIN.get_groq_key()
    if k:
        res = call_openai_compatible_api(
            endpoint="https://api.groq.com/openai/v1/chat/completions",
            api_key=k,
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "Ping test: reply with 'PONG'"}],
            timeout=10
        )
        content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        latency = round(time.time() - t0, 3)
        report["Groq_120B_API"] = {"status": "ONLINE", "latency_sec": latency, "response": content[:60]}
    else:
        report["Groq_120B_API"] = {"status": "NO_KEY"}
except Exception as e:
    report["Groq_120B_API"] = {"status": "ERROR", "error": str(e)}

# 2. TEST OPENROUTER API
t0 = time.time()
try:
    k = MULTI_BRAIN.get_openrouter_key()
    if k:
        res = call_openai_compatible_api(
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            api_key=k,
            model="nvidia/nemotron-3.5-lightning:free",
            messages=[{"role": "user", "content": "Ping test: reply with 'PONG'"}],
            timeout=12
        )
        content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        latency = round(time.time() - t0, 3)
        report["OpenRouter_Free_API"] = {"status": "ONLINE", "latency_sec": latency, "response": content[:60]}
    else:
        report["OpenRouter_Free_API"] = {"status": "NO_KEY"}
except Exception as e:
    report["OpenRouter_Free_API"] = {"status": "ERROR", "error": str(e)}

# 3. TEST GEMINI KEY-RING POOL (All 3 Keys)
gemini_results = []
try:
    from omnichannel_powerhouse.gemini_key_rotator import KEY_RING
    for idx, item in enumerate(KEY_RING.keys):
        t0 = time.time()
        k_val = item.get("key")
        lbl = item.get("label", f"Key_{idx+1}")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={k_val}"
            payload = json.dumps({"contents": [{"parts": [{"text": "Reply 'OK'"}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                cand = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                gemini_results.append({"label": lbl, "status": "ONLINE", "latency_sec": round(time.time()-t0, 3), "reply": cand})
        except Exception as ge:
            gemini_results.append({"label": lbl, "status": "ERROR", "error": str(ge)})
    report["Gemini_KeyRing_Pool"] = gemini_results
except Exception as e:
    report["Gemini_KeyRing_Pool"] = {"status": "ERROR", "error": str(e)}

# 4. TEST PIXABAY VIDEO API
t0 = time.time()
try:
    from omnichannel_powerhouse.multi_stock_aggregator import query_pixabay_videos
    hits = query_pixabay_videos("artificial intelligence", target_count=5)
    report["Pixabay_Video_API"] = {"status": "ONLINE", "clips_returned": len(hits), "latency_sec": round(time.time()-t0, 3)}
except Exception as e:
    report["Pixabay_Video_API"] = {"status": "ERROR", "error": str(e)}

# 5. TEST PEXELS KEYLESS CDN EXTRACTOR
t0 = time.time()
try:
    from omnichannel_powerhouse.multi_stock_aggregator import query_pexels_videos
    hits = query_pexels_videos("technology servers", target_count=3)
    report["Pexels_CDN_Extractor"] = {"status": "ONLINE", "clips_returned": len(hits), "latency_sec": round(time.time()-t0, 3)}
except Exception as e:
    report["Pexels_CDN_Extractor"] = {"status": "ERROR", "error": str(e)}

# 6. TEST WIKIMEDIA COMMONS VIDEO API
t0 = time.time()
try:
    from omnichannel_powerhouse.multi_stock_aggregator import query_wikimedia_videos
    hits = query_wikimedia_videos("supercomputer", target_count=3)
    report["Wikimedia_Video_API"] = {"status": "ONLINE", "clips_returned": len(hits), "latency_sec": round(time.time()-t0, 3)}
except Exception as e:
    report["Wikimedia_Video_API"] = {"status": "ERROR", "error": str(e)}

# 7. TEST KOKORO-82M ENGINE
t0 = time.time()
try:
    from omnichannel_powerhouse.kokoro_engine import get_kokoro_instance, MODEL_FILE, VOICES_FILE
    k_inst = get_kokoro_instance()
    report["Kokoro_82M_Engine"] = {
        "status": "ONLINE" if k_inst else "FAILED_LOAD",
        "model_file_exists": os.path.exists(MODEL_FILE),
        "voices_file_exists": os.path.exists(VOICES_FILE),
        "model_mb": round(os.path.getsize(MODEL_FILE)/(1024*1024), 1) if os.path.exists(MODEL_FILE) else 0,
        "voices_mb": round(os.path.getsize(VOICES_FILE)/(1024*1024), 1) if os.path.exists(VOICES_FILE) else 0
    }
except Exception as e:
    report["Kokoro_82M_Engine"] = {"status": "ERROR", "error": str(e)}

# 8. TEST CHROMADB VECTOR MEMORY
t0 = time.time()
try:
    from omnichannel_powerhouse.vector_memory import VECTOR_MEMORY
    is_ready = VECTOR_MEMORY.collection is not None
    res = VECTOR_MEMORY.query_similar_topics("semiconductor", niche="tech", n_results=1)
    report["ChromaDB_Vector_Memory"] = {
        "status": "ONLINE" if is_ready else "FALLBACK",
        "query_latency_sec": round(time.time()-t0, 3),
        "matches_found": len(res)
    }
except Exception as e:
    report["ChromaDB_Vector_Memory"] = {"status": "ERROR", "error": str(e)}

# 9. TEST CHATBOT BACKEND SERVER & API ENDPOINTS
t0 = time.time()
try:
    req = urllib.request.Request("http://127.0.0.1:8899/api/channels")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode())
        ch_count = len(data.get("channels", []))
    
    # Test chat streaming SSE endpoint
    fresh_session = f"audit_session_{int(time.time())}"
    chat_payload = json.dumps({
        "message": "Status check: Confirm system operational in one sentence.",
        "session_id": fresh_session,
        "model": "auto"
    }).encode("utf-8")
    chat_req = urllib.request.Request(
        "http://127.0.0.1:8899/api/chat/message",
        data=chat_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    chat_reply_chunks = []
    with urllib.request.urlopen(chat_req, timeout=12) as cr:
        while True:
            line = cr.readline().decode("utf-8")
            if not line:
                break
            if line.startswith("data: "):
                try:
                    payload = json.loads(line[6:].strip())
                    if payload.get("type") == "chunk":
                        chat_reply_chunks.append(payload.get("text", ""))
                except Exception:
                    pass
    chat_reply = "".join(chat_reply_chunks).strip()

    report["Chatbot_Server_API"] = {
        "status": "ONLINE",
        "live_channels_loaded": ch_count,
        "server_latency_sec": round(time.time()-t0, 3),
        "chat_endpoint_working": bool(chat_reply),
        "chat_sample_reply": chat_reply[:140]
    }
except Exception as e:
    report["Chatbot_Server_API"] = {"status": "ERROR", "error": str(e)}

print(json.dumps(report, indent=2))
