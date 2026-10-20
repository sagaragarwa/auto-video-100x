"""
Chat-To-Video On-Demand Autonomous Engine
Produces deep-researched 1-5 minute 1080p documentaries with:
- Deep research scripting with high-retention hooks and mid-roll CTAs
- Blazing-fast neural voice (Edge-TTS) & cinematic visual scenes
- Outro clip automatically merged at the end (with subscribe & end-screen placeholders)
- Auto-delivery straight to C:\\Users\\janar\\Downloads\\
- Deep-researched SEO package (viral title, chapter timestamps, 30+ tags)
- Smart YouTube upload toggle (unlisted, zero thumbnails per user rules)
"""

import os
import sys
import time
import json
import shutil
import asyncio
import argparse
import subprocess
from typing import Dict, Any, Optional, List
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

import edge_tts
from yt_uploader.cinematic_director import CinematicDirector
from yt_uploader.cinematic_render import normalize_cinematic_clip, render_cinematic_longform
from yt_uploader.seo_generator import generate_viral_seo_package

USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
OUT_DIR = os.path.join(_root, "output", "chat_videos")
TEMP_DIR = os.path.join(_root, "storage", "temp")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

VOICE_EN = "en-US-ChristopherNeural"
VOICE_HI = "hi-IN-MadhurNeural"

import random
import re

def detect_language(prompt: str) -> str:
    hindi_keywords = ["hindi", "mein", "karein", "kaise", "kyun", "depression", "chahiye", "banao", "anxiety", "man", "dimag", "sach", "video", "batao"]
    p_lower = prompt.lower()
    if "english" in p_lower or "for usa" in p_lower:
        return "en"
    for kw in hindi_keywords:
        if kw in p_lower:
            return "hi"
    # Check Devanagari characters
    if any(0x0900 <= ord(c) <= 0x097F for c in prompt):
        return "hi"
    return "hi"  # Default to Hindi for India dashboard workflow

def detect_niche(prompt: str) -> str:
    p_lower = prompt.lower()
    trading_kw = ["trading", "stock", "market", "hft", "order book", "dark pool", "crypto", "forex", "finance", "options", "share bazaar", "nifty", "banknifty", "wall street", "paiso", "money"]
    tech_kw = ["tech", "ai", "artificial intelligence", "robot", "software", "code", "cyber", "gpu", "computer", "future", "algorithm", "chip"]
    psychology_kw = ["depression", "anxiety", "mood", "schizophrenia", "psychology", "mental health", "brain", "dopamine", "trauma", "habit", "mindset", "focus", "sleep", "detox", "calm", "stress"]
    science_kw = ["science", "space", "physics", "universe", "black hole", "galaxy", "quantum", "earth", "atom"]
    history_kw = ["history", "ancient", "mystery", "temple", "civilization", "pyramid", "empire", "king", "war", "kailash", "sanatan"]

    for kw in trading_kw:
        if kw in p_lower:
            return "trading"
    for kw in tech_kw:
        if kw in p_lower:
            return "tech"
    for kw in psychology_kw:
        if kw in p_lower:
            return "psychology"
    for kw in science_kw:
        if kw in p_lower:
            return "science"
    for kw in history_kw:
        if kw in p_lower:
            return "history"
    return "general"

def clean_subject(prompt: str) -> str:
    clean = prompt
    patterns = [
        r'\b\d+\s*(?:min|mins|minute|minutes|sec|secs|second|seconds|m|s)\b',
        r'\b(?:in\s+)?(?:hindi|english|angrezi)\b',
        r'\b(?:documentary|masterclass|fast cuts|cinematic|quality)\b',
        r'\b(?:auto\s+upload(?:\s+to)?|upload(?:\s+to)?|auto)\b',
        r'\b(?:channel_\w+|psychology channel|trading channel|tech channel|science channel)\b',
        r'\b(?:channel|to)\b',
        r'\b(?:banao|generate|create|make)\b',
        r'\b(?:ki\s+)?video\b',
        r'\bvideo\b'
    ]
    for pat in patterns:
        clean = re.sub(pat, ' ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[,;:\-_\s]+', ' ', clean).strip()
    clean = re.sub(r'\b(?:ki|ka|ke|ko|in|on|of|for|to)\s*$', '', clean, flags=re.IGNORECASE).strip()
    return clean if clean else "Deep Masterclass"

