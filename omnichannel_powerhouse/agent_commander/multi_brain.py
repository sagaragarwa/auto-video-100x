"""
OmniChannel Multi-Brain Engine (Gemini + Groq + OpenRouter + Smart Hybrid Router)
================================================================================
Orchestrates multiple AI engines with 100% lifetime free operation:
1. Google Gemini 3.5 (1M Context, Native 4K Multimodal Vision, Multi-Key Pool)
2. GroqCloud LPU (800+ tokens/sec, Sub-200ms TTFT, Uncensored Llama 3.3 70B)
3. OpenRouter Free Tier (DeepSeek-R1 Chain-of-Thought, Qwen 2.5 72B)
4. Auto-Smart Hybrid Router with Automatic Fallback to Gemini
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from omnichannel_powerhouse.agent_commander.key_pool import KEY_POOL
from omnichannel_powerhouse.agent_commander.tools import TOOL_REGISTRY, GEMINI_FUNCTION_DECLARATIONS

MULTI_BRAIN_KEYS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "multi_brain_keys.json")
GROQ_LOCAL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "groq_api_key.local")
OPENROUTER_LOCAL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openrouter_api_key.local")


class MultiBrainManager:
    """Manages multi-provider API keys and health telemetry."""

    def __init__(self):
        self.groq_keys: List[Dict[str, Any]] = []
        self.openrouter_keys: List[Dict[str, Any]] = []
        self.load_all_keys()

    def load_all_keys(self):
        # 1. Groq Keys from local file or env
        self.groq_keys = []
        if os.path.exists(GROQ_LOCAL_FILE):
            try:
                k = open(GROQ_LOCAL_FILE, "r", encoding="utf-8").read().strip()
                if k:
                    self.groq_keys.append({"key": k, "label": "Groq Primary Key", "status": "healthy", "daily_count": 0, "avg_latency": 0.25})
            except Exception:
                pass
        env_groq = os.environ.get("GROQ_API_KEY", "").strip()
        if env_groq and not any(x["key"] == env_groq for x in self.groq_keys):
            self.groq_keys.append({"key": env_groq, "label": "Groq Env Key", "status": "healthy", "daily_count": 0, "avg_latency": 0.25})

        # 2. OpenRouter Keys from local file or env
        self.openrouter_keys = []
        if os.path.exists(OPENROUTER_LOCAL_FILE):
            try:
                k = open(OPENROUTER_LOCAL_FILE, "r", encoding="utf-8").read().strip()
                if k:
                    self.openrouter_keys.append({"key": k, "label": "OpenRouter Primary Key", "status": "healthy", "daily_count": 0, "avg_latency": 1.2})
            except Exception:
                pass
        env_or = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if env_or and not any(x["key"] == env_or for x in self.openrouter_keys):
            self.openrouter_keys.append({"key": env_or, "label": "OpenRouter Env Key", "status": "healthy", "daily_count": 0, "avg_latency": 1.2})

        # 3. Load from multi_brain_keys.json
        if os.path.exists(MULTI_BRAIN_KEYS_FILE):
            try:
                with open(MULTI_BRAIN_KEYS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("groq_keys", []):
                        k = item.get("key", "").strip()
                        if k and not any(x["key"] == k for x in self.groq_keys):
                            self.groq_keys.append({
                                "key": k,
                                "label": item.get("label", f"Groq Key {len(self.groq_keys)+1:02d}"),
                                "status": "healthy",
                                "daily_count": 0,
                                "avg_latency": 0.25
                            })
                    for item in data.get("openrouter_keys", []):
                        k = item.get("key", "").strip()
                        if k and not any(x["key"] == k for x in self.openrouter_keys):
                            self.openrouter_keys.append({
                                "key": k,
                                "label": item.get("label", f"OpenRouter Key {len(self.openrouter_keys)+1:02d}"),
                                "status": "healthy",
                                "daily_count": 0,
                                "avg_latency": 1.2
                            })
            except Exception:
                pass

    def save_keys(self):
        data = {
            "groq_keys": [{"key": k["key"], "label": k["label"]} for k in self.groq_keys],
            "openrouter_keys": [{"key": k["key"], "label": k["label"]} for k in self.openrouter_keys]
        }
        try:
            with open(MULTI_BRAIN_KEYS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def add_key(self, api_key: str, label: str = "", provider: str = "auto") -> Dict[str, Any]:
        clean_key = api_key.strip()
        if not clean_key:
            return {"success": False, "error": "API key cannot be empty"}

        # Auto-detect provider if auto
        if provider == "auto":
            if clean_key.startswith("AIzaSy"):
                provider = "gemini"
            elif clean_key.startswith("gsk_"):
                provider = "groq"
            elif clean_key.startswith("sk-or-"):
                provider = "openrouter"
            else:
                provider = "gemini"

        if provider == "gemini":
            return KEY_POOL.add_key(clean_key, label=label)

        elif provider == "groq":
            # Validate with test call
            is_valid, err = self.test_groq_key(clean_key)
            if not is_valid:
                return {"success": False, "error": f"Invalid Groq key: {err}"}

            if not any(x["key"] == clean_key for x in self.groq_keys):
                new_lbl = label or f"Groq Key {len(self.groq_keys)+1:02d}"
                self.groq_keys.append({"key": clean_key, "label": new_lbl, "status": "healthy", "daily_count": 0, "avg_latency": 0.25})
                self.save_keys()
                # Also save to local file
                with open(GROQ_LOCAL_FILE, "w", encoding="utf-8") as f:
                    f.write(clean_key)
                return {"success": True, "provider": "groq", "message": f"Successfully enrolled Groq Key '{new_lbl}'! 800 t/s unlocked."}
            return {"success": True, "message": "Groq Key already enrolled"}

        elif provider == "openrouter":
            is_valid, err = self.test_openrouter_key(clean_key)
            if not is_valid:
                return {"success": False, "error": f"Invalid OpenRouter key: {err}"}

            if not any(x["key"] == clean_key for x in self.openrouter_keys):
                new_lbl = label or f"OpenRouter Key {len(self.openrouter_keys)+1:02d}"
                self.openrouter_keys.append({"key": clean_key, "label": new_lbl, "status": "healthy", "daily_count": 0, "avg_latency": 1.2})
                self.save_keys()
                with open(OPENROUTER_LOCAL_FILE, "w", encoding="utf-8") as f:
                    f.write(clean_key)
                return {"success": True, "provider": "openrouter", "message": f"Successfully enrolled OpenRouter Key '{new_lbl}'! DeepSeek-R1 unlocked."}
            return {"success": True, "message": "OpenRouter Key already enrolled"}

        return {"success": False, "error": f"Unknown provider '{provider}'"}

    def test_groq_key(self, key: str) -> Tuple[bool, str]:
        url = "https://api.groq.com/openai/v1/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "MultiBrain"})
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                return resp.status == 200, ""
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, str(e)

    def test_openrouter_key(self, key: str) -> Tuple[bool, str]:
        url = "https://openrouter.ai/api/v1/auth/key"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "MultiBrain"})
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                return resp.status == 200, ""
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, str(e)

    def record_groq_error(self, key: str, status_code: int = 429):
        """Temporarily throttles Groq key on 429/403 so subsequent queries route seamlessly without delay."""
        now = time.time()
        for k in self.groq_keys:
            if k["key"] == key:
                k["status"] = "throttled"
                k["throttled_until"] = now + 120  # 2-minute cooloff

    def get_groq_key(self) -> Optional[str]:
        now = time.time()
        for k in self.groq_keys:
            if k.get("status") == "throttled" and now > k.get("throttled_until", 0):
                k["status"] = "healthy"
        healthy = [k for k in self.groq_keys if k.get("status") == "healthy"]
        if healthy:
            return healthy[0]["key"]
        return None

    def get_openrouter_key(self) -> Optional[str]:
        healthy = [k for k in self.openrouter_keys if k["status"] == "healthy"]
        if healthy:
            return healthy[0]["key"]
        return None

    def get_all_telemetry(self) -> Dict[str, Any]:
        gemini_telem = KEY_POOL.get_telemetry()
        groq_telem = {
            "total_keys": len(self.groq_keys),
            "keys": [{"label": k["label"], "status": k["status"]} for k in self.groq_keys]
        }
        openrouter_telem = {
            "total_keys": len(self.openrouter_keys),
            "keys": [{"label": k["label"], "status": k["status"]} for k in self.openrouter_keys]
        }
        # Top-level backwards compatibility for existing UI
        res = dict(gemini_telem)
        res["providers"] = {
            "gemini": gemini_telem,
            "groq": groq_telem,
            "openrouter": openrouter_telem
        }
        res["groq_keys_count"] = len(self.groq_keys)
        res["openrouter_keys_count"] = len(self.openrouter_keys)
        res["hybrid_ready"] = True
        return res


MULTI_BRAIN = MultiBrainManager()


def convert_gemini_tools_to_openai(gemini_declarations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recursively converts Gemini function declarations to OpenAI tools JSON schema."""
    def _lower_types(obj: Any) -> Any:
        if isinstance(obj, dict):
            res = {}
            for k, v in obj.items():
                if k == "type" and isinstance(v, str):
                    res[k] = v.lower()
                else:
                    res[k] = _lower_types(v)
            return res
        elif isinstance(obj, list):
            return [_lower_types(x) for x in obj]
        return obj

    openai_tools = []
    for decl in gemini_declarations:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": decl["name"],
                "description": decl.get("description", ""),
                "parameters": _lower_types(decl.get("parameters", {"type": "object", "properties": {}}))
            }
        })
    return openai_tools


