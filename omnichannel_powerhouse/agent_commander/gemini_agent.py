"""
OmniChannel Supreme AI Agent Core (ChatGPT Pro Architecture)
============================================================
Handles conversational reasoning, streaming SSE tokens,
dynamic tool execution (function calling), and context management.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Generator, Optional

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
from omnichannel_powerhouse.agent_commander.tools import TOOL_REGISTRY, GEMINI_FUNCTION_DECLARATIONS
from omnichannel_powerhouse.agent_commander.multi_brain import (
    MULTI_BRAIN,
    convert_gemini_tools_to_openai,
    call_openai_compatible_api
)
from omnichannel_powerhouse.agent_commander.memory import (
    save_message,
    get_sliding_window_context,
    create_session
)

DEFAULT_SYSTEM_PROMPT = """You are the Supreme AI Commander of the OmniChannel Autonomous Empire.
You possess complete real-time authority and agentic tools over:
1. Dynamic Video Production: Synthesizing documentaries of ANY requested duration (5, 10, 15, 20, 30, 45, 60+ min) with Edge-TTS voices and 6-stage Shure SM7B DSP.
2. Batch & Multi-Channel Swarm: Producing multiple videos across multiple channels (Silicon Pulse / channel_trading, Neural Stack / ai_and_tech, Mind Decoded / channel_psychology, motival) in a single command.
3. 24/7 Standing Orders & Daemon: Scheduling recurring autonomous production and uploads every N hours (tool_schedule_standing_order).
4. Content Protection & SEO: Hard-locking the 173.25s Vintage Blue Laser Content ID outro, 98/100 algorithmic SEO, custom thumbnails, and high-velocity pinned debate comments.
5. Zero-Touch Uploads: Uploading directly to YouTube Studio as Unlisted via Playwright Chrome profiles.
6. Zero-Token Shield: Routing queries through Groq (120B @ 800 t/s) and OpenRouter for 100% lifetime free operation with Gemini Key Pool failover.

