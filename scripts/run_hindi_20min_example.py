import os
import sys
import json
import time

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

from omnichannel_powerhouse.tier1_producer import produce_and_queue_tier1_video

channel_data = {
    "name": "Get Neural Stack Pro",
    "niche": "technology",
    "voice_preferred": "hi-IN-MadhurNeural"
}

topic = "The Microchip Monopoly: Kaise ASML Aur TSMC Puri Duniya Ki Technology Ko Secretly Control Karte Hain"

print("🚀 Starting 20-minute Hindi Master Video Generation (ZERO AI IMAGES, 100% REAL STOCK FOOTAGE)...", flush=True)
result = produce_and_queue_tier1_video(
    channel_key="yt_tech_01",
    channel_data=channel_data,
    platform="youtube",
    duration_min=20,
    custom_topic=topic,
    language="hi",
    auto_upload_unlisted=False
)

print("✅ Master Video Complete!", flush=True)
print(f"Video ID: {result.get('video_id')}")
print(f"Master Path: {result.get('master_video_path')}")
print(f"Title: {result.get('script_data', {}).get('title')}")
print(f"SEO Score: {result.get('script_data', {}).get('seo_score')}")