def call_openai_compatible_api(
    endpoint: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 35
) -> Dict[str, Any]:
    """Calls any OpenAI-compatible endpoint (Groq or OpenRouter) with full tool calling support."""
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 4096
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data_bytes,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OmniChannelMultiBrain/1.0"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_hybrid_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 8192,
    timeout: int = 45
) -> str:
    """
    Tiered Zero-Token Completion Engine:
    1. Groq (openai/gpt-oss-120b) -> 800+ tokens/sec, 100% Free, 0 Gemini tokens!
    2. OpenRouter (nvidia/nemotron-3.5-lightning:free) -> 100% Free, 0 Gemini tokens!
    3. Gemini Key Pool (gemini-3.1-flash-lite) -> 3-key round-robin failover
    """
    msgs: List[Dict[str, Any]] = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    msgs.append({"role": "user", "content": prompt})

    # 1. Try Groq (120B Frontier Model, Sub-second TTFT)
    groq_key = MULTI_BRAIN.get_groq_key()
    if groq_key:
        try:
            res = call_openai_compatible_api(
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                model="openai/gpt-oss-120b",
                messages=msgs,
                timeout=timeout
            )
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content and len(content.strip()) > 20:
                return content.strip()
        except Exception as e:
            pass

    # 2. Try OpenRouter Free Tier
    or_key = MULTI_BRAIN.get_openrouter_key()
    if or_key:
        try:
            res = call_openai_compatible_api(
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                api_key=or_key,
                model="nvidia/nemotron-3.5-lightning:free",
                messages=msgs,
                timeout=timeout
            )
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content and len(content.strip()) > 20:
                return content.strip()
        except Exception as e:
            pass

    # 3. Fallback to Gemini 3.1 Flash Lite Multi-Key Pool
    try:
        from omnichannel_powerhouse.gemini_script_engine import call_gemini
        return call_gemini(prompt, model="gemini-3.1-flash-lite")
    except Exception as e:
        raise RuntimeError(f"All multi-brain providers failed: {e}")