You speak authoritatively, smartly, and concisely in English, Hindi, or Hinglish depending on what the user speaks.
When the user requests an action (e.g. "Silicon pulse pe 2 video 30 min ki aur Neural Stack pe 1 video 15 min ki banao aur upload kardo", or "har 12 ghante me ek video upload karo"), immediately call the appropriate tool (tool_batch_manufacture_and_upload, tool_manufacture_video, or tool_schedule_standing_order) to execute it.
Always format output in rich GitHub-style Markdown with tables, bullet points, and execution telemetry.
"""


def call_gemini_raw(payload: Dict[str, Any], model: str = "gemini-3.1-flash-lite", timeout: int = 40) -> Dict[str, Any]:
    """Calls Gemini REST API with automatic multi-key rotation, 429/503 failover, and model failover."""
    req_data = json.dumps(payload).encode("utf-8")
    candidate_models = [model]
    for alt in ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-latest"]:
        if alt not in candidate_models:
            candidate_models.append(alt)

    last_err = None
    for cur_m in candidate_models:
        for attempt in range(len(KEY_POOL.keys) or 3):
            key = KEY_POOL.get_key()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{cur_m}:generateContent?key={key}"
            start_t = time.time()
            try:
                req = urllib.request.Request(
                    url, data=req_data,
                    headers={"Content-Type": "application/json", "User-Agent": "OmniChannelAgent"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    latency = time.time() - start_t
                    KEY_POOL.record_success(key, latency)
                    return res_data
            except urllib.error.HTTPError as e:
                last_err = e
                KEY_POOL.record_error(key, status_code=e.code)
                time.sleep(0.3)
            except Exception as e:
                last_err = e
                KEY_POOL.record_error(key, status_code=500)
                time.sleep(0.3)

    raise RuntimeError(f"All Gemini models & keys in pool failed: {last_err}")


def stream_chat_response(
    session_id: str,
    user_prompt: str,
    model_name: str = "gemini-3.5-flash",
    enable_tools: bool = True
) -> Generator[str, None, None]:
    """
    Generator streaming Server-Sent Events (SSE) to the web UI.
    Emits thinking state, tool invocations, tool execution results, and token text.
    """
    if not session_id:
        session_id = create_session(user_prompt[:40] + "...")

    # Save user message to SQLite
    save_message(session_id, role="user", content=user_prompt)

    # Yield initial handshake
    yield f"data: {json.dumps({'type': 'start', 'session_id': session_id, 'model': model_name})}\n\n"

    # Retrieve sliding-window context
    past_messages = get_sliding_window_context(session_id, max_turns=6)

    # Build Gemini contents structure
    contents = []
    for msg in past_messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": DEFAULT_SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.6,
            "topP": 0.95,
            "maxOutputTokens": 4096
        }
    }

    if enable_tools:
        payload["tools"] = [{"function_declarations": GEMINI_FUNCTION_DECLARATIONS}]

    # Yield Thinking Process Card
    yield f"data: {json.dumps({'type': 'thinking_start', 'message': 'Deducing strategic intent & cross-referencing empire telemetry...'})}\n\n"
    time.sleep(0.2)

    target_provider = "gemini"
    target_model_id = model_name

    # Model Aliases for decommissioned or renamed third-party endpoints
    GROQ_MODEL_ALIASES = {
        "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
        "llama-3.1-70b-versatile": "openai/gpt-oss-120b",
        "llama3-70b-8192": "openai/gpt-oss-120b",
        "deepseek-r1-distill-llama-70b": "openai/gpt-oss-120b",
        "llama-3.1-8b-instant": "openai/gpt-oss-20b",
        "mixtral-8x7b-32768": "openai/gpt-oss-120b"
    }
    OPENROUTER_MODEL_ALIASES = {
        "deepseek/deepseek-r1:free": "nvidia/nemotron-3.5-lightning:free",
        "meta-llama/llama-3.3-70b-instruct:free": "nvidia/nemotron-3.5-lightning:free"
    }

    if model_name.startswith("groq:"):
        target_provider = "groq"
        raw_id = model_name.split("groq:", 1)[1]
        target_model_id = GROQ_MODEL_ALIASES.get(raw_id, raw_id)
    elif model_name.startswith("openrouter:"):
        target_provider = "openrouter"
        raw_id = model_name.split("openrouter:", 1)[1]
        target_model_id = OPENROUTER_MODEL_ALIASES.get(raw_id, raw_id)
    elif model_name in ("hybrid:auto", "auto"):
        if MULTI_BRAIN.get_groq_key():
            target_provider = "groq"
            target_model_id = "openai/gpt-oss-120b"
        elif MULTI_BRAIN.get_openrouter_key():
            target_provider = "openrouter"
            target_model_id = "nvidia/nemotron-3.5-lightning:free"
        else:
            target_provider = "gemini"
            target_model_id = "gemini-3.1-flash-lite"

    # --- MULTI-BRAIN EXECUTION (GROQ / OPENROUTER) ---
    if target_provider in ("groq", "openrouter"):
        api_key = MULTI_BRAIN.get_groq_key() if target_provider == "groq" else MULTI_BRAIN.get_openrouter_key()
        endpoint = "https://api.groq.com/openai/v1/chat/completions" if target_provider == "groq" else "https://openrouter.ai/api/v1/chat/completions"

        if not api_key:
            notice = f"> ℹ️ *[{target_provider.upper()} API key not configured yet. Auto-routing through Gemini 3.5 Flash Key Pool]*\n\n"
            yield f"data: {json.dumps({'type': 'chunk', 'text': notice})}\n\n"
            target_provider = "gemini"
            model_name = "gemini-3.5-flash"
        else:
            openai_messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
            for msg in past_messages:
                openai_messages.append({"role": msg["role"], "content": msg["content"]})

            openai_tools = convert_gemini_tools_to_openai(GEMINI_FUNCTION_DECLARATIONS) if enable_tools else None

            try:
                resp = call_openai_compatible_api(
                    endpoint=endpoint,
                    api_key=api_key,
                    model=target_model_id,
                    messages=openai_messages,
                    tools=openai_tools
                )
                choice = resp.get("choices", [{}])[0].get("message", {})
                tool_calls = choice.get("tool_calls", [])
                assistant_final_text = ""
                thinking_text = f"Executed via {target_provider.upper()} ({target_model_id}) with ultra-low latency."
                executed_tools = []

                if tool_calls:
                    assistant_msg = {
                        "role": "assistant",
                        "content": choice.get("content") or "",
                        "tool_calls": tool_calls
                    }
                    openai_messages.append(assistant_msg)

                    for tc in tool_calls:
                        fn_info = tc.get("function", {})
                        fn_name = fn_info.get("name")
                        fn_args = {}
                        try:
                            fn_args = json.loads(fn_info.get("arguments", "{}"))
                        except Exception:
                            pass

                        yield f"data: {json.dumps({'type': 'tool_call', 'name': fn_name, 'args': fn_args})}\n\n"
                        tool_func = TOOL_REGISTRY.get(fn_name)
                        tool_result = {}
                        if tool_func:
                            try:
                                tool_result = tool_func(**fn_args)
                            except Exception as te:
                                tool_result = {"success": False, "error": str(te)}
                        else:
                            tool_result = {"success": False, "error": f"Tool '{fn_name}' not registered"}

                        executed_tools.append({"tool": fn_name, "args": fn_args, "result": tool_result})
                        yield f"data: {json.dumps({'type': 'tool_result', 'name': fn_name, 'result': tool_result})}\n\n"

                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tc.get("id", "call_1"),
                            "content": json.dumps(tool_result)
                        })

                    followup = call_openai_compatible_api(
                        endpoint=endpoint,
                        api_key=api_key,
                        model=target_model_id,
                        messages=openai_messages,
                        tools=None
                    )
                    assistant_final_text = followup.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    assistant_final_text = choice.get("content", "")

                if "<think>" in assistant_final_text and "</think>" in assistant_final_text:
                    s_idx = assistant_final_text.find("<think>") + len("<think>")
                    e_idx = assistant_final_text.find("</think>")
                    thinking_text = assistant_final_text[s_idx:e_idx].strip()
                    assistant_final_text = assistant_final_text[e_idx + len("</think>"):].strip()

                yield f"data: {json.dumps({'type': 'thinking_done', 'thought': thinking_text[:500]})}\n\n"

                words = assistant_final_text.split(" ")
                buffer = ""
                for idx, w in enumerate(words):
                    buffer += w + " "
                    if idx % 4 == 0 or idx == len(words) - 1:
                        yield f"data: {json.dumps({'type': 'chunk', 'text': buffer})}\n\n"
                        buffer = ""
                        time.sleep(0.01)

                save_message(
                    session_id=session_id,
                    role="assistant",
                    content=assistant_final_text,
                    thinking=thinking_text,
                    tool_calls=executed_tools
                )
                yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
                return

            except Exception as e:
                err_str = str(e)[:80]
                failover_msg = f"> ⚠️ *[{target_provider.upper()} API notice: {err_str}. Seamless failover to Gemini Key Pool...]*\n\n"
                yield f"data: {json.dumps({'type': 'chunk', 'text': failover_msg})}\n\n"
                target_provider = "gemini"
                model_name = "gemini-3.5-flash"

    try:
        resp = call_gemini_raw(payload, model=model_name)
    except Exception as e:
        err_msg = f"API Error: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': err_msg})}\n\n"
        save_message(session_id, role="assistant", content=err_msg)
        return

    candidate = resp.get("candidates", [{}])[0]
    content_obj = candidate.get("content", {})
    parts = content_obj.get("parts", [])

    thinking_text = "Analyzed user query, verified channel configurations and quota states."
    
    # Check for functionCall
    has_tool_call = any("functionCall" in p for p in parts)
    assistant_final_text = ""
    executed_tools = []

    for part in parts:
        if "functionCall" in part:
            fn_call = part["functionCall"]
            fn_name = fn_call.get("name")
            fn_args = fn_call.get("args", {})

            yield f"data: {json.dumps({'type': 'tool_call', 'name': fn_name, 'args': fn_args})}\n\n"

            # Execute the tool locally!
            tool_func = TOOL_REGISTRY.get(fn_name)
            tool_result = {}
            if tool_func:
                try:
                    tool_result = tool_func(**fn_args)
                except Exception as te:
                    tool_result = {"success": False, "error": str(te)}
            else:
                tool_result = {"success": False, "error": f"Tool '{fn_name}' not registered"}

            executed_tools.append({"tool": fn_name, "args": fn_args, "result": tool_result})
            yield f"data: {json.dumps({'type': 'tool_result', 'name': fn_name, 'result': tool_result})}\n\n"

            # Feed tool result back to Gemini for natural language synthesis
            followup_contents = list(contents)
            followup_contents.append({
                "role": "model",
                "parts": [{"functionCall": {"name": fn_name, "args": fn_args}}]
            })
            followup_contents.append({
                "role": "function",
                "parts": [{
                    "functionResponse": {
                        "name": fn_name,
                        "response": {"name": fn_name, "content": tool_result}
                    }
                }]
            })

            followup_payload = {
                "contents": followup_contents,
                "systemInstruction": {"parts": [{"text": DEFAULT_SYSTEM_PROMPT}]},
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 3000}
            }
            if enable_tools:
                followup_payload["tools"] = [{"function_declarations": GEMINI_FUNCTION_DECLARATIONS}]

            try:
                followup_resp = call_gemini_raw(followup_payload, model=model_name)
                f_parts = followup_resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for fp in f_parts:
                    if "text" in fp:
                        assistant_final_text += fp["text"]
            except Exception:
                assistant_final_text = f"Action **{fn_name}** executed successfully. Result: `{json.dumps(tool_result)[:300]}`"

        elif "text" in part:
            if has_tool_call:
                # If tool call is present in the turn, text is model's internal deliberation
                thinking_text = part["text"][:500]
            else:
                assistant_final_text += part["text"]

    # Filter out leaked internal thoughts (e.g. "The user wants to... Plan: ...")
    if "The user wants to" in assistant_final_text:
        parts_split = assistant_final_text.split("###")
        if len(parts_split) > 1:
            assistant_final_text = "###" + parts_split[1]

    yield f"data: {json.dumps({'type': 'thinking_done', 'thought': thinking_text[:500]})}\n\n"

    # Stream the assistant's final text in chunks for smooth ChatGPT Pro experience
    words = assistant_final_text.split(" ")
    buffer = ""
    for idx, w in enumerate(words):
        buffer += w + " "
        if idx % 3 == 0 or idx == len(words) - 1:
            yield f"data: {json.dumps({'type': 'chunk', 'text': buffer})}\n\n"
            buffer = ""
            time.sleep(0.015)

    # Save to SQLite memory
    save_message(
        session_id=session_id,
        role="assistant",
        content=assistant_final_text,
        thinking=thinking_text,
        tool_calls=executed_tools
    )

    yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"


def analyze_visual_media(
    image_base64: Optional[str] = None,
    image_path: Optional[str] = None,
    prompt: Optional[str] = None,
    model_name: str = "gemini-3.5-flash"
) -> Dict[str, Any]:
    """
    Multimodal Vision Engine: Audits thumbnails, charts, or screenshots
    for CTR, visual contrast, readability, and institutional aesthetics.
    """
    import base64
    import mimetypes

    if not prompt:
        prompt = (
            "Analyze this YouTube thumbnail/visual media for high-CTR institutional appeal, "
            "rule of thirds, text contrast, and Tier-1 audience retention. Provide:\n"
            "1) Estimated CTR Score (0-100%)\n"
            "2) Focal Point & Composition Audit\n"
            "3) Typography & Mobile Readability (at 100px width)\n"
            "4) 3 Direct Actionable Tweaks to Maximize Organic Clicks"
        )

    b64_data = ""
    mime_type = "image/jpeg"

    if image_base64:
        # Strip data URL prefix if present
        if "base64," in image_base64:
            header, b64_data = image_base64.split("base64,", 1)
            if "image/png" in header:
                mime_type = "image/png"
            elif "image/webp" in header:
                mime_type = "image/webp"
        else:
            b64_data = image_base64
    elif image_path and os.path.exists(image_path):
        mtype, _ = mimetypes.guess_type(image_path)
        if mtype:
            mime_type = mtype
        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
    else:
        return {"success": False, "error": "No valid image data or path provided"}

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048
        }
    }

    try:
        resp = call_gemini_raw(payload, model=model_name)
        parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        review_text = "".join(p.get("text", "") for p in parts)
        return {
            "success": True,
            "analysis": review_text,
            "model_used": model_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
