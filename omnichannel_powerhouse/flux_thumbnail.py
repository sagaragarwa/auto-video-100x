"""
Cloudflare Workers AI Free Thumbnail Generator (Flux.1 Schnell)
==============================================================
Generates 1080p photorealistic thumbnail backgrounds completely free using
Black Forest Labs' Flux.1 Schnell model under Cloudflare's 10,000 Neurons/day free tier.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

CLOUDFLARE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflare_config.local")


def load_cloudflare_credentials() -> Dict[str, str]:
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()

    if os.path.exists(CLOUDFLARE_CONFIG_FILE):
        try:
            with open(CLOUDFLARE_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                account_id = account_id or data.get("account_id", "").strip()
                api_token = api_token or data.get("api_token", "").strip()
        except Exception:
            pass

    return {"account_id": account_id, "api_token": api_token}


def generate_flux_thumbnail_background(
    prompt: str,
    output_path: str,
    steps: int = 4
) -> Dict[str, Any]:
    """
    Generates a high-CTR image via Cloudflare Workers AI Flux.1 Schnell.
    Free tier quota: 10,000 Neurons/day.
    """
    creds = load_cloudflare_credentials()
    account_id = creds["account_id"]
    api_token = creds["api_token"]

    if not account_id or not api_token:
        return {
            "success": False,
            "error": "Cloudflare credentials not configured. Please set account_id and api_token."
        }

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    payload = {
        "prompt": f"{prompt}, 8k resolution, cinematic lighting, photorealistic, documentary thumbnail, high contrast, trending on artstation",
        "steps": min(steps, 8)
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            # Flux endpoint returns raw image bytes or json with image base64
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            if "application/json" in content_type:
                data = json.loads(raw.decode("utf-8"))
                import base64
                img_b64 = data.get("result", {}).get("image", "")
                if img_b64:
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(img_b64))
                else:
                    return {"success": False, "error": "No image returned in JSON payload"}
            else:
                with open(output_path, "wb") as f:
                    f.write(raw)

            return {
                "success": True,
                "output_path": output_path,
                "model": "flux-1-schnell",
                "bytes": os.path.getsize(output_path)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