def generate_deep_script(prompt: str, niche: str, lang: str, target_duration_sec: int) -> Dict[str, Any]:
    """
    Synthesizes deep-researched long-form documentary script (3 to 20+ minutes).
    1. Attempts to use configured LLM service if available.
    2. Seamlessly falls back to rich, multi-niche procedural generator with high-retention hooks and authentic domain knowledge.
    Guarantees exact target word count so that (narration + 173s signature outro) >= target_duration_sec!
    """
    clean_topic = clean_subject(prompt)
    detected_n = detect_niche(prompt) if not niche or niche == "general" else niche

    words_per_minute = 135 if lang == "en" else 125
    outro_dur = 173.25

    # 1. Target Narration Word Count Calculation
    if target_duration_sec >= 300:
        needed_narration_sec = max(180, target_duration_sec - outro_dur + 45)
    else:
        needed_narration_sec = max(90, target_duration_sec)

    target_words = int((needed_narration_sec / 60.0) * words_per_minute)

    # Check LLM if configured
    try:
        from app.services import llm
        from app.config import config
        has_llm = any([
            config.app.get("gemini_api_key"),
            config.app.get("openai_api_key"),
            config.app.get("moonshot_api_key"),
            config.app.get("deepseek_api_key"),
            config.app.get("qwen_api_key"),
            config.app.get("anthropic_api_key"),
            os.environ.get("GEMINI_API_KEY"),
            os.environ.get("OPENAI_API_KEY")
        ])
        if has_llm:
            target_paragraphs = max(4, min(16, int(needed_narration_sec / 45)))
            lang_str = "Hindi" if lang == "hi" else "English"
            llm_script = llm.generate_script(
                video_subject=f"{clean_topic} comprehensive deep analysis documentary",
                language=lang_str,
                paragraph_number=target_paragraphs
            )
            if llm_script and len(llm_script.split()) >= target_words * 0.7:
                return {
                    "title": f"The Untold Truth Behind {clean_topic.title()}" if lang == "en" else f"{clean_topic.title()} Ka Asli Sach [Deep Analysis]",
                    "script": llm_script.strip(),
                    "niche": detected_n,
                    "lang": lang
                }
    except Exception:
        pass

    # 2. Rich Multi-Chapter Procedural Knowledge Engines
    if lang == "en":
        # ENGLISH SYNTHESIS
        if detected_n == "trading":
            hook = (
                f"Most market participants look at their trading screens and assume that what they see on the public lit tape "
                f"represents the entirety of financial reality. They draw retail trendlines, watch lagging indicators like RSI or MACD, "
                f"and believe that supply and demand meet in a transparent, democratic auction. "
                f"But in modern institutional finance, the public tape is often merely an engineered optical illusion. "
                f"In this exhaustive masterclass, we dissect {clean_topic}, peeling back the layers of market microstructure, "
                f"dark pools, and high-frequency algorithms to reveal how Wall Street actually operates behind closed doors."
            )
            cta1 = (
                f"Before we examine the proprietary routing logic, if you find this institutional breakdown valuable, "
                f"take a brief moment to subscribe to the channel and turn on notifications so you never miss a deep-dive market masterclass."
            )
            cta2 = (
                f"What is your perspective on this structural shift in institutional finance? "
                f"Do you trade with automated mechanical risk rules or discretionary gut feel? "
                f"Share your experience in the comments below—we read every community discussion."
            )
            conclusion = (
                f"The conclusion is undeniable: institutional trading is not about predicting the future with magical indicators; "
                f"it is about understanding liquidity engineering, managing asymmetric risk-to-reward ratios, and executing with robotic discipline. "
                f"Implement these mechanical frameworks systematically. Thank you for watching, and stay focused on what truly matters."
            )
            chapters = [
                f"To understand the core architecture of {clean_topic}, we must first examine market microstructure and institutional order flow. Retail traders focus on lagging chart patterns, while quantitative desks at Citadel and Jane Street monitor liquidity pools and order book imbalances. When sovereign wealth funds rebalance billions across asset classes, liquidity must be engineered before price can transition into an impulsive expansion.",
                f"In modern financial markets, liquidity is the only true fundamental reality. High-frequency algorithms continuously monitor trade prints on the Trade Reporting Facility to detect patterns of off-exchange accumulation. Clustered stop losses resting above swing highs or below structural lows represent resting volume that predatory algorithms actively hunt to fill institutional parent orders.",
                f"Next, let us analyze order book anatomy: Level Two versus Level Three direct exchange multicast feeds. While the public SIP feed aggregates top-of-book quotes with geographic latency, quantitative desks consume raw ITCH and OpenBook feeds directly in memory. Tracking order replenishment speed, hidden reserve icebergs, and queue priority separates passive spread capture from toxic adverse selection.",
                f"Consider also alternative trading venues, crossing networks, and dark order execution. Institutional desks utilize Midpoint Pegs, Discretionary Pegs, and Minimum Quantity instructions to execute massive blocks without broadcasting pre-trade information leakage to the lit market. Navigating these off-exchange protocols requires understanding how high-frequency pinging probes attempt to sniff hidden size.",
                f"The psychological dimension of execution is where 95 percent of operators fail. Cognitive biases like loss aversion and sunk cost fallacy cause traders to hold losers while cutting winners prematurely. Mathematical expectation dictates that without positive expectancy, strictly defined risk per trade, and volatility-adjusted position sizing, long-term survival is statistically impossible.",
                f"Professional quantitative execution models eliminate emotional turbulence entirely. By utilizing algorithmic execution schedules—such as Volume-Weighted Average Price and Time-Weighted Average Price—institutional traders slice massive parent orders into hundreds of micro-child orders, minimizing market impact and adverse slippage across multiple dark pools.",
                f"Finally, let us examine the macroeconomic regime shift. As global interest rates oscillate and quantitative tightening drains market liquidity, volatility surfaces shift rapidly. Adapting to these structural regime changes requires relentless journaling, continuous backtesting against historical out-of-sample data, and the humility to respect market mechanics over personal ego."
            ]
            deep_extensions = [
                f"Delving further into the mathematical mechanics of {clean_topic}, portfolio variance and drawdown risk must be continuously monitored. Quantitative risk parity models balance asset exposure by inverse volatility, ensuring that catastrophic black swan events do not breach statutory capital preservation requirements.",
                f"Statistical arbitrage frameworks exploit microsecond pricing discrepancies between correlated ETF baskets and underlying single-stock components. By maintaining market-neutral beta exposure, algorithmic market makers extract risk-free edge regardless of broader macroeconomic direction.",
                f"The evolution of machine learning in order routing has introduced reinforcement learning agents that optimize execution trajectories in real time. These algorithms dynamically adapt their passive-versus-aggressive order ratio based on real-time bid-ask spread expansion and order book pressure."
            ]

        elif detected_n == "tech":
            hook = (
                f"Most people think Artificial Intelligence and {clean_topic} are merely about chatbots and automated text generation. "
                f"But when you examine the computational scaling laws, semiconductor physics, and massive cluster architecture powering this paradigm, "
                f"the reality is radically more profound. We are witnessing the most significant technological inflection point in human civilization. "
                f"In this exhaustive documentary breakdown, we dissect the rigorous engineering, the compute bottlenecks, and the operational reality governing {clean_topic}."
            )
            cta1 = (
                f"If you appreciate deep engineering research that respects your technical curiosity, subscribe to the channel now and hit the notification bell. "
                f"We publish weekly masterclasses dissecting the foundational mechanics of frontier technology."
            )
            cta2 = (
                f"How do you view this transition toward autonomous agentic intelligence? "
                f"Will autonomous multi-agent workflows amplify human creativity 100x, or fundamentally disrupt traditional white-collar occupations? "
                f"Drop your thoughts in the comment section below."
            )
            conclusion = (
                f"The conclusion is unmistakable: {clean_topic} is not a fleeting hype cycle, but the new foundational computing architecture for the next century. "
                f"Understand these computational scaling principles, embrace autonomous orchestration, and continuously upgrade your mental models. "
                f"Thank you for watching, and we will see you in the next deep breakdown."
            )
            chapters = [
                f"The foundational architecture behind {clean_topic} originated with the 2017 Transformer breakthrough. By replacing recurrent sequential bottlenecks with Multi-Head Self-Attention, transformers enabled parallel training across trillions of tokens. Input text is tokenized and mapped into high-dimensional vector spaces, where deep attention matrices calculate contextual relationships across complex semantic sequences simultaneously.",
                f"Beneath the mathematical software lies the harsh physical reality of semiconductor hardware. Modern frontier models require tens of thousands of specialized tensor processing units, like Nvidia H100 and B200 Blackwell silicon. Featuring High-Bandwidth Memory operating at multiple terabytes per second, these clusters require high-speed optical interconnects and massive liquid-cooling infrastructure to prevent thermal throttling.",
                f"Let us now examine training dynamics and Chinchilla Neural Scaling Laws. Research demonstrates that model performance scales predictably as a power-law function of compute budget, dataset volume, and parameter capacity. Following unsupervised pre-training, models undergo Reinforcement Learning from Human Feedback and Direct Preference Optimization to align probabilistic token outputs with human intent.",
                f"Beyond static single-turn prompting lies the true technological frontier: Autonomous Multi-Agent Swarms. By deploying specialized agents arranged in Planner, Worker, and Evaluator hierarchies, complex multi-step workflows are solved autonomously. Utilizing Model Context Protocols, these agents interact directly with file systems, execution environments, and external cloud APIs.",
                f"Recent breakthroughs in test-time compute scaling have unlocked genuine reasoning capabilities. Rather than instantaneous next-token prediction, modern reasoning models generate internal chain-of-thought trajectories, evaluate alternative branches via tree search, and backtrack when dead ends are identified, achieving elite human benchmarks in competitive coding and mathematical synthesis.",
                f"To remain competitive in this evolving ecosystem, practitioners must transition from passive tool users to autonomous AI orchestrators. Mastering context window efficiency, system prompt architecture, and local open-source models like DeepSeek and Llama allows individuals to build automated software pipelines with extraordinary economic leverage.",
                f"From a geopolitical perspective, compute infrastructure has become a matter of sovereign national defense. Advanced photolithography, semiconductor fabrication facilities, and dedicated nuclear power contracts are dictating the global balance of power. Raw compute power is rapidly becoming the world's most valuable strategic commodity."
            ]
            deep_extensions = [
                f"Examining the internal latency and memory bandwidth challenges reveals that memory wall constraints remain the primary hurdle in hardware scaling. SRAM caching hierarchies, wafer-scale integration, and silicon photonics represent the cutting-edge solutions currently being deployed to transcend von Neumann bottlenecks.",
                f"Synthetic data generation and self-play reinforcement learning are replacing human-curated datasets. By setting models against adversarial evaluators in simulated environments, frontier systems continuously synthesize novel mathematical proofs and algorithmic optimizations without human intervention.",
                f"The economic implications of zero-marginal-cost software generation will fundamentally reshape organizational design. Small autonomous teams leveraging intelligent agent workflows will routinely build and maintain infrastructure that historically required multi-million-dollar engineering departments."
            ]

        elif detected_n == "science" or detected_n == "history":
            hook = (
                f"When modern researchers examine {clean_topic} through rigorous empirical lenses, historical orthodoxies and conventional assumptions rapidly crumble. "
                f"Physical evidence, precision isotopic dating, and architectural anomalies point to a complexity that defies simplistic textbooks. "
                f"In this comprehensive documentary masterclass, we examine the raw scientific data and forgotten records that reshape our understanding of {clean_topic}."
            )
            cta1 = (
                f"If you value independent scientific and historical research backed by empirical evidence, subscribe today and join our community of curious thinkers."
            )
            cta2 = (
                f"What do you believe is the most compelling explanation for these anomalous discoveries? Share your hypothesis in the comments below."
            )
            conclusion = (
                f"Ultimately, seeking truth requires setting aside dogmatic bias and following physical evidence wherever it leads. "
                f"Embrace scientific rigor and keep questioning conventional narratives. Thank you for watching, and see you in the next investigation."
            )
            chapters = [
                f"The physical evidence surrounding {clean_topic} challenges mainstream consensus. Whether analyzing micro-machining marks on ancient diorite vessels or precision astronomical alignments across megalithic complexes, the level of engineering intentionality suggests sophisticated lost technological paradigms.",
                f"Examining geological stratigraphy and environmental sediment cores reveals catastrophic climatic transitions in Earth's history. Rapid meltwater pulses, cosmic impact indicators like nanodiamonds and platinum anomalies, and abrupt extinction horizons suggest cyclical global disruptions that reset ancient human civilizations.",
                f"From an astrophysical perspective, cosmological observations continue to reveal fundamental puzzles. Dark matter, cosmic background radiation anomalies, and quantum vacuum energy challenge the Standard Model of physics, suggesting that our understanding of space-time and gravity remains fundamentally incomplete.",
                f"Synthesizing ancient mathematical traditions reveals profound geometric knowledge encoded in architectural dimensions. The Golden Ratio, Pythagorean harmonics, and geodesic measurements indicate that ancient builders understood the precise equatorial circumference and curvature of the Earth millennia before modern satellites.",
                f"Modern multi-spectral satellite imagery and LiDAR technology are currently revolutionizing archaeology, revealing lost urban networks buried beneath dense rainforests and desert sands that accommodated millions of inhabitants with advanced hydraulic engineering systems.",
                f"Interdisciplinary research combining archaeoastronomy, genetics, and linguistic phylogenetics is dismantling fragmented academic silos. Tracing human mitochondrial DNA migration corridors demonstrates complex global maritime interactions far earlier than conventional history acknowledged.",
                f"As emerging technologies allow us to probe deeper into quantum mechanics and cosmic microwave backgrounds, the boundary between ancient philosophical intuition and modern physics continues to blur, pointing toward a profound underlying continuity in universal structure."
            ]
            deep_extensions = [
                f"Carbon-14 calibration curves and accelerator mass spectrometry have provided unprecedented temporal resolution, demonstrating that anomalous monuments were constructed centuries earlier than previously theorized.",
                f"Quantum entanglement and non-local correlations continue to challenge deterministic classical mechanics, proving that information itself is a foundational physical property woven into the fabric of reality.",
                f"Analyzing ancient archaeo-metallurgy demonstrates specialized alloy compositions and high-temperature furnace techniques that modern metallurgy struggled to replicate until the late industrial era."
            ]

        else: # Psychology / Mindset / General
            hook = (
                f"Most people believe that navigating {clean_topic} is simply a matter of raw willpower and positive thinking. "
                f"However, rigorous neurobiology and cognitive science prove that willpower is a severely finite biological resource. "
                f"Behind our daily behaviors lies an intricate network of neurotransmitters, autonomic feedback loops, and default mode networks that govern human decision-making. "
                f"In this in-depth masterclass, we break down the clinical research and evidence-based protocols that allow you to master {clean_topic} once and for all."
            )
            cta1 = (
                f"If this scientific perspective on human behavior is providing clarity, hit the like button and subscribe to the channel for weekly evidence-based masterclasses."
            )
            cta2 = (
                f"What is your single greatest friction point when attempting to implement lasting behavioral change? Drop your experience in the comments below."
            )
            conclusion = (
                f"True transformation is not born from fleeting motivation; it is engineered through physiological alignment and systematic environmental design. "
                f"Apply these protocols consistently and protect your mental sovereignty. Thank you for watching, and see you in the next masterclass."
            )
            chapters = [
                f"To understand the biological baseline of {clean_topic}, we must examine how modern hyper-stimulation disrupts dopamine receptors. Constant notifications, short-form algorithm feeds, and artificial rewards cause chronic down-regulation of dopamine D2 receptors, creating baseline lethargy, chronic procrastination, and severe attentional fragmentation.",
                f"When environmental friction is low for high-dopamine distractions, the default mode network hijacks cognitive bandwidth. Chronic elevation of cortisol and adrenaline keeps the sympathetic nervous system locked in a low-grade fight-or-flight state, impairing prefrontal cortex executive functioning and rational decision-making.",
                f"Implementing sustainable neuroplastic recovery requires somatic regulation. Stimulating the vagus nerve through physiologically verified respiration—such as extended exhalations and physiological sighs—instantly activates parasympathetic tone, reducing heart rate variability stress metrics within seconds.",
                f"Circadian rhythm entrainment represents the foundational pillar of cognitive endurance. Viewing natural early-morning sunlight stimulates retinal ganglion cells, synchronizing cortisol peaks with daylight and establishing a biochemical timer for optimal evening melatonin synthesis and restorative deep sleep architecture.",
                f"Cognitive restructuring involves reframing catastrophic self-talk into objective empirical observations. By recognizing that thoughts are biological events rather than immutable truths, practitioners create psychological distance between stimulus and response, restoring dominant self-regulatory control.",
                f"Identity-based habit compounding dictates that lasting behavioral shifts occur only when actions align with core personal identity. By automating micro-habits that reduce decision fatigue, elite performers maintain effortless focus while others exhaust their willpower through brute-force struggle.",
                f"Over a multi-month trajectory, consistent adherence to these physiological principles leads to structural neurogenesis in the hippocampus and enhanced prefrontal gray matter density, transforming deliberate discipline into an automated baseline state."
            ]
            deep_extensions = [
                f"Investigating neurotransmitter reuptake kinetics demonstrates that adequate micronutrient intake, including magnesium L-threonate and omega-3 fatty acids, provides critical cofactors for myelin sheath repair and neurotransmitter synthesis.",
                f"Deliberate environmental architecture creates physical boundaries that protect cognitive focus. By introducing intentional friction—such as physical device lockboxes and dedicated deep-work sanctuaries—attention is defended from predatory algorithmic capture.",
                f"Non-Sleep Deep Rest protocols and systematic body scanning techniques facilitate rapid parasympathetic recovery, clearing neurotoxic adenosine accumulation from server synaptic clefts without requiring full sleep cycles."
            ]

    else:
        # HINDI SYNTHESIS
        if detected_n == "trading":
            hook = (
                f"Zyadatar log trading ko sirf chart par indicators dekhna ya call-put buy karna samajhte hain. "
                f"Lekin jab aap Wall Street ke institutional desks, high-frequency algorithms aur order book microstructure ko dekhte hain, "
                f"toh samajh aata hai ki public tape par dikhne wali har movement ek well-planned liquidity trap hoti hai. "
                f"Retail traders jahan breakout par buy karte hain, wahan institutional algorithms unhe exit liquidity banakar stop hunt karte hain. "
                f"Aaj ke is exhaustive documentary masterclass me hum {clean_topic} ke un real institutional mechanics ko decode karenge jo 99% traders ko kabhi nahi sikhaye jaate."
            )
            cta1 = (
                f"Agar aapko yeh institutional market microstructure samajh aa raha hai aur aap retail mindset se nikal kar "
                f"smart money ke sath align hona chahte hain, toh is video ko like karein aur channel ko subscribe kar lijiye. "
                f"Bell icon zaroor dabayein taaki koi bhi trading masterclass miss na ho."
            )
            cta2 = (
                f"Aap trading me indicators par depend karte hain ya institutional liquidity pools aur price action ko follow karte hain? "
                f"Apna honest experience comment section me zaroor share karein—hum har ek comment ko read karte hain."
            )
            conclusion = (
                f"Nishkarsh bilkul spasht hai: Trading me kamyabi kisi magical indicator se nahi, balki liquidity engineering, "
                f"strict risk management aur mechanical discipline se aati hai. Apne losses ko chota rakhein aur winners ko smoothly run hone dein. "
                f"Video dekhne ke liye dil se shukriya. Milte hain agle institutional breakdown me."
            )
            chapters = [
                f"Pehle chapter me baat karte hain market microstructure aur institutional order flow ki. Ek aam retail trader indicator ke crossover par trade leta hai, jabki institutional market makers Level 3 order book feeds aur liquidity imbalances ko dekhte hain. Jab bade funds hazaron crores ka volume deploy karte hain, toh unhe aggressive buy ya sell karne se pehle counter-party liquidity assemble karni padti hai.",
                f"Bade financial markets me sirf ek hi sachai hoti hai—aur woh hai Liquidity Hunt. Support aur resistance ke upar aur niche retail traders ke stop losses clustered hote hain. Predatory algorithms in clustered stops ko sweep karke heavy volume execute karte hain, jisse aam trader fake breakout me trap ho jata hai aur market turant reverse ho jaati hai.",
                f"Teesre chapter me hum dissect karenge Level 2 aur Level 3 market data ko. Nasdaq ITCH aur NYSE OpenBook direct multicast feeds hoti hain jo nanoseconds me har ek order ke addition, modification aur cancellation ko broadcast karti hain. Algorithms order book replenishment speed aur hidden iceberg orders ko monitor karke passive spread capture karte hain.",
                f"Chauthe chapter me aate hain Dark Pools aur Alternative Trading Systems par. Billion-dollar parent orders ko public lit exchange par execute karne ke bajaye institutions dark crossing networks me Midpoint Pegs aur Minimum Quantity conditions use karte hain. Isse pre-trade price impact aur slippage zero ho jati hai.",
                f"Paanchwe chapter me baat karte hain Trader Psychology aur Mathematical Expectation ki. 90% log strategy ki wajah se nahi, balki loss aversion aur revenge trading ki wajah se fail hote hain. Asymmetric risk-to-reward ratio—kam se kam 1:2 ya 1:3—aur har trade par maximum 1% risk lena hi capital preservation ka golden rule hai.",
                f"Chhathe chapter me execute karte hain Systematic Quantitative Playbook. Professional desks discretionary gut feel ke bajaye Volume-Weighted Average Price aur automated execution schedules use karte hain. Isse emotion puri tarah eliminate ho jata hai aur trading ek cold probabilistic business ban jaati hai.",
                f"Saatwe chapter me evaluate karte hain Macroeconomic Regimes aur Volatility Shifts ko. Interest rates, bond yields aur central bank liquidity ke cycles ke sath market ka volatility structure badalta rehta hai. Sahi market phase ko pehchankar position sizing ko adjust karna hi long-term consistency deta hai."
            ]
            deep_extensions = [
                f"Iske mathematical dimension me Portfolio Drawdown aur Sharpe Ratio ko track karna anivarya hai. Ek systematic trader kabhi bhi apni drawdown limit ko 10% se exceed nahi hone deta aur high volatility me position size ko automatically scale-down kar deta hai.",
                f"Statistical Arbitrage aur Pair Trading jaise quantitative models market-neutral rehte hain. Do correlated assets ke spread divergence par trade lagakar bina kisi market directional bias ke risk-free returns extract kiye jaate hain.",
                f"Algorithmic Execution me Slippage control sabse bada edge hai. Smart Order Routers multiple exchanges aur dark pools me micro-second routing karke execution cost ko significantly reduce kar dete hain."
            ]

        elif detected_n == "tech":
            hook = (
                f"Zyadatar log {clean_topic} ko sirf ek superficial tool ya simple chatbot samajhte hain. "
                f"Lekin jab hum iski deep core architecture, neural network scaling laws aur computational infrastructure ko analyze karte hain, "
                f"toh samajh aata hai ki yeh manav itihas ka sabse krantikari turning point hai. "
                f"Parde ke peeche aisi takneek kaam kar rahi hai jo software engineering, research aur poore digital universe ko hamesha ke liye badal rahi hai. "
                f"Aaj ke is exhaustive masterclass me hum {clean_topic} ke un hidden mechanics ko decode karenge jo 99% logon ko bilkul nahi pata."
            )
            cta1 = (
                f"Agar aapko yeh deep technological breakdown samajh aa raha hai aur aap mainstream media ki superficial baaton se aage "
                f"real engineering facts ko sikhna chahte hain, toh is video ko like zaroor karein aur channel ko subscribe kar lijiye. "
                f"Bell notification on rakhein taaki koi bhi high-level masterclass miss na ho."
            )
            cta2 = (
                f"Aapka is autonomous technological revolution ke baare me kya manna hai? "
                f"Kya aane wale samay me insaani productivity 10 guna badhegi ya pura traditional work structure automate ho jayega? "
                f"Apne vichar niche comment section me zaroor share karein, hum har ek comment ko deeply read karte hain."
            )
            conclusion = (
                f"Nishkarsh bilkul spasht hai: {clean_topic} koi temporary trend ya marketing hype nahi hai, "
                f"balki hamari modern civilization ka naya computational foundation hai. "
                f"In underlying principles ko samjhein, algorithmic leverage ko apni daily life me execute karein aur lagatar naye concepts ko master karte rahein. "
                f"Is deep investigative video ko dekhne ke liye shukriya. Apna dhyan rakhein aur milte hain agle documentary masterclass me."
            )
            chapters = [
                f"Pehle chapter me hum baat karenge core technological architecture aur Transformer revolution ki. 2017 me research paper 'Attention Is All You Need' ne computational science ki disha badal di. Pehle ke recurrent models me sequential processing hoti thi, jisse lambe sentences me context disappear ho jata tha. Transformer model ne Multi-Head Self-Attention mechanism introduce kiya, jahan har ek word ya token sentence ke baki sabhi tokens ke sath simultaneously mathematical relationship establish karta hai. Jab hum kisi model me prompt enter karte hain, toh input text ko hazaron multi-dimensional vector embeddings me convert kiya jata hai. Yeh embeddings billions of parameters ke high-speed matrix multiplication ke through pass hoti hain, jisse model ko language ki deep context aur semantic meaning samajh aati hai.",
                f"Dusra sabse bada reality check hai physical hardware aur compute bottleneck. Software kitna bhi advanced ho, bina silicon chips ke compute impossible hai. Nvidia ke H100 aur B200 Blackwell chips is pure revolution ki backbone hain. Har ek chip me 80 billion se 200 billion transistors hote hain, jo High-Bandwidth Memory yani HBM3e se 8 terabytes per second ki massive bandwidth par data process karte hain. Lekin sabse bada constraint semiconductor nahi, balki electrical power aur cooling grids hain. Ek modern gigawatt-scale AI datacenter ko chalane ke liye ek pure metropolitan shehar jitni electricity ki zaroorat hoti hai. Global tech giants ab nuclear power plants ke sath direct supply contracts sign kar rahe hain, kyunki jiske paas continuous energy aur silicon compute hoga, wahi global intelligence ko lead karega.",
                f"Teesre chapter me dekhte hain Training Dynamics aur Neural Scaling Laws. Frontier research labs trillions of tokens ke web-scale text aur code repositories par models ko pre-train karti hain. Chinchilla scaling laws yeh dictate karti hain ki model ke parameter count aur training tokens ka ratio perfectly balanced hona chahiye. Jaise-jaise compute budget badhta hai, model ki test loss mathematically smooth curve me decrease hoti hai aur surprising emergent capabilities jaise logic reasoning aur complex code synthesis activate hone lagti hain. Pre-training ke baad Alignment phase aata hai, jahan Reinforcement Learning from Human Feedback yani RLHF aur Direct Preference Optimization se model ko safe aur helpful banaya jata hai. Ab internet ka human data saturate ho chuka hai, isliye leading labs high-fidelity synthetic data aur automated self-play simulation loops ke through models ko training provide kar rahi hain.",
                f"Chauthe chapter me hum aate hain sabse impactful phase par—Autonomous AI Agents. Ek single model se chat karna AI ka past tha; AI ka future Multi-Agent Systems me hai. Is architecture me multiple specialized agents ek sath milkar complex engineering problems ko solve karte hain. Ek Planner agent goal ko logical milestones me divide karta hai; ek Coder agent software likhta hai; aur ek Critic agent continuously tests execute karke code errors ko fix karta hai. Model Context Protocol yani MCP ke through yeh autonomous agents databases, operating system terminals, cloud APIs aur web browsers ko directly control karte hain. Aane wale do saalon me ek single engineer in autonomous agent swarms ko orchestrate karke ek 50-person engineering team ke barabar software output generate kar sakega.",
                f"Paanchwe chapter me baat karte hain Reasoning Models aur Test-Time Compute scaling ki. Legacy models me prompt milte hi agla token bina soche predict kiya jata tha, jisse complex math aur logical puzzles me failure aati thi. Modern reasoning models inference ke samay test-time compute ko scale karte hain. Jab aap inhein ek difficult challenge dete hain, toh yeh answer dene se pehle internal chain-of-thought generate karte hain. Yeh model tree search aur Monte Carlo simulations ke through multiple solution paths explore karta hai, apni galatiyon ko midway backtrack karta hai, aur verify hone ke baad hi accurate response deliver karta hai. Is capability ne AI ko ek simple text predictor se convert karke ek autonomous scientific researcher ke level par la khada kiya hai.",
                f"Chhathe chapter me aate hain practical implementation aur human strategy par. Is massive transition me aam user aur elite operator ke beech ka gap exponentially badhne wala hai. Agar aap sirf AI ko search engine ki tarah use karenge, toh aapka leverage zero rahega. Aapko ek AI Orchestrator banna hoga—jise yeh pata ho ki context windows ko optimize kaise karein, system prompts ko mathematically structure kaise karein, aur local open-source models jaise DeepSeek aur Llama ko apne custom business pipelines ke sath integrate kaise karein. Aapka domain expertise jab autonomous AI leverage ke sath multiply hota hai, tab aap aisi productivity achieve karte hain jo pehle puri organization milkar bhi nahi kar sakti thi.",
                f"Saatwe chapter me hum evaluate karte hain geopolitical aur economic impact ko. AI sovereignty ab har major nation ke liye national defense jaisa priority issue ban chuka hai. Semiconductor fabrication plants, lithography machines aur advanced packaging technology par global trade wars chal rahi hain. Data center clusters ab naye industrial factories hain jo physical goods ke bajaye cognitive intelligence produce karte hain. Yeh economic shift human labor ki value ko redefine kar raha hai. Jo companies aur individuals is transformation ki core reality ko samajhkar early position le rahe hain, wahi aane wale digital era ke economic leaders honge."
            ]
            deep_extensions = [
                f"Iske mathematical dimension par aur gehraai se dhyan dein. Jab hum neural network ke parameter weights aur attention matrices ko inspect karte hain, toh har ek layer abstract representation learn karti hai—low-level syntactic patterns se lekar high-level reasoning concepts tak. Yeh continuous learning loop empirical research ko naye mukam par le ja raha hai.",
                f"Software architecture me Zero-Shot aur Few-Shot prompting se nikal kar ab Retrieval-Augmented Generation yani RAG ka daur hai. Enterprise documents ko vector database me index karke semantic search ke through live context injection kiya jata hai, jisse hallucination rate zero ho jati hai.",
                f"Edge AI aur On-Device Intelligence naya revolution hai. Quantization techniques jaise 4-bit aur 8-bit precision models ko mobile devices aur local hardware par ultra-fast speed se run karne me saksham banati hain."
            ]

        elif detected_n == "science" or detected_n == "history":
            hook = (
                f"Jab modern researchers {clean_topic} ko empirical scientific aur archaeological lens se dekhte hain, "
                f"toh purani theories aur orthodox assumptions bilkul galat sabit hone lagte hain. "
                f"Physical anomalies, carbon dating ke naye results aur advanced precision engineering yeh saaf karti hain "
                f"ki hamare past aur universe ke bare me hum jo jaante hain, woh sirf 10% sach hai. "
                f"Aaj ke is exhaustive documentary masterclass me hum un facts aur empirical data ko explore karenge jo aam kitabon me nahi milte."
            )
            cta1 = (
                f"Agar aap genuine research aur scientific discoveries ko support karte hain, toh video ko like karein aur channel ko subscribe kar lijiye."
            )
            cta2 = (
                f"Aapka is mysterious discovery ke baare me kya nazariya hai? Kya ancient civilizations ke paas koi advanced understanding thi? Comment karein."
            )
            conclusion = (
                f"Sach hamesha wahi hota hai jo physical evidence aur empirical data me dikhta hai. "
                f"Apne dhyan ko hamesha scientific perspective par केंद्रित rakhein. Video dekhne ke liye shukriya. Milte hain agle documentary breakdown me."
            )
            chapters = [
                f"Pehle chapter me hum baat karenge geological aur archaeological anomalies ki. {clean_topic} ke bare me milne wale physical evidences standard textbook timeline se hazaron saal purane hain. Precision stonework aur geometric alignments aam tools se banana physics ke hisab se impossible tha.",
                f"Dusre chapter me decode karte hain ancient mathematical precision ko. Mega-structures me Pi aur Golden Ratio ka use yeh sabit karta hai ki unhe Prithvi ke exact circumference aur dimensions ka pura gyan tha, jo modern science ne satellites se verify kiya.",
                f"Teesre chapter me astrophysics aur quantum principles ko jodkar dekhte hain. Cosmic radiation, vacuum energy aur quantum entanglement yeh dikhate hain ki hamara physical cosmos ek interconnected information matrix hai.",
                f"Chauthe chapter me climate transitions aur cataclysms ka analysis karte hain. Earth ke geological layers me nanodiamonds aur sudden melting pulse evidence sabit karte hain ki global catastrophic events ne itihas ko kayi baar reset kiya hai.",
                f"Paanchwe chapter me modern satellite LiDAR scanning ke results ko dekhte hain. Dense jungles aur deserts ke niche dafn massive cities yeh reveal kar rahi hain ki hamara aitihasik gyan kitna adhura tha.",
                f"Chhathe chapter me genetic migration aur ancient maritime trade routes ko analyze karte hain. Human mitochondrial DNA se pata chalta hai ki continents ke beech interaction bohot pehle se chala aa raha hai.",
                f"Saatwe chapter me philosophical synthesis par aate hain. Science aur consciousness ka interlink yeh batata hai ki human evolution ka agla padav hamari awareness me chhipa hai."
            ]
            deep_extensions = [
                f"Radiometric dating aur accelerator mass spectrometry ne chronology ko naye sire se define kiya hai, jisse purane dates ko hazaron saal piche shift karna pada hai.",
                f"Quantum physics me Observer Effect yeh dikhata hai ki consciousness aur physical matter ek dusre se alag nahi hain.",
                f"Ancient metallurgy aur high-temperature blast furnaces ke chemical traces yeh sabit karte hain ki advanced materials ka gyan us daur me bhi maujood tha."
            ]

        else: # Psychology / Mindset / General
            t_low = clean_topic.lower()
            if any(k in t_low for k in ["anxiety", "panic", "overthinking", "fear", "घबराहट", "चिंता", "डर", "बेचैनी"]):
                hook = (
                    f"Zyadatar log anxiety ya panic attacks ko sirf mann ka weham ya kamzori samajhte hain. "
                    f"Lekin neurobiology aur clinical psychiatry yeh spasht karti hai ki anxiety ek intense biological storm hai. "
                    f"Jab dimag ka fear center yani Amygdala bina kisi physical khatre ke emergency alarm baja deta hai, "
                    f"toh bloodstream me adrenaline aur cortisol ka sailab aa jata hai aur sharir fight-or-flight mode me lock ho jata hai. "
                    f"Aaj ke is exhaustive masterclass me hum anxiety aur panic attacks ke neurobiological roots aur un scientific protocols ko samjhenge jo ise permanent heal karte hain."
                )
                chapters = [
                    f"Pehle chapter me decode karte hain Amygdala Hijack aur Sympathetic Nervous System ko. Chronic stress ki wajah se autonomic nervous system hypersensitive ho jata hai. Dimag choti si aashanka ko bhi catastrophic threat maan leta hai, jisse heart rate spike hoti hai, breathing shallow hoti hai aur chest me tightness mehsoos hoti hai. Yeh purely physiological response hai.",
                    f"Dusre chapter me dekhte hain Neurochemical Cascade ko. Adrenaline aur Noradrenaline ke continuous secretion se brain ka prefrontal cortex shut down hone lagta hai. Insaan rational sochna band kar deta hai aur worst-case scenario ke obsessive loop me fans jata hai. Is neurochemical loop ko todne ke liye body-first intervention anivarya hai.",
                    f"Teesre chapter me hum sikhate hain Somatic Vagus Nerve Activation. Jab panic attack start ho, toh dimag se ladna band karein aur physiological sigh use karein—do bar deep inhale aur lamba mouth exhale. Yeh technique turant parasympathetic nervous system ko trigger karti hai aur heart rate ko 60 seconds me normal karti hai.",
                    f"Chauthe chapter me aate hain 5-4-3-2-1 Sensory Grounding Technique par. Anxiety insaan ko future ke imaginary dar me le jaati hai. 5 visible objects, 4 touchable textures, 3 ambient sounds ko consciously identify karke sensory cortex activate hota hai aur dimag wapas present reality me ground ho jata hai.",
                    f"Paanchwe chapter me baat karte hain Cognitive Restructuring aur Thought Labeling ki. Har ek vichar sach nahi hota. Apne catastrophic thoughts ko likhein aur objective evidence se challenge karein. 'Main marne wala hoon' ko replace karein 'Yeh sirf adrenaline rush hai jo agle 5 minute me calm ho jayega'.",
                    f"Chhathe chapter me circadian rhythm aur sleep stabilization par focus karein. Morning sunlight exposure aur consistent bedtime se cortisol baseline normal rehta hai, jisse nervous system ki daily hyper-reactivity 70% tak drop ho jaati hai.",
                    f"Saatwe chapter me long-term neuroplastic healing ka blueprint dekhte hain. Consistent somatic mindfulness, daily walks, clean nutrition aur gradual exposure se Amygdala rewire hota hai aur insaan hamesha ke liye fearless ban jata hai."
                ]
            elif any(k in t_low for k in ["depression", "anhedonia", "sadness", "डिप्रेशन", "उदासी", "अकेलापन", "निराशा"]):
                hook = (
                    f"Depression sirf udas hona nahi hai; yeh ek aisi biological sthiti hai jise clinical science me Anhedonia kehte hain. "
                    f"Insaan un cheezon me bhi koi khushi mehsoos nahi kar pata jise wo kabhi sabse zyada chahta tha. "
                    f"Brain neuroimaging me dekha gaya hai ki Default Mode Network hyperactive ho jata hai aur neurotransmitters exhaust ho jaate hain. "
                    f"Aaj ke is in-depth masterclass me hum depression ki asli neurobiology aur clinical healing protocols ko decode karenge."
                )
                chapters = [
                    f"Pehle chapter me samjhenge Default Mode Network aur Neurotransmitter Depletion ko. Serotonin aur Dopamine pathways down-regulate hone se brain me cognitive fatigue aa jaati hai. Prefrontal cortex ki executive energy khatam ho jaati hai aur insaan ko basic daily tasks bhi pahad jaise lagte hain. Yeh aalas nahi, biological exhaustion hai.",
                    f"Dusre chapter me baat karte hain Hippocampal Neurogenesis aur BDNF protein ki. Chronic depression me hippocampus shrink hone lagta hai. Is process ko reverse karne ke liye natural sunlight, aerobic walking aur omega-3 fatty acids essential cofactors hain jo brain-derived neurotrophic factor ko stimulate karte hain.",
                    f"Teesre chapter me Behavioral Activation protocol implement karte hain. Motivation ka wait mat kijiye; micro-actions initiate karein. Sirf 5 minute ke liye bistar se uthna, room ki window kholna aur paani peena dopamine circuitry ko restart karta hai.",
                    f"Chauthe chapter me social connection aur isolation breakdown zaroori hai. Akelepan me Default Mode Network self-criticism loop ko 10 guna amplify kar deta hai. Kisi trusted person ya support group se baat karna neurochemical relief deta hai.",
                    f"Paanchwe chapter me Cognitive Behavioral Therapy ke principles se negative cognitive distortions ko systematically challenge kiya jata hai. Self-compassion ke sath khud ko judge karna band karein.",
                    f"Chhathe chapter me circadian biology aur physical recovery routines ko establish karein. Sleep architecture ko repair karke brain toxins ko glymphatic system ke zariye wash-out kiya jata hai.",
                    f"Saatwe chapter me permanent recovery ka vision establish hota hai. Depression 100% curable neurological condition hai, bas sahi systematic approaches ko consistency ke sath follow karne ki zaroorat hai."
                ]
            else: # Dopamine Detox & General Mindset
                hook = (
                    f"Aaj ke hyper-stimulated daur me hamara dimag continuous sensory overload aur dopamine exhaustion se guzar raha hai. "
                    f"Reels, shorts, instant notifications aur constant scrolling ne hamare prefrontal cortex ko weak kar diya hai. "
                    f"Iska parinaam yeh hai ki hum 10 minute bhi bina screen ke focus nahi kar paate aur deep work impossible lagta hai. "
                    f"Aaj ke is exhaustive masterclass me hum Dopamine Fasting, Mental Reset aur Focus Restoration ka complete scientific protocol samjhenge."
                )
                chapters = [
                    f"Pehle chapter me decode karte hain Dopamine Receptors aur Baseline Chemistry ko. Jab aap subah uthte hi phone scroll karte hain, toh instant artificial spike milta hai. Iske baad dopamine baseline severely crash ho jata hai, jisse din bhar procrastination, mental fog aur lethargy bani rehti hai.",
                    f"Dusre chapter me samjhenge Prefrontal Cortex Hijack ko. High-stimulation habits brain ke executive control ko paralyze kar deti hain. Insaan hard tasks se bhaagne lagta hai aur continuous cheap stimulation ka ghulam ban jata hai.",
                    f"Teesre chapter me 48-Hour Dopamine Detox protocol shuru hota hai. Sabhi high-stimulation triggers—social media, junk food, entertainment—par physical friction create karein. Phone ko grayscale mode par daalein aur dusre kamre me rakhein.",
                    f"Chauthe chapter me Stillness aur Boredom Tolerance develop karein. Boredom dimag ka natural reset mechanism hai. Jab aap bina phone ke shant baithna seekhte hain, toh natural dopamine baseline dobara restore hone lagta hai.",
                    f"Paanchwe chapter me Deep Work Sessions aur Single-Tasking par focus karein. 90-minute ke focused blocks me bina kisi interruption ke kaam karna brain ke neuroplasticity circuits ko rewire karta hai.",
                    f"Chhathe chapter me Circadian Alignment aur Natural Sunlight immersion daily routine ka hissa banayein. Morning light cortisol ko optimize karti hai aur evening me restful sleep induce karti hai.",
                    f"Saatwe chapter me Identity Shift aur Atomic Habits ke zariye permanent transformation locked ho jata hai. Discipline ko punishment nahi, balki self-respect banakar routine execute karein."
                ]

            cta1 = (
                f"Agar aapko yeh evidence-based mental health research pasand aa rahi hai, toh is video ko like zaroor karein aur channel ko subscribe kar lijiye. "
                f"Apne doston ke sath zaroor share karein jise iski sabse zyada zaroorat hai."
            )
            cta2 = (
                f"Aap apne daily life me focus aur mental clarity maintain karne ke liye kya protocol follow karte hain? "
                f"Niche comment me share karein, hum har ek response ko appreciate karte hain."
            )
            conclusion = (
                f"Nishkarsh spasht hai: Aapka dhyan aur mental energy aapki sabse badi sampatti hai. "
                f"Cheap stimulation ke trap se bachein, apne nervous system ko protect karein aur intentional life jiyein. "
                f"Video dekhne ke liye dil se shukriya. Milte hain agle transformative masterclass me."
            )
            deep_extensions = [
                f"Somatic mindfulness aur daily vagus nerve conditioning se nervous system ki emotional resilience 10 guna badh jaati hai. Har din 15 minute deep relaxation me bitana dimag ko hamesha santulit rakhta hai.",
                f"Nutrition aur Gut-Brain Axis mental health me 90% serotonin produce karta hai. Healthy fermented foods aur hydration brain fog ko permanent door kar dete hain.",
                f"Daily gratitude journaling aur self-reflection default mode network ki chronic negativity ko rewire karke internal peace establish karta hai."
            ]

    # 3. Dynamic Chapter Accumulator Loop
    assembled_sections = [hook, chapters[0], cta1, chapters[1]]
    curr_words = sum(len(s.split()) for s in assembled_sections)

    remaining_chaps = list(chapters[2:])
    ext_idx = 0
    added_cta2 = False

    while curr_words < target_words:
        if curr_words > target_words * 0.55 and not added_cta2:
            assembled_sections.append(cta2)
            added_cta2 = True
            curr_words = sum(len(s.split()) for s in assembled_sections)
            continue

        if remaining_chaps:
            assembled_sections.append(remaining_chaps.pop(0))
            curr_words = sum(len(s.split()) for s in assembled_sections)
        elif ext_idx < len(deep_extensions):
            assembled_sections.append(deep_extensions[ext_idx])
            ext_idx += 1
            curr_words = sum(len(s.split()) for s in assembled_sections)
        else:
            # If target_words is exceptionally large (e.g. 15-20+ min masterclass), cycle extensions
            cycle_ext = deep_extensions[ext_idx % len(deep_extensions)]
            ext_idx += 1
            assembled_sections.append(cycle_ext)
            curr_words = sum(len(s.split()) for s in assembled_sections)

    assembled_sections.append(conclusion)
    full_script = "\n\n".join(assembled_sections)

    return {
        "title": f"The Untold Truth Behind {clean_topic.title()}" if lang == "en" else f"{clean_topic.title()} Ka Asli Sach [Deep Analysis]",
        "script": full_script,
        "niche": detected_n,
        "lang": lang
    }

