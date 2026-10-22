"""
OmniChannel 24/7 Perpetual Autonomous Empire Daemon (1000x Edition)
Continuously manufactures and uploads high-retention 30-60 min Tier-1 English documentaries:
- YouTube Fleet: Exactly 5 supreme videos / day per channel (High-retention, algorithmic cadence)
- Rumble Fleet: Exactly 20 high-frequency videos / day per channel (Aggressive monetization)
- Native Tier-1 English Voices (Christopher, Guy, Brian) + 6-Stage Shure SM7B DSP (-14 LUFS)
- Quota-Safe Gemini 3-Key Research Scripting (4,500 Daily Free Capacity)
- 100% Zero-Touch Playwright Automation for YouTube Studio & Rumble
"""

import os
import sys
import json
import time
import random
import threading
from typing import Dict, Any, List, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("perpetual_daemon")

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perpetual_daemon_state.json")
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unlisted_queue.json")
YT_CHANNELS_FILE = os.path.join(_root, "yt_uploader", "channels_config.json")
RUMBLE_CHANNELS_FILE = os.path.join(_root, "yt_uploader", "rumble_config.json")

# Tier-1 English High-RPM Evergreen Topics Bank (30-60 Min Deep Documentaries)
TIER1_TOPICS = [
    # Tech & AI Hardware (Silicon Valley Prime)
    {"topic": "The $500B ASML Monopoly: The Extreme Ultraviolet Machine Controlling Humanity", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 45},
    {"topic": "Inside TSMC: What Happens When the World's 3nm Microchip Fabs Halt for 90 Days", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 42},
    {"topic": "The Subsea Cable War: Who Controls 99% of Global Internet and Financial Data", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 38},
    {"topic": "Project Maven & Sovereign Compute: The Covert Hardware War Inside Modern AI Warfare", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 48},
    {"topic": "The Lithium & Rare Earth Heist: How Global Superpowers Cornered the Next Century", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 36},
    {"topic": "Quantum Decryption Day: The Secret Algorithm That Will Break Every Bank on Earth", "niche": "technology", "voice": "en-US-GuyNeural", "duration_min": 40},

    # Trading & Macroeconomics (Wall Street / London City)
    {"topic": "The $40 Trillion Dark Pool Network: How Wall Street Whales Trade Invisible to Retail", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 46},
    {"topic": "Citadel & Virtu: The 8-Microsecond Microwave War Front-Running Global Markets", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 44},
    {"topic": "The Petrodollar Collapse: How Sovereign Gold Swaps and CBDCs Are Dismantling Fiat", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 52},
    {"topic": "Inside Central Bank Liquidity Swaps: The Shadow Financial System Nobody Understands", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 39},
    {"topic": "The Repo Market Heart Attack: How Wall Street Almost Froze in a Single Afternoon", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 41},
    {"topic": "Black Swan Algorithms: How Hedge Funds Engineered the Greatest Transfer of Wealth", "niche": "trading", "voice": "en-US-ChristopherNeural", "duration_min": 47},

    # Psychology & Covert Power (Global Mystery Audience)
    {"topic": "Mass Behavioral Control: How Dopamine Optimization Algorithms Rewired Modern Society", "niche": "psychology", "voice": "en-US-BrianNeural", "duration_min": 50},
    {"topic": "From MKUltra to Algorithmic Persuasion: The 70-Year Evolution of Psychological Warfare", "niche": "psychology", "voice": "en-US-BrianNeural", "duration_min": 45},
    {"topic": "The Neuroscience of Collective Panics: Why Millions Follow Cults and Market Bubbles", "niche": "psychology", "voice": "en-US-BrianNeural", "duration_min": 38},
    {"topic": "The Architecture of Dark Charisma: How Modern Influencers Weaponize Cognitive Biases", "niche": "psychology", "voice": "en-US-BrianNeural", "duration_min": 42}
]


