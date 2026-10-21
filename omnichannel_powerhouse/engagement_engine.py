"""
OmniChannel Engagement & Playlist Engine
Powers the Viral Binge-Watching Flywheel:
1. Generates High-IQ Pinned Debate Comments to multiply viewer engagement
2. Assigns videos to Curated Master Series Playlists to maximize session watch time
3. Auto-formats Call-to-Actions for maximum subscriber conversion
"""

import os
import sys
import json
from typing import Dict, Any, List

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("engagement_engine")

PLAYLIST_TAXONOMY = {
    "tech": {
        "title": "The Frontier AI & Silicon Compute Masterclass",
        "description": "An exhaustive, granular investigation into transformer architecture, TSMC photolithography, GPU memory walls, and autonomous agent swarms."
    },
    "finance": {
        "title": "Wall Street Quantitative Finance & Market Microstructure",
        "description": "Deconstructing dark pools, high-frequency microwave networks, payment for order flow, zero-DTE options, and systemic sovereign debt contagion."
    },
    "space": {
        "title": "Orbital Infrastructure & Deep Space Propulsion",
        "description": "Engineering Starship cryogenic orbital refueling, Hall effect ion thrusters, relativistic kinetics, and space-based solar power beaming."
    },
    "biotech": {
        "title": "Synthetic Biology, AlphaFold & Genetic Frontiers",
        "description": "Granular analysis of CRISPR-Cas9 base editing, molecular evolution, mRNA lipid nanoparticles, and epigenetic cellular reprogramming."
    }
}


def generate_pinned_comment(title: str, niche: str = "tech", channel_handle: str = "@GetNeuralStack") -> str:
    """
    Generates a high-IQ, debate-provoking pinned comment designed to trigger comment section velocity.
    """
    if "dark pool" in title.lower() or "hft" in title.lower() or "wall street" in title.lower():
        debate_hook = "Do you believe the rise of off-exchange dark pool crossing networks and sub-millisecond HFT arbitrage has permanently eliminated true price discovery on public exchanges?"
    elif "blackwell" in title.lower() or "nvidia" in title.lower() or "tsmc" in title.lower() or "chip" in title.lower():
        debate_hook = "As TSMC approaches the physical limits of 2nm GAAFET nanosheets, will ASML High-NA lithography and CoWoS packaging be enough to sustain Moore's Law for another decade?"
    elif "transformer" in title.lower() or "attention" in title.lower() or "ai" in title.lower():
        debate_hook = "Do you think quadratic attention complexity will inevitably force the industry to abandon pure Transformers in favor of State Space Models like Mamba, or will FlashAttention keep Transformers dominant?"
    else:
        debate_hook = f"What is your technical perspective on the future implications of {title}? Which institutional players will capture the most value over the next 5 years?"

    comment = f"""💬 [COMMUNITY RESEARCH DEBATE]:
{debate_hook}

Share your technical analysis in the comments below—the most insightful perspectives will be featured in our upcoming episode.

📌 Binge the complete documentary playlist here: https://youtube.com
🔔 Subscribe to {channel_handle} for weekly institutional deep-dive masterclasses."""

    return comment.strip()


def get_curated_playlist(niche: str = "tech") -> Dict[str, str]:
    """Returns the dedicated playlist title and description for this niche."""
    clean_niche = niche.lower()
    for key, data in PLAYLIST_TAXONOMY.items():
        if key in clean_niche:
            return data
    return PLAYLIST_TAXONOMY["tech"]


if __name__ == "__main__":
    c = generate_pinned_comment("The Silicon Monopoly: Nvidia B200 Blackwell & The AI Compute War", "tech", "@GetNeuralStack")
    print("Sample Pinned Comment:\n", c)