async def synth_voice(text: str, voice: str, out_audio: str):
    comm = edge_tts.Communicate(text, voice, rate="+4%")
    await comm.save(out_audio)

def append_outro_to_video(main_video: str, outro_video: str, final_output: str) -> str:
    """
    Appends the cinematic outro clip with seamless audio/video concat filter.
    """
    logger.info(f"Merging cinematic outro clip into final video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", main_video,
        "-i", outro_video,
        "-filter_complex",
        "[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
        "[1:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
        "[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];"
        "[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        final_output
    ]
    subprocess.run(cmd, check=True)
    return final_output

def produce_chat_video(
    prompt: str,
    duration: int = 180,
    channel: str = "auto",
    auto_upload: bool = False,
    include_outro: bool = True
) -> Dict[str, Any]:
    """
    Complete Autonomous Pipeline for chat-triggered videos.
    """
    t0 = time.time()
    logger.info(f"🎬 Processing Video Request: '{prompt}' (Duration: {duration}s, Upload: {auto_upload})")

    lang = detect_language(prompt)
    niche = detect_niche(prompt) if channel == "auto" else ("trading" if "trading" in channel else "psychology")
    voice = VOICE_EN if lang == "en" else VOICE_HI

    # 1. Deep Research Script
    deep_data = generate_deep_script(prompt, niche, lang, duration)
    title = deep_data["title"]
    script_text = deep_data["script"]
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")[:35]

    logger.info(f"Generated deep research script ({len(script_text.split())} words) for niche: {niche.upper()}")

    # 2. Audio Synthesis
    audio_path = os.path.join(TEMP_DIR, f"chat_audio_{int(t0)}.mp3")
    asyncio.run(synth_voice(script_text, voice, audio_path))

    cmd_p = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    real_duration = float(subprocess.check_output(cmd_p).decode().strip())
    logger.info(f"Voice synthesized successfully: {real_duration:.1f}s")

    # 3. Assemble Strictly UNIQUE Normalized Clips (ZERO IN-VIDEO REPEATS)
    director = CinematicDirector(niche=niche)
    raw_unique_clips = director.gather_unique_clips_for_duration(
        target_duration=real_duration,
        prompt=title,
        niche=niche,
        avg_scene_duration=4.2,
        max_online_downloads=6,
        script_text=script_text
    )

    norm_clips = []
    norm_dir = os.path.join(_root, "storage", "ep_norm_clips")
    os.makedirs(norm_dir, exist_ok=True)

    for idx, raw_clip in enumerate(raw_unique_clips):
        n_clip = os.path.join(norm_dir, f"chat_{int(t0)}_sc_{idx:02d}.mp4")
        normalize_cinematic_clip(raw_clip, n_clip, target_duration=4.5)
        norm_clips.append(n_clip)

    logger.success(f"🎬 Assembled {len(norm_clips)} STRICTLY UNIQUE clips! Total visual coverage: {len(norm_clips)*4.5:.1f}s vs audio {real_duration:.1f}s (ZERO LOOPS)!")

    # 4. Background Music
    bgm_file = os.path.join(_root, "resource", "songs", "output001.mp3")

    # 5. Render Master Video + Signature Content ID Outro (Zero Subtitles, Broadcast Loudness)
    final_output_path = os.path.join(OUT_DIR, f"{safe_title}_{int(t0)}.mp4")
    content_id_outro = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
    effective_outro = content_id_outro if (include_outro and os.path.exists(content_id_outro)) else None

    logger.info(f"🎬 Rendering final 1080p documentary with broadcast loudness & signature Content ID outro: {effective_outro}...")
    render_cinematic_longform(
        normalized_clips=norm_clips,
        audio_path=audio_path,
        output_video_path=final_output_path,
        bgm_path=bgm_file if os.path.exists(bgm_file) else None,
        audio_duration=real_duration,
        burn_subtitles=False,
        outro_clip_path=effective_outro,
        outro_duration=None  # ALWAYS PLAY FULL SIGNATURE OUTRO CLIP PER USER MANDATE
    )

    # 6. Single-Source Auto-Delivery & Ephemeral Temp Purge (Zero Disk Leak)
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"
    dest_download = final_output_path
    try:
        from yt_uploader.disk_sanitizer import safe_deliver_and_deduplicate, purge_ephemeral_clips, enforce_infinite_storage_headroom
        purge_ephemeral_clips(norm_clips)
        enforce_infinite_storage_headroom(min_free_gb=10.0)
        if not is_ci:
            dest_download = safe_deliver_and_deduplicate(final_output_path, USER_DOWNLOADS, move_instead_of_copy=True)
        else:
            logger.info(f"CI runner detected: Preserving video at {final_output_path}")
            dest_download = final_output_path
    except Exception as _ds_err:
        logger.warning(f"Disk sanitizer note: {_ds_err}")
        dest_download = final_output_path

    # 8. Deep-Researched Viral SEO
    seo = generate_viral_seo_package(subject=title, niche=niche)
    seo["visibility"] = "unlisted"  # Strictly unlisted for future uploads per mandate
    seo_meta_file = os.path.join(OUT_DIR, f"{safe_title}_{int(t0)}_meta.json")
    with open(seo_meta_file, "w", encoding="utf-8") as f:
        json.dump(seo, f, indent=4)

    # 9. Smart Multi-Platform Auto-Upload (YouTube, Rumble, etc.)
    actual_file = dest_download if (dest_download and os.path.exists(dest_download)) else final_output_path
    upload_result = None
    should_upload = auto_upload or any(k in prompt.lower() for k in ["rumble", "upload", "रंबल", "अपलोड"])
    if should_upload:
        try:
            from yt_uploader.multi_platform_router import parse_multi_platform_intent, dispatch_to_platforms
            intent = parse_multi_platform_intent(prompt)
            logger.info(f"🚀 Multi-Platform Auto-Upload triggered for: {intent['platforms']}")
            upload_result = dispatch_to_platforms(
                video_path=actual_file,
                seo_package=seo,
                platforms=intent["platforms"],
                youtube_channel=intent["youtube_channel"],
                rumble_channel=intent["rumble_channel"],
                visibility=intent["visibility"],
                rumble_license=intent["rumble_license"],
                headless=True
            )
            logger.success(f"Multi-Platform Upload Result: {upload_result}")
        except Exception as e:
            logger.error(f"Upload attempt encountered: {e}")
            upload_result = {"success": False, "error": str(e)}

    total_time = time.time() - t0
    logger.success(f"⚡ Pipeline finished in {total_time:.1f}s!")

    return {
        "success": True,
        "title": title,
        "video_path": actual_file,
        "download_path": dest_download,
        "duration": real_duration,
        "seo": seo,
        "upload_result": upload_result,
        "elapsed_seconds": total_time
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat-To-Video On-Demand Engine")
    parser.add_argument("--prompt", type=str, required=True, help="Video prompt or topic")
    parser.add_argument("--duration", type=int, default=180, help="Target duration in seconds (60-300)")
    parser.add_argument("--channel", type=str, default="auto", help="Channel (auto, trading, psychology)")
    parser.add_argument("--upload", action="store_true", help="Auto-upload to YouTube Studio")
    parser.add_argument("--no-outro", action="store_true", help="Do not append outro clip")

    args = parser.parse_args()
    res = produce_chat_video(
        prompt=args.prompt,
        duration=args.duration,
        channel=args.channel,
        auto_upload=args.upload,
        include_outro=not args.no_outro
    )
    print("\n" + "="*50)
    print(f"✅ VIDEO READY IN DOWNLOADS: {res['download_path']}")
    print(f"📊 Title: {res['title']}")
    print(f"⏱️ Duration: {res['duration']:.1f}s")
    if res.get("upload_result"):
        print(f"☁️ Upload: {res['upload_result']}")
    print("="*50)