class PerpetualGeniusDaemon:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PerpetualGeniusDaemon, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.is_running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        default_state = {
            "is_running": False,
            "started_at": None,
            "total_cycles_completed": 0,
            "current_status": "Idle (Daemon Ready for 5/Day YT & 20/Day Rumble)",
            "current_channel": None,
            "current_topic": None,
            "current_step": "Waiting for Start signal",
            "last_cycle_timestamp": None,
            "logs": ["1000x Daemon initialized. Targeted for 5 YouTube/day & 20 Rumble/day in Tier-1 English."]
        }
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    default_state.update(saved)
            except Exception:
                pass
        return default_state

    def _save_state(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save daemon state: {e}")

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        logger.info(entry)
        if "logs" not in self.state:
            self.state["logs"] = []
        self.state["logs"].insert(0, entry)
        if len(self.state["logs"]) > 60:
            self.state["logs"] = self.state["logs"][:60]
        self._save_state()

    def start(self) -> Dict[str, Any]:
        with self._lock:
            if self.is_running:
                return {"success": True, "message": "Daemon already running", "state": self.state}
            self.is_running = True
            self.state["is_running"] = True
            self.state["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.state["current_status"] = "Active (5/Day YT + 20/Day Rumble Perpetual Loop)"
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
            self._worker_thread.start()
            self.log("🚀 24/7 Autonomous Empire Engine STARTED. Targeted for 5 YouTube/day and 20 Rumble/day!")
            self._save_state()
            return {"success": True, "message": "Daemon started successfully", "state": self.state}

    def stop(self) -> Dict[str, Any]:
        with self._lock:
            if not self.is_running:
                return {"success": True, "message": "Daemon is not running", "state": self.state}
            self.is_running = False
            self.state["is_running"] = False
            self.state["current_status"] = "Paused / Stopped"
            self.state["current_step"] = "Idle"
            self._stop_event.set()
            self.log("⏸️ 24/7 Autonomous Empire Engine PAUSED by user.")
            self._save_state()
            return {"success": True, "message": "Daemon paused successfully", "state": self.state}

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "state": self.state
        }

    def _run_loop(self):
        self.log("Entering continuous autonomous Tier-1 long-form manufacturing cycle...")
        while not self._stop_event.is_set():
            try:
                # 0. Midnight UTC/Local Quota Reset
                current_day = time.strftime("%Y-%m-%d")
                if self.state.get("last_active_date") != current_day:
                    self.state["last_active_date"] = current_day
                    yt_channels = self._load_json(YT_CHANNELS_FILE)
                    rumble_channels = self._load_json(RUMBLE_CHANNELS_FILE)
                    for ch in yt_channels.values():
                        ch["uploads_today"] = 0
                    for r in rumble_channels.values():
                        r["uploads_today"] = 0
                    self._save_json(YT_CHANNELS_FILE, yt_channels)
                    self._save_json(RUMBLE_CHANNELS_FILE, rumble_channels)
                    self.log(f"🌅 New Day ({current_day})! Reset daily counters (YT: 5/day, Rumble: 20/day per channel).")

                # 1. Process YouTube Fleet (Target: 5 videos / day per channel)
                yt_channels = self._load_json(YT_CHANNELS_FILE)
                for ch_key, ch_data in yt_channels.items():
                    if self._stop_event.is_set():
                        break

                    daily_max = ch_data.get("daily_max_uploads", 5)
                    uploads_today = ch_data.get("uploads_today", 0)
                    if uploads_today >= daily_max:
                        continue

                    ch_name = ch_data.get("name", ch_key)
                    self.state["current_channel"] = f"YouTube: {ch_name}"
                    self.state["current_step"] = f"1/4. Gemini 3.5 Flash Deep Research & Scripting ({uploads_today + 1}/{daily_max} today)..."
                    self.log(f"🎬 [YouTube: {ch_name}] Manufacturing Tier-1 English episode ({uploads_today + 1}/{daily_max} today)...")
                    self._save_state()

                    # Execute YouTube Production & Upload
                    success = self._manufacture_and_upload_youtube(ch_key, ch_data)
                    if success:
                        self.state["total_cycles_completed"] += 1
                        self.state["last_cycle_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        ch_data["uploads_today"] = uploads_today + 1
                        self._save_json(YT_CHANNELS_FILE, yt_channels)
                        self.log(f"✅ Published to YouTube: {ch_name}! Total completed: {self.state['total_cycles_completed']}")

                    # Cooldown pacing between YouTube uploads
                    self.state["current_step"] = f"Cooldown pacing for YouTube [{ch_name}]..."
                    self._save_state()
                    self._stop_event.wait(45)

                # 2. Process Rumble Fleet (Target: 20 videos / day per channel)
                rumble_channels = self._load_json(RUMBLE_CHANNELS_FILE)
                for r_key, r_data in rumble_channels.items():
                    if self._stop_event.is_set():
                        break

                    daily_max_r = r_data.get("daily_max_uploads", 20)
                    uploads_today_r = r_data.get("uploads_today", 0)
                    if uploads_today_r >= daily_max_r:
                        continue

                    r_name = r_data.get("name", r_key)
                    self.state["current_channel"] = f"Rumble: {r_name}"
                    self.state["current_step"] = f"Manufacturing for Rumble ({uploads_today_r + 1}/{daily_max_r}): '{r_name}'"
                    self.log(f"🟢 [Rumble: {r_name}] Launching video ({uploads_today_r + 1}/{daily_max_r} today)...")
                    self._save_state()

                    # Execute Rumble Production & Upload
                    success_r = self._manufacture_and_upload_rumble(r_key, r_data)
                    if success_r:
                        self.state["total_cycles_completed"] += 1
                        self.state["last_cycle_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        r_data["uploads_today"] = uploads_today_r + 1
                        self._save_json(RUMBLE_CHANNELS_FILE, rumble_channels)
                        self.log(f"✅ Published to Rumble: {r_name}!")

                    self._stop_event.wait(30)

                # Idle sleep between sweep cycles
                self.state["current_status"] = "Active · Autonomous Monitoring & Scheduling"
                self.state["current_step"] = "Checking fleet queues..."
                self._save_state()
                self._stop_event.wait(60)

            except Exception as e:
                logger.error(f"Daemon exception in loop: {e}")
                self.log(f"⚠️ Notice: {e}")
                self._stop_event.wait(30)

    def _manufacture_and_upload_youtube(self, ch_key: str, ch_data: Dict[str, Any], topic_obj: Optional[Dict[str, Any]] = None) -> bool:
        ch_name = ch_data.get("name", ch_key)

        try:
            # 1. Deep Research, Script Synthesis & 1080p Video Rendering with Outro Lock
            self.state["current_step"] = f"1/3. Deep Research & Video Assembly for [{ch_name}]..."
            self._save_state()
            from omnichannel_powerhouse.tier1_producer import produce_and_queue_tier1_video

            prod_res = produce_and_queue_tier1_video(ch_key, ch_data, platform="youtube")
            if not prod_res.get("success"):
                self.log(f"⚠️ Production failed for YouTube: {ch_name}")
                return False

            vid_id = prod_res["video_id"]
            self.state["current_topic"] = prod_res["script_data"].get("title", "Master Documentary")

            # 2. Playwright Studio Zero-Touch Upload (Unlisted)
            self.state["current_step"] = f"2/3. Playwright Studio Auto-Upload to [{ch_name}]..."
            self._save_state()
            from omnichannel_powerhouse.studio_upload_manager import execute_video_upload
            res = execute_video_upload(vid_id, ch_key, headless=False)
            return bool(res.get("success"))

        except Exception as e:
            logger.error(f"Error in YouTube manufacturing sequence: {e}")
            return False

    def _manufacture_and_upload_rumble(self, r_key: str, r_data: Dict[str, Any], topic_obj: Optional[Dict[str, Any]] = None) -> bool:
        r_name = r_data.get("name", r_key)

        try:
            self.state["current_step"] = f"1/3. Manufacturing Tier-1 Episode for Rumble [{r_name}]..."
            self._save_state()
            from omnichannel_powerhouse.tier1_producer import produce_and_queue_tier1_video

            prod_res = produce_and_queue_tier1_video(r_key, r_data, platform="rumble")
            if not prod_res.get("success"):
                return False

            master_video = prod_res["master_video_path"]
            script_data = prod_res["script_data"]

            # Try Playwright Rumble Upload if profile exists
            self.state["current_step"] = f"2/3. Rumble Zero-Touch Upload to [{r_name}]..."
            self._save_state()
            from yt_uploader.rumble_uploader import upload_video_to_rumble
            res = upload_video_to_rumble(
                channel_key=r_key,
                video_file_path=master_video,
                seo_package=script_data,
                license_type=r_data.get("license", "rumble_only"),
                headless=False
            )
            return bool(res.get("success"))
        except Exception as e:
            logger.error(f"Rumble sequence failed for {r_name}: {e}")
            self.log(f"⚠️ Rumble upload failure for {r_name}: {e}")
            return False

    def _prepend_to_queue(self, entry: Dict[str, Any]):
        try:
            queue_data = {"videos": []}
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    queue_data = json.load(f)
            vids = queue_data.get("videos", [])
            vids.insert(0, entry)
            queue_data["videos"] = vids
            queue_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(queue_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error updating queue: {e}")

    def _pick_next_topic(self, niche: str) -> Dict[str, Any]:
        matched = [t for t in TIER1_TOPICS if t.get("niche") == niche]
        if not matched:
            matched = TIER1_TOPICS
        return random.choice(matched)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_json(self, path: str, data: Dict[str, Any]):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


DAEMON = PerpetualGeniusDaemon()


def get_daemon() -> PerpetualGeniusDaemon:
    return DAEMON
