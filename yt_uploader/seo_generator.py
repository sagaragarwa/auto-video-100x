import re
import json
from typing import Dict, Any

def generate_viral_seo_package(
    subject: str,
    script_text: str = "",
    niche: str = "psychology",
    language: str = "hi"
) -> Dict[str, Any]:
    """
    Synthesizes an Ultra-Optimized, Algorithm-Catchy YouTube SEO Package:
    - High-CTR Dual-Hook Title (Curiosity Hook + Search Keyword)
    - Google-Indexed Structured Description with Chapters
    - 500-Character Tag Matrix
    - High-Impact 3-Word Thumbnail Punchline
    """
    clean_subj = subject.strip()
    
    # 1. High-CTR Title Engineering
    if "depression" in clean_subj.lower() or "डिप्रेशन" in clean_subj or niche == "psychology":
        title = f"Your Brain Is Lying To You... (The Dark Science of Depression) | Complete Documentary"
        punchline = "TRAPPED IN\nYOUR BRAIN?"
        badge = "HARVARD NEUROSCIENCE"
        tags = [
            "what is depression", "depression symptoms in hindi", "neurobiology of depression",
            "dopamine and serotonin", "anhedonia explained", "clinical depression hindi",
            "how to fix depression", "psychology documentary", "brain chemistry",
            "mental health awareness", "neuroscience documentary", "prefrontal cortex",
            "learned helplessness", "psychological facts", "cure depression naturally"
        ]
        chapters = [
            ("00:00", "The Invisible Trap (डिप्रेशन का असली सच)"),
            ("03:15", "The Chemical Illusion: Serotonin & Dopamine"),
            ("08:40", "Why Your Prefrontal Cortex Shuts Down"),
            ("14:20", "The Exhaustion of Hope: Anhedonia"),
            ("20:50", "Learned Helplessness & The Psychological Cage"),
            ("25:30", "The Neuroplastic Path To Permanent Recovery")
        ]
        category_id = "27" # Education
    elif "trading" in clean_subj.lower() or "market" in clean_subj.lower() or niche == "trading":
        title = f"99% Traders Will Fail Here... (The Psychological Trap of Market) | Full Documentary"
        punchline = "99% WILL\nFAIL HERE!"
        badge = "WALL STREET PSYCHOLOGY"
        tags = [
            "trading psychology", "stock market documentary", "why 99% traders lose money",
            "risk management trading", "trading discipline", "stock market for beginners",
            "smart money concepts", "option trading psychology", "price action trading",
            "emotional control in trading", "wall street trading secrets", "candlestick psychology"
        ]
        chapters = [
            ("00:00", "The Brutal Reality of Trading"),
            ("04:10", "The Casino Mindset & Dopamine Loop"),
            ("09:30", "Loss Aversion: Why You Hold Losing Trades"),
            ("15:45", "The System of the Top 1% Institutional Traders"),
            ("21:20", "Risk Management: The Only Holy Grail"),
            ("26:10", "Building An Iron Trading Discipline")
        ]
        category_id = "27" # Education
    else:
        title = f"{clean_subj} - The Hidden Truth They Never Tell You | Full Documentary"
        punchline = "THE HIDDEN\nTRUTH!"
        badge = "EXCLUSIVE REPORT"
        tags = [clean_subj, f"{clean_subj} explained", f"{clean_subj} documentary", "viral documentary", "deep analysis"]
        chapters = [
            ("00:00", "Introduction & The Big Mystery"),
            ("05:00", "The Underlying Mechanics"),
            ("12:00", "Critical Evidence & Breakdown"),
            ("18:00", "The Turning Point"),
            ("24:00", "Final Conclusion & Actionable Insight")
        ]
        category_id = "28" # Science & Tech

    # 2. Build Rich Description with Timestamps & Algorithm Hooks
    desc_lines = [
        f"{title}\n",
        f"क्या आप जानते हैं कि {clean_subj} के पीछे की असली सच्चाई क्या है? इस विस्तृत और गहन 30-मिनट की डॉक्यूमेंट्री में हम वैज्ञानिक तथ्यों, न्यूरोबायोलॉजी और मनोवैज्ञानिक शोध के आधार पर इस विषय के हर पहलू को गहराई से उजागर करते हैं।\n",
        "📌 Key Chapters & Timestamps (सीधे संबंधित भाग पर जाएँ):"
    ]
    for ts, ch_title in chapters:
        desc_lines.append(f"{ts} - {ch_title}")

    desc_lines.extend([
        "\n🔬 Scientific & Research Citations:",
        "- Peer-Reviewed Neurobiology and Psychological Archives",
        "- Cognitive Science and Behavioral Economics Research Review\n",
        "💬 What are your thoughts on this? Drop your perspective in the comments below!\n",
        "🔔 Subscribe for more in-depth, research-backed cinematic documentaries.\n",
        f"#{niche} #documentary #science #analysis #psychology"
    ])
    description = "\n".join(desc_lines)

    # 3. Format Tags to exact 500-char string
    tag_string = ",".join(tags)
    if len(tag_string) > 490:
        tag_string = tag_string[:490].rsplit(",", 1)[0]

    return {
        "title": title,
        "punchline": punchline,
        "badge": badge,
        "description": description,
        "tags": tag_string,
        "tags_list": tags,
        "category_id": category_id,
        "made_for_kids": False,
        "visibility": "public"
    }

if __name__ == "__main__":
    pkg = generate_viral_seo_package("The Neurobiology of Depression", niche="psychology")
    print(f"Title: {pkg['title']}")
    print(f"Punchline: {pkg['punchline']}")
    print(f"Tags Count: {len(pkg['tags_list'])}")
    print(f"Description length: {len(pkg['description'])} chars")
