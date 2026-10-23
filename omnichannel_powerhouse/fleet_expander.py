"""
Fleet Expander: Provision 100 YouTube + 100 Rumble Channels Architecture
========================================================================
Populates channels_registry.json, yt_uploader/channels_config.json, and
yt_uploader/rumble_config.json across the 10 Master Niche Clusters.
"""

import os
import sys
import json

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_CONFIG = os.path.join(_root, "yt_uploader", "channels_config.json")
RUMBLE_CONFIG = os.path.join(_root, "yt_uploader", "rumble_config.json")
REGISTRY_PATH = os.path.join(_root, "omnichannel_powerhouse", "channels_registry.json")

CLUSTERS = [
    {
        "id": "c01_ai",
        "niche": "tech",
        "lang": "en",
        "voice": "en-US-ChristopherNeural",
        "prefix": "NeuralStack",
        "keywords": ["transformer", "llm", "neural network", "compute war", "gpu"]
    },
    {
        "id": "c02_semis",
        "niche": "tech",
        "lang": "en",
        "voice": "en-US-ChristopherNeural",
        "prefix": "SiliconFoundry",
        "keywords": ["asml", "tsmc", "lithography", "euv", "semiconductor", "cleanroom"]
    },
    {
        "id": "c03_quant",
        "niche": "finance",
        "lang": "en",
        "voice": "en-US-ChristopherNeural",
        "prefix": "SiliconPulse",
        "keywords": ["dark pool", "high frequency trading", "order flow", "hedge fund", "liquidity"]
    },
    {
        "id": "c04_macro",
        "niche": "finance",
        "lang": "en",
        "voice": "en-US-BrianNeural",
        "prefix": "SovereignMacro",
        "keywords": ["federal reserve", "treasury auctions", "repo market", "petrodollar", "debt"]
    },
    {
        "id": "c05_space",
        "niche": "science",
        "lang": "en",
        "voice": "en-US-EricNeural",
        "prefix": "OrbitalDeep",
        "keywords": ["starship", "ion propulsion", "deep space", "astronomy", "three body"]
    },
    {
        "id": "c06_cyber",
        "niche": "cybersecurity",
        "lang": "en",
        "voice": "en-US-GuyNeural",
        "prefix": "ZeroDayFiles",
        "keywords": ["zero day", "stuxnet", "scada", "cryptography", "exploit"]
    },
    {
        "id": "c07_energy",
        "niche": "energy",
        "lang": "en",
        "voice": "en-US-ChristopherNeural",
        "prefix": "AtomicHorizon",
        "keywords": ["nuclear fusion", "smr", "geothermal", "grid inertia", "tokamak"]
    },
    {
        "id": "c08_biotech",
        "niche": "biotech",
        "lang": "en",
        "voice": "en-US-JennyNeural",
        "prefix": "BioSynthetic",
        "keywords": ["crispr", "mrna", "neuralink", "aging", "synthetic chromosome"]
    },
    {
        "id": "c09_robotics",
        "niche": "robotics",
        "lang": "en",
        "voice": "en-US-ChristopherNeural",
        "prefix": "KineticSwarm",
        "keywords": ["humanoid", "actuator", "drone swarm", "slam", "bipedal"]
    },
    {
        "id": "c10_hindi",
        "niche": "hindi_documentary",
        "lang": "hi",
        "voice": "hi-IN-MadhurNeural",
        "prefix": "BharatTechVault",
        "keywords": ["monopoly hindi", "asml hindi", "tech war india", "case study", "dark pools"]
    }
]


def expand_empire_fleet():
    yt_channels = {}
    rumble_channels = {}
    registry_channels = {}

    ch_num = 1
    for cluster in CLUSTERS:
        for idx in range(1, 11):
            ch_key = f"yt_ch_{ch_num:03d}"
            rm_key = f"rumble_ch_{ch_num:03d}"
            name = f"{cluster['prefix']} {idx:02d}"

            # YouTube Channel Config
            yt_profile = os.path.join(_root, "yt_uploader", "profiles", f"channel_{ch_num:03d}")
            yt_channels[ch_key] = {
                "channel_id": ch_key,
                "name": name,
                "platform": "youtube",
                "niche": cluster["niche"],
                "cluster_id": cluster["id"],
                "language": cluster["lang"],
                "voice_preferred": cluster["voice"],
                "profile_dir": yt_profile,
                "daily_max_uploads": 3,
                "visibility": "unlisted",
                "keywords": cluster["keywords"]
            }

            # Rumble Mirror Channel Config
            rm_profile = os.path.join(_root, "yt_uploader", "profiles_rumble", f"rumble_{ch_num:03d}")
            rumble_channels[rm_key] = {
                "channel_id": rm_key,
                "name": f"{name} (Rumble)",
                "platform": "rumble",
                "niche": cluster["niche"],
                "cluster_id": cluster["id"],
                "language": cluster["lang"],
                "voice_preferred": cluster["voice"],
                "profile_dir": rm_profile,
                "daily_max_uploads": 10,
                "license": "rumble_only",
                "youtube_mirror_target": ch_key
            }

            # Registry Data
            registry_channels[ch_key] = {
                "channel_id": ch_key,
                "platform": "youtube",
                "name": name,
                "niche": cluster["niche"],
                "language": cluster["lang"],
                "voice_preferred": cluster["voice"],
                "profile_dir": yt_profile,
                "daily_max_uploads": 3,
                "uploads_today": 0,
                "last_upload_timestamp": "",
                "auto_publish_visibility": "unlisted"
            }
            registry_channels[rm_key] = {
                "channel_id": rm_key,
                "platform": "rumble",
                "name": f"{name} (Rumble)",
                "niche": cluster["niche"],
                "language": cluster["lang"],
                "voice_preferred": cluster["voice"],
                "profile_dir": rm_profile,
                "daily_max_uploads": 10,
                "uploads_today": 0,
                "last_upload_timestamp": "",
                "auto_publish_visibility": "unlisted"
            }

            ch_num += 1

    # Preserve existing custom channels if any
    if os.path.exists(YT_CONFIG):
        try:
            curr = json.load(open(YT_CONFIG, "r", encoding="utf-8"))
            for k, v in curr.items():
                if k not in yt_channels:
                    yt_channels[k] = v
                    registry_channels[k] = v
        except Exception:
            pass

    # Save to disk
    with open(YT_CONFIG, "w", encoding="utf-8") as f:
        json.dump(yt_channels, f, indent=2)

    with open(RUMBLE_CONFIG, "w", encoding="utf-8") as f:
        json.dump(rumble_channels, f, indent=2)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump({"channels": registry_channels, "updated_at": "2026-10-23 19:00:00", "version": "2.0.0"}, f, indent=2)

    print(f"SUCCESS: Provisioned {len(yt_channels)} YouTube Channels and {len(rumble_channels)} Rumble Channels across 10 Master Clusters!")


if __name__ == "__main__":
    expand_empire_fleet()
