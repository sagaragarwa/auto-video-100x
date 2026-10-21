import os
import sys
import json
from loguru import logger

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels_config.json")
PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")

def load_channels():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "channel_psychology": {
                "name": "Psychology & Mental Health Channel",
                "profile_dir": os.path.join(PROFILES_DIR, "channel_psychology"),
                "niche": "psychology",
                "visibility": "public"
            },
            "channel_trading": {
                "name": "Trading & Finance Channel",
                "profile_dir": os.path.join(PROFILES_DIR, "channel_trading"),
                "niche": "trading",
                "visibility": "public"
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read channels_config.json: {e}")
        return {}

def save_channels(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def open_login_window(channel_key: str):
    """
    Opens a real Chrome window with the specified channel profile.
    The user logs in to YouTube Studio manually ONCE.
    All cookies and tokens are permanently saved.
    """
    from playwright.sync_api import sync_playwright

    channels = load_channels()
    if channel_key not in channels:
        logger.error(f"Channel key '{channel_key}' not found in channels_config.json")
        return False

    ch_info = channels[channel_key]
    profile_path = os.path.abspath(ch_info["profile_dir"])
    os.makedirs(profile_path, exist_ok=True)

    logger.info(f"Opening Chrome window for channel: '{ch_info['name']}'...")
    logger.info("Please log in to your Google Account / YouTube Studio in the opened Chrome window.")
    logger.info("Once you are logged into YouTube Studio, close the browser window to complete setup.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=False,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = context.new_page()
        page.goto("https://studio.youtube.com")
        page.wait_for_timeout(5000)

        # Keep browser open until user closes it
        logger.info("Browser is active. Log in to your YouTube Studio and close the window when done...")
        try:
            context.pages[0].wait_for_event("close", timeout=0)
        except Exception:
            pass

    logger.success(f"Channel profile setup complete for '{channel_key}'! Cookies are permanently saved.")
    return True

def auto_detect_channel(video_name_or_subject: str) -> str:
    """
    Smart Channel Router:
    Automatically analyzes the video filename or topic and routes it to the matching channel.
    Matches against channel niche, keywords, and channel key names.
    """
    channels = load_channels()
    if not channels:
        return ""

    text = video_name_or_subject.lower().replace("_", " ").replace("-", " ")

    # Pre-defined domain keyword dictionaries
    niche_keywords = {
        "psychology": [
            "depression", "anxiety", "neurobiology", "brain", "mind", "mental",
            "psychology", "adhd", "dopamine", "serotonin", "habit", "trauma",
            "stress", "sleep", "healing", "therapy", "emotion", "loneliness"
        ],
        "trading": [
            "trading", "stock", "market", "finance", "money", "crypto", "bitcoin",
            "investing", "share", "forex", "candlestick", "nifty", "sensex",
            "profit", "loss", "portfolio", "wealth", "business", "scalping"
        ],
        "technology": [
            "tech", "ai", "python", "software", "code", "coding", "gadget",
            "computer", "machine learning", "hardware", "cyber", "robot",
            "transformer", "attention", "neural", "deep learning", "agent",
            "swarm", "nvidia", "blackwell", "b200", "cuda", "gpu", "semiconductor",
            "compute", "model", "deepseek", "rag", "vector", "alignment", "dpo",
            "rlhf", "asml", "euv", "chinchilla", "scaling", "alphafold",
            "quantization", "triton", "compiler", "photonic", "optical",
            "multimodal", "robotics", "humanoid", "sovereign", "superintelligence",
            "agi", "synthetic data", "reasoning", "jepa"
        ],
        "science": [
            "science", "space", "physics", "universe", "nasa", "planet",
            "quantum", "biology", "chemistry", "evolution", "dna"
        ]
    }

    # 1. Exact match on channel keys (e.g. "trading" or "psychology" in filename)
    for ch_key, ch_info in channels.items():
        clean_key = ch_key.lower().replace("channel_", "")
        if clean_key in text:
            return ch_key

    # 2. Score based on niche keywords
    scores = {ch_key: 0 for ch_key in channels}
    for ch_key, ch_info in channels.items():
        ch_niche = ch_info.get("niche", "").lower()
        # Direct niche match
        if ch_niche in text:
            scores[ch_key] += 5

        # Check keyword matches
        kws = niche_keywords.get(ch_niche, [])
        for kw in kws:
            if kw in text:
                scores[ch_key] += 2

        # Check channel name match
        ch_name_words = ch_info.get("name", "").lower().split()
        for w in ch_name_words:
            if len(w) > 3 and w in text:
                scores[ch_key] += 1

    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0:
        logger.info(f"🎯 Smart Auto-Route: Matched '{video_name_or_subject}' to '{best_match}' (Score: {scores[best_match]})")
        return best_match

    # Fallback to the first configured channel if no specific keyword matched
    return list(channels.keys())[0]

if __name__ == "__main__":
    channels = load_channels()
    print("Registered Channels:")
    for k, v in channels.items():
        print(f" - {k}: {v['name']} (Niche: {v['niche']})")
