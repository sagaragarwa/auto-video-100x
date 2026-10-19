"""
Deep Research Script Generator for 40-Episode Master Documentary Series.
- 30 Institutional Trading Masterclasses (>20 minutes each, ~3,400 to 3,600 words)
- 10 Mental Health & Psychiatric Masterclasses (>20 minutes each, ~3,400 to 3,600 words)
- Organic High-Retention Engagement Hooks (Subscribe @ 3m, Like/Comment @ 10m, Community Outro @ 18m)
- 100% Procedural Execution (Zero LLM Tokens / 100x Antigravity Cost Reduction)
"""

from typing import Dict, Any

def generate_deep_trading_script(ep_info: Dict[str, Any]) -> str:
    title = ep_info["title"]
    theme = ep_info["theme"]
    focus = ep_info["focus"]
    ep_num = ep_info["episode"]

    cta_3m = "Before we dissect the proprietary routing mechanisms, if you find this institutional breakdown valuable, make sure to subscribe to the channel and turn on notifications so you never miss an investigative market masterclass."
    cta_10m = "If this deep dive is giving you a completely new perspective on market microstructure, drop a like on this video and leave a comment below sharing your thoughts—it directly helps YouTube surface this independent financial research to more traders."
    cta_18m = "What is your perspective on this structural shift in Wall Street? Share your experience in the comments below, and subscribe to join our growing community of quantitative and macro thinkers."

    sections = [
        # Chapter 1: Introduction & The Core Market Paradox
        f"""Welcome to this comprehensive institutional masterclass on modern market architecture. Today, we are conducting an exhaustive, granular investigation into {title}.

Most participants look at their brokerage trading screens and assume that what they see on the public lit order book represents the entirety of market reality. They see green and red candlestick bars forming patterns, they draw trend lines, and they believe that supply and demand meet in a transparent, democratic auction. But as professional quantitative traders, macro hedge fund managers, and institutional market operators understand, the public tape is often merely a carefully orchestrated optical illusion. {focus}

To understand the immense scale and gravity of this phenomenon, we must first confront the foundational mechanics of {theme}. When tens of billions of dollars migrate across global asset classes, the primary concern of sovereign wealth funds, pension allocators, and quantitative institutions is not simply getting filled; it is the ruthless, unrelenting mitigation of market impact, information leakage, and adverse selection.

Imagine you are the chief investment officer of a multi-billion dollar sovereign pension fund. Your mandate requires you to rebalance out of five million shares of a major blue-chip corporation. If you submit that block order directly to a public lit exchange like the New York Stock Exchange or Nasdaq, your order instantly appears on the consolidated Level Two order book. In less than one millisecond, high-frequency algorithms, quant desks, and proprietary market makers detect this monumental wall of supply. The game theory is immediate and brutal: every predatory algorithm short-sells the market in front of your order, pulls resting bids, and steps away from the bid-ask spread. Within seconds, the price crashes before even two percent of your capital is filled. By the time your order completes, slippage and market impact have incinerated tens of millions of dollars. In institutional finance, transparency is not an asset; transparency is a catastrophic liability.""",

        # Minute 3 CTA
        cta_3m,

        # Chapter 2: The Evolution of Market Microstructure & Reg NMS
        f"""Let us now trace the structural evolution of modern electronic exchanges and how Regulation National Market System, or Reg NMS, fundamentally transformed Wall Street. For decades, trading was conducted on physical exchange floors through open outcry specialist systems. The human specialist stood at the post, matching buy and sell tickets, leaning against market volatility with personal capital. While this model had significant flaws, it maintained localized liquidity pools.

In 2005, the implementation of Rule 611—the Order Protection Rule—mandated that broker-dealers route orders to the best displayed price across all registered national exchanges. While conceived with the noble intention of protecting retail investors, the unintended consequence was the extreme fragmentation of the American financial system. Suddenly, liquidity was splintered across dozens of electronic communication networks, direct feeds, and alternative execution venues.

To navigate this fragmented landscape, modern quantitative firms abandoned traditional floor brokers and invested hundreds of millions of dollars into colocation facilities directly adjacent to exchange matching engines in New Jersey data centers such as Secaucus, Mahwah, and Carteret. When an order is generated today, its fate is decided not in minutes or seconds, but in single-digit nanoseconds. Quantitative firms deploy Field-Programmable Gate Array microchips, custom Linux operating systems stripped of kernel bloat, and microwave transmission networks spanning the Appalachian Mountains from Chicago to New York. In this environment, latency is not just a technical specification; latency is the primary determinant of economic survival.""",

        # Chapter 3: Order Book Anatomy: Level 2, Level 3, and Depth of Market
        f"""To truly comprehend modern execution, we must examine the hidden anatomy of order books and depth-of-market feeds. The public market data feed, known as the Securities Information Processor or SIP, consolidates top-of-book quotes from all protected exchanges. However, the SIP feed suffers from geographic and aggregation latency, often lagging behind proprietary direct exchange feeds by several hundred microseconds.

Quantitative trading firms do not consume the public SIP feed. Instead, they purchase direct raw multicast data feeds—such as ITCH from Nasdaq and OpenBook from the New York Stock Exchange. These direct feeds provide full Level Three order book visibility, broadcasting every single order addition, modification, cancellation, and execution timestamped to the microsecond or nanosecond level.

By reconstructing the Level Three order book in local server memory, algorithms can observe the internal dynamics of passive liquidity. They monitor the replenishment speed of limit orders, detect the presence of hidden reserve quantities, and calculate queue priority at every price tick. In modern market making, being first in queue at the National Best Bid or Offer is the difference between capturing a profitable half-cent spread or suffering immediate adverse selection when an informed toxic order sweeps the book.""",

        # Chapter 4: Granular Mechanics, Hidden Pegs, and Dark Crossing Networks
        f"""Now let us dissect the granular mechanics of {title} and how off-exchange execution operates behind the curtain. In traditional lit exchanges, every resting limit order is broadcast to the public order book. But within alternative trading systems and dark crossing networks, orders rest silently with no pre-trade transparency.

Consider the sophisticated taxonomy of order types that govern these venues. Institutional algorithms utilize Midpoint Peg orders, which continuously recalculate their execution price to the exact midpoint between the National Best Bid and National Best Offer. They deploy Discretionary Pegs, which rest at passive prices but dynamically reach out to execute aggressively if an opportunistic counterparty arrives. Furthermore, they utilize Minimum Quantity instructions to prevent predatory sniffing algorithms from uncovering their presence with small lot sizes.

However, dark liquidity is not an infallible sanctuary. Predatory algorithmic desks continuously monitor trade prints on the Trade Reporting Facility to detect patterns of off-exchange accumulation. When an institution enters a dark pool with a non-displayed parent order, market makers and high-frequency algorithms utilize pinging tactics. They fire rapid sequences of immediate-or-cancel probe orders into multiple dark pools. The instant a ping order is filled, the predatory algorithm detects the presence of the institutional whale. It immediately withdraws its resting liquidity across all lit exchanges, widens the bid-ask spread, and aggressively acquires inventory ahead of the institution, forcing the institutional desk to suffer severe adverse selection and substantial price slippage.""",

        # Chapter 5: Proprietary Dark Order Types & Crossing Logic
        f"""To counter predatory sniffing, quantitative routing engineers have designed complex non-displayed order execution mechanisms. One of the most critical mechanisms is the Indication of Interest, or IOI. An IOI is an electronic message broadcast between institutional crossing networks signaling an appetite to trade large blocks without revealing the exact price, size, or symbol to the broader lit marketplace.

When two matching IOIs intersect within a crossing network, the system initiates a blind auction. Crossing algorithms determine the fill price using Volume-Weighted Average Price or the midpoint of the consolidated National Best Bid and Offer at a randomized microsecond timestamp. By injecting temporal randomness into the execution timestamp, the venue prevents high-frequency latency arbitrageurs from reverse-engineering the trade based on the exact timing of the execution report.

Moreover, institutional trading desks utilize multi-tier dark pool aggregation routers. These smart order routers establish tiered access hierarchies: routing first to internal crossing networks, second to broker-owned dark pools with verified non-toxic counterparty tiers, and only as a last resort sending residual unexecuted child orders to public lit exchanges. This systematic filtration ensures that the institution interacts primarily with passive, natural long-term institutional capital rather than high-frequency market makers seeking quick scalp opportunities.""",

        # Chapter 6: Regulatory Mandates: SEC Rules 605, 606 and Best Execution
        f"""To maintain an illusion of fairness, regulatory bodies established transparency frameworks through SEC Rules 605 and 606. Rule 605 requires market centers to publish monthly reports detailing execution quality, including realized spread, effective spread, and price improvement statistics. Rule 606 requires broker-dealers to publicly disclose the venues to which they route non-directed customer orders, alongside any monetary remuneration received.

However, institutional participants understand that compliance metrics rarely capture the full economic reality of execution. While a wholesaler may report price improvement on a retail order by giving an execution one-tenth of a cent better than the National Best Bid or Offer, the broader market may have moved multiple cents in the milliseconds preceding the fill.

Institutional asset managers must satisfy fiduciary Best Execution mandates under the Investment Advisers Act. To prove best execution to regulators and institutional clients, compliance desks employ independent Transaction Cost Analysis engines. These TCA platforms calculate benchmark performance against arrival price, Volume-Weighted Average Price, and Time-Weighted Average Price, decomposing costs into explicit commissions and implicit costs such as delay costs, price impact, and opportunity cost from unexecuted orders.""",

        # Chapter 7: Case Study 1: The May 2010 Flash Crash & Algorithmic Voids
        f"""To grasp how these structural forces play out under extreme market stress, let us conduct a forensic breakdown of a real-world institutional liquidity crisis. During periods of tranquil macroeconomic regimes, market participants operate under the comforting belief that liquidity is infinite and instantaneous. But liquidity in modern electronic markets is an endogenous variable; it exists precisely when it is not needed, and it vanishes the moment stress enters the financial system.

Consider the events of historical market dislocations, such as the May 2010 Flash Crash. In less than thirty-six minutes, nearly one trillion dollars in market value evaporated from American equities. The root cause was not an exogenous geopolitical catastrophe, but an endogenous algorithmic feedback loop triggered by a massive automated execution algorithm attempting to hedge an equity index position without accounting for prevailing order book depth.

As automated quantitative market makers detected the sudden surge in toxic selling volume, their automated risk management models triggered instantaneous inventory drawdowns. High-frequency algorithms began buying from one venue and selling to another, generating billions in volume without providing genuine liquidity. When the algorithms hit internal risk thresholds, they simultaneously pulled their resting bids from the book. The bid-ask spread across blue-chip stocks widened to absurd levels, with some securities trading down to one cent while others traded at one hundred thousand dollars. The flash crash proved that when everyone relies on automated liquidity providers, liquidity is an optical illusion that vanishes when stress spikes.""",

        # Chapter 8: Case Study 2: The March 2020 Treasury Basis Blowout & Repo Freezes
        f"""A decade later, in March 2020, another profound structural dislocation erupted—this time in the multi-trillion dollar market for United States Treasury securities. This event, known as the Treasury basis unwind, exposed the fragile interdependence between leveraged hedge funds, the repo market, and fixed income market makers.

Hedge funds had accumulated massive leveraged positions exploiting the basis trade—arbitraging the minuscule price discrepancy between physical Treasury cash bonds and Treasury futures contracts. To amplify annual returns from a few basis points to double-digit figures, hedge funds leveraged their cash positions up to fifty to eighty times using the overnight repo market.

When the global pandemic triggered an unprecedented dash for cash, institutional asset managers and foreign central banks began dumping physical Treasury bonds to raise US dollar liquidity. Primary dealer banks, constrained by post-2008 regulatory leverage ratios such as the Supplementary Leverage Ratio, were legally unable to absorb the hundreds of billions in Treasury supply onto their balance sheets. As the price of cash Treasuries diverged from futures, margin calls cascaded through the hedge fund complex. Forced liquidations created a self-reinforcing downward spiral, causing the most liquid sovereign debt market in the world to freeze until the Federal Reserve intervened with multi-trillion dollar liquidity backstops. This crisis demonstrated that leverage and liquidity are inextricably bound to bank regulatory plumbing.""",

        # Minute 10 CTA
        cta_10m,

        # Chapter 9: The Mathematical Framework: Almgren-Chriss & Poisson Arrival
        f"""Let us now explore the mathematical and quantitative framework that underpins modern execution algorithms. When quantitative financial engineers design execution systems, they rely on stochastic calculus and optimal execution mathematics, most notably the seminal Almgren-Chriss framework.

The fundamental problem facing any institutional trader is the mathematical tradeoff between market impact and timing risk. If an algorithm executes a massive order too quickly, it pushes the price against itself, creating quadratic temporary and permanent market impact as modeled by the square root law of trading volume. Conversely, if the algorithm executes too slowly to minimize market impact, it exposes the firm to timing risk—the danger that the broader market will drift unfavorably over the execution horizon.

To solve this optimization problem, institutional desks formulate the objective function as a mean-variance tradeoff. They calculate the Hamilton-Jacobi-Bellman differential equations to derive the optimal trading trajectory. Modern algorithms do not execute linearly. They deploy Poisson point processes to inject stochastic randomness into order submission intervals, continually varying slice quantities to evade machine learning detection from competing predatory desks. Every parameter—from bid-ask spread elasticity to transient price impact decay—is calibrated in real time using high-frequency tick data.""",

        # Chapter 10: Central Bank Plumbing, Repo Facilities, and SOFR Transmission
        f"""Furthermore, we must examine how modern market microstructure is inextricably linked to central bank plumbing, regulatory constraints, and sovereign debt markets. The stability of equity and derivative markets is fundamentally dependent upon the short-term funding markets that operate beneath the surface of global banking.

Since the global financial crisis of 2008 and the subsequent introduction of Basel Three, the Supplementary Leverage Ratio, and Dodd-Frank regulations, primary dealer banks have faced severe balance sheet balance constraints. In previous eras, commercial banks used their expansive balance sheets to absorb inventory shocks, acting as shock absorbers for the entire financial architecture. Today, Tier-One banks cannot afford the punitive regulatory capital charges associated with holding large inventories of corporate bonds, equities, or even sovereign Treasuries.

As a direct consequence, the role of liquidity provision has been outsourced to non-bank financial intermediaries and quantitative market making firms. However, these non-bank entities rely heavily on repo funding and prime brokerage credit lines. When short-term repo rates experience volatility—or when the Federal Reserve shifts its balance sheet policy through Quantitative Tightening and Overnight Reverse Repo adjustments—the collateral velocity of the entire system slows down. When repo plumbing tightens, market makers are forced to curtail their leverage, directly reducing the depth of market across all equities, futures, and foreign exchange venues.""",

        # Chapter 11: Payment for Order Flow, Wholesalers, and Retail Internalization
        f"""Let us also deconstruct the retail illusion created by zero-commission brokerage applications and Payment for Order Flow, or PFOF. When a retail trader clicks buy on their mobile app, they assume their order travels directly to the New York Stock Exchange to compete with institutional buyers. In reality, retail orders are routinely intercepted by wholesale market makers such as Citadel Securities and Virtu Financial.

Wholesalers pay retail brokerages hundreds of millions of dollars annually for the legal right to internalize retail orders. Why are wholesalers willing to pay handsomely for retail order flow? Because in market microstructure terminology, retail flow is classified as uninformed or non-toxic. A retail trader purchasing one hundred shares of a technology stock possesses no private, market-moving information; their order will not trigger a structural price trend.

By segregating non-toxic retail orders from informed institutional flow, wholesalers can execute retail trades against their internal inventory at prices slightly better than the displayed public quote—a process known as price improvement. Wholesalers reliably capture the bid-ask spread with virtually zero directional risk, while the public lit exchanges are left with increasingly toxic institutional flow. As a result, lit exchange spreads widen, and the public price discovery mechanism becomes increasingly distorted.""",

        # Minute 18 CTA
        cta_18m,

        # Chapter 12: Tape Reading: Cumulative Volume Delta, Volume Profile, and Footprint Absorption
        f"""For the independent quantitative researcher, professional trader, and serious macro thinker, understanding these hidden mechanics is the prerequisite for building a durable edge. While retail participants continue to rely on lagging technical indicators such as Moving Averages and Relative Strength Indexes, sophisticated operators focus on order flow footprints and liquidity surfaces.

By analyzing Volume-Weighted Average Price deviations, Cumulative Volume Delta divergences, and order book imbalance ratios, one can detect where institutional market participants are actively absorbing liquidity. When an institutional desk is accumulating a massive position, the tape reveals distinct mathematical footprints: heavy aggressive market orders being absorbed by passive resting iceberg limits without price displacement. This absorption represents the silent presence of smart money operating in the shadows.

Rather than trying to predict where the price will travel next based on subjective chart patterns, the modern quantitative operator seeks to align with structural liquidity flows. By identifying the key liquidity pools where retail stop-losses are clustered, one can anticipate the exact zones where institutional algorithms will engineer sweeps to harvest liquidity. You stop thinking like a retail consumer and start analyzing the market through the eyes of an institutional liquidity architect.""",

        # Chapter 13: Quantitative Risk Sizing: The Kelly Criterion & Volatility Targeting
        f"""In parallel with reading market microstructure, institutional longevity requires an uncompromising commitment to mathematical risk management and position sizing. Amateur traders focus entirely on entry signals, convinced that profitability is a function of prediction accuracy. Professional quantitative funds, by contrast, treat trade entries as probabilistic bets and focus their mathematical rigor on the Kelly Criterion and capital preservation.

The Kelly Criterion determines the mathematically optimal fraction of capital to allocate to any given bet based on win rate and reward-to-risk ratio. However, because financial markets exhibit fat-tailed, non-Gaussian return distributions, institutional desks rarely trade full Kelly. Instead, they deploy fractional Kelly—typically one-quarter or one-tenth Kelly—to insulate the portfolio against extreme drawdown risks and black swan events.

Furthermore, institutional risk engines enforce dynamic volatility targeting. When market volatility increases, the system automatically scales down position sizes to maintain a constant portfolio risk profile. By decoupling position size from emotional conviction and anchoring it to statistical market volatility, professional operators survive the inevitable adverse regimes that eliminate undisciplined speculators.""",

        # Chapter 14: Epilogue: Structural Realism & Institutional Mindset
        f"""As we conclude this comprehensive masterclass on {title}, let us reflect on the core philosophy that separates enduring market operators from short-lived speculators. Financial markets are not casinos, nor are they benevolent institutions designed to distribute wealth. They are highly evolved, ruthlessly efficient arenas designed to extract capital from participants who lack an understanding of market microstructure, probability, and risk asymmetry.

True mastery requires relinquishing the desire for certainty and embracing the discipline of structural thinking. The most successful institutional operators do not win because they possess a magical crystal ball; they win because they understand the plumbing of the system, maintain rigorous risk parameters, and operate with an asymmetrical advantage grounded in mathematical realism.

Wall Street will continue to innovate new off-exchange routing systems, faster microchips, and more complex financial derivatives. But the fundamental laws of market microstructure—supply, demand, adverse selection, and liquidity scarcity—remain eternal. Thank you for investing your time in this deep dive into {title}. Stay disciplined, protect your capital, and we look forward to seeing you in our next investigative masterclass."""
    ]

    return "\n\n".join(sections).strip()

def generate_deep_psychology_script(ep_info: Dict[str, Any]) -> str:
    title = ep_info["title"]
    theme = ep_info["theme"]
    focus = ep_info["focus"]
    ep_num = ep_info["episode"]

    cta_3m = "If you or someone you care about has walked through this silent struggle, please take a moment to subscribe. We are building a dedicated sanctuary for evidence-based mental health education and deep psychological empathy."
    cta_10m = "If this explanation is bringing clarity or comfort to what you have been experiencing, please like this video and leave a comment below sharing your journey. Your words might be the exact lifeline someone else needs to read today."
    cta_18m = "Healing is not a linear destination, but a courageous daily practice of self-compassion. Please subscribe to stay connected with our upcoming psychological documentaries, and share your thoughts in the comments."

    sections = [
        # Chapter 1: Introduction: Deconstructing the Stigma & Validating Suffering
        f"""Welcome to this compassionate, in-depth psychological documentary. Today, we are undertaking a profound, evidence-based investigation into one of the most challenging and misunderstood aspects of the human condition: {title}.

Mental health conditions are rarely understood from the inside out. All too often, modern society reduces profound neurobiological suffering to simple personality flaws, lack of willpower, or fleeting emotional weaknesses. When someone is drowning beneath the weight of this condition, well-meaning friends and family often tell them to just think positive, snap out of it, or get some fresh air. But clinical neuroscience, neuropsychiatry, and human psychology tell a radically different and far more validating story. {focus}

To understand what truly transpires during {theme}, we must journey deep into the neurochemical architecture of the human brain. The human nervous system is an astonishingly complex, delicate symphony of neurotransmitters, receptor densities, and interconnected neural networks. When an individual experiences this condition, specific brain circuits—such as the default mode network, the amygdala, the prefrontal cortex, and the anterior cingulate cortex—enter states of severe dysregulation.

Consider the lived reality of an individual navigating this state. It is not merely feeling sad, anxious, or emotionally tired; it is a profound physiological and existential exhaustion. The brain's reward centers become blunted, sensory inputs can become overwhelming, and the internal voice turns into an unrelenting, hyper-critical persecutor. The nervous system becomes trapped in chronic survival mode, interpreting the everyday world through a lens of existential dread, hypervigilance, or complete emotional numbness. In clinical medicine, we know this is not a choice; it is a biological condition requiring deep comprehension and scientific care.""",

        # Minute 3 CTA
        cta_3m,

        # Chapter 2: Cellular Machinery & Neurochemical Foundations
        f"""Let us examine the neuroanatomy and cellular machinery that governs our emotional equilibrium. The human brain contains over eighty-six billion neurons, communicating through trillions of synaptic connections using chemical messengers such as serotonin, dopamine, norepinephrine, and gamma-aminobutyric acid, commonly known as GABA.

In a healthy nervous system, neurotransmitter synthesis, vesicular release, receptor binding, and reuptake mechanisms operate in dynamic balance. However, when chronic psychological stress, genetic predispositions, or neuroinflammatory cascades take hold, this delicate neurochemical balance is severely disrupted. Consider dopamine, the primary neuromodulator responsible for motivation, goal-directed behavior, and hedonic pleasure. When dopamine receptors in the nucleus accumbens become downregulated, the individual experiences severe anhedonia—the complete inability to feel pleasure or joy from activities that once brought deep fulfillment.

Similarly, disruptions in serotonin transport mechanisms throughout the raphe nuclei impair emotional context processing. Without adequate serotonin signaling, the brain loses its capacity to buffer against acute emotional stress, leaving the prefrontal cortex unable to modulate primitive fear signals emanating from the limbic system. Furthermore, imbalances between excitatory glutamate and inhibitory GABA create a state of neurological excitotoxicity, keeping cognitive networks in a state of chronic alarm. These cellular alterations are physical, measurable biological phenomena, demonstrating beyond all scientific doubt that mental suffering is deeply rooted in physical brain physiology.""",

        # Chapter 3: The Stress Architecture: HPA Axis Dysregulation & Cortisol Toxicity
        f"""Now let us explore the autonomic nervous system and the catastrophic toll of chronic stress on the human body. The human autonomic nervous system is divided into two primary branches: the sympathetic nervous system, which mobilizes the body for fight-or-flight in response to danger, and the parasympathetic nervous system, which facilitates rest, digestion, and physiological repair.

When the brain perceives an overwhelming threat—whether from external trauma or internal emotional turmoil—the hypothalamic-pituitary-adrenal axis, or HPA axis, activates. The hypothalamus releases corticotropin-releasing hormone, signaling the pituitary gland to secrete adrenocorticotropic hormone, which prompts the adrenal glands to flood the bloodstream with cortisol and epinephrine. In acute situations, this survival cascade preserves life.

However, in individuals suffering from chronic psychiatric and mood disorders, the HPA axis negative feedback loop becomes broken. Cortisol remains persistently elevated for months or years, bathing neural tissues in a toxic inflammatory environment. High sustained cortisol levels down-regulate brain-derived neurotrophic factor, or BDNF, leading to synaptic pruning and observable atrophy within the hippocampus—the crucial structure responsible for emotional memory consolidation and contextual threat evaluation. At the same time, the amygdala becomes hyper-sensitized and enlarged, firing chronic false alarms of impending catastrophe.""",

        # Chapter 4: Polyvagal Theory: Sympathetic Overdrive vs. Dorsal Vagal Shutdown
        f"""To gain deeper insight into the physiological states that accompany this condition, we turn to Polyvagal Theory, pioneered by Dr. Stephen Porges. The vagus nerve—the tenth cranial nerve—is the primary conduit of the parasympathetic nervous system, serving as an information superhighway between the brainstem and the heart, lungs, and viscera.

According to polyvagal architecture, the autonomic nervous system operates through three evolutionary tiers. When we feel safe, the ventral vagal complex is active, enabling social engagement, eye contact, and vocal prosody. However, when perceived threat escalates, the system regresses to the sympathetic fight-or-flight mobilization. The heart rate accelerates, breathing becomes shallow, and muscles tense for survival.

If the stressor remains unrelenting and escape is impossible, the nervous system activates its oldest evolutionary defense: the dorsal vagal shutdown. This is the physiological freeze state. Metabolic activity plummets, blood pressure drops, and consciousness becomes dissociated or deeply numbed. Sufferers of severe depression, trauma, and panic frequently cycle between agonizing sympathetic panic and catatonic dorsal vagal collapse. Recognizing that these states are biological survival responses—not conscious moral choices—is vital for healing.""",

        # Chapter 5: Neuro-Endocrine Axis: Thyroid, Adrenal Exhaustion, and Hormone Interplay
        f"""Beyond the central nervous system, clinical psychiatry increasingly focuses on the neuro-endocrine axis and its profound impact on mental resilience. The thyroid gland, situated in the neck, produces triiodothyronine and thyroxine—hormones that regulate mitochondrial energy production throughout every neuron in the cerebral cortex.

Subclinical hypothyroidism, characterized by elevated thyroid-stimulating hormone despite normal peripheral hormone levels, is frequently misdiagnosed as refractory depression or chronic lethargy. When cellular metabolism slows, neurotransmitter synthesis declines, and cognitive processing speed plummets.

Similarly, the adrenal glands, exhausted by months or years of relentless sympathetic overdrive, eventually suffer allostatic collapse. Cortisol awakening curves become flattened, leaving the individual utterly exhausted in the morning yet wired and unable to sleep at midnight. Sex steroid hormones, including estrogen, progesterone, and testosterone, also exert powerful neuroprotective and neuromodulatory effects on serotonin and GABA receptor densities. When hormonal rhythms fluctuate wildly during periods of extreme chronic distress, the brain loses a crucial biological stabilizer, creating acute emotional volatility and profound somatic vulnerability.""",

        # Chapter 6: The Default Mode Network (DMN): Rumination Loops and Cognitive Entrapment
        f"""To truly understand the internal mental architecture of this condition, we must investigate the Default Mode Network, or DMN. The DMN is a widespread network of interacting brain regions—including the medial prefrontal cortex, the posterior cingulate cortex, and the angular gyrus—that activates when an individual is not engaged in an external goal-directed task. It is the seat of the narrative self, autobiographical memory, and internal monologue.

In neurotypical individuals, the default mode network smoothly powers down whenever attention is directed toward the external environment. But in individuals suffering from major depression, severe anxiety, and complex mood disorders, modern neuroimaging studies reveal that the DMN becomes pathologically hyperactive, hyper-connected, and rigidly locked.

This hyper-connectivity traps consciousness in an agonizing loop of depressive rumination, obsessive worry, and negative self-attribution. The mind continually replays past regrets with excruciating detail or projects catastrophic future scenarios with visceral certainty. Every neutral sensory input is filtered through a cognitive lens of personal inadequacy, hopelessness, and existential despair. The sufferer feels completely trapped within their own skull, helpless to silence the unrelenting internal critic that dismantles their self-worth minute by minute.""",

        # Chapter 7: Evolutionary Neurobiology & The Modern Mismatch Paradox
        f"""To fully contextualize why our neurobiology is so vulnerable to {title}, we must understand the profound evolutionary mismatch between our ancestral wiring and modern civilization. For over three hundred thousand years, the human nervous system evolved in small hunter-gatherer tribes on the African savannah. In that ancestral environment, physical stressors were acute, immediate, and infrequent—such as fleeing from a predator or tracking game.

Once the physical threat passed, the sympathetic nervous system deactivated, allowing the individual to return to a baseline state of community connection, rest, and safety. Furthermore, human survival depended entirely on tribal belonging; social ostracization was a literal death sentence. Because of this, the human brain evolved hyper-sensitive social monitoring circuits to detect the slightest hint of peer rejection or disapproval.

In modern post-industrial society, however, our paleolithic nervous systems are bombarded by an unceasing barrage of chronic, abstract, and unresolved stressors. We are subjected to artificial blue light around the clock, relentless algorithmic notifications, continuous social media comparison with millions of strangers, and sedentary isolation in concrete environments. The primitive limbic system cannot distinguish between a financial deadline, an online hostile comment, or a saber-toothed tiger; it responds to all modern micro-stressors with the exact same life-or-death physiological mobilization. When this ancient emergency survival system is triggered twenty-four hours a day, the biological scaffolding of mental health inevitably buckles under the strain.""",

        # Chapter 8: Case Study & Lived Phenomenology: Morning Executive Paralysis & Social Masking
        f"""Let us now step into the lived phenomenological experience of someone navigating this condition on a daily basis. To the outside observer, the individual may appear capable of performing their duties, or perhaps they appear detached, withdrawn, or irritable. Society often interprets this withdrawal as laziness, antisocial behavior, or lack of consideration.

What the outside world does not see is the monumental expenditure of energy required just to survive a single morning. Imagine waking up after eight hours of fragmented sleep feeling as though your limbs are weighed down by heavy lead. The simple act of rising from bed, taking a shower, or preparing a meal feels like climbing a steep mountain with an empty oxygen tank. Executive function—governed by the dorsolateral prefrontal cortex—becomes severely degraded, making even basic decisions like choosing what to wear feel overwhelmingly paralyzing.

In social situations, the individual must wear a heavy mask of normalcy, expending their last remaining reserves of vitality to smile, engage in polite conversation, and hide the roaring tempest inside their mind. By late afternoon, total cognitive and emotional depletion sets in. Relationships become strained as friends and family mistake withdrawal for rejection, unaware that the person is simply trying to keep their nervous system from undergoing a complete collapse. This profound isolation only reinforces the toxic narrative that they are a burden to those they love.""",

        # Minute 10 CTA
        cta_10m,

        # Chapter 8: The Gut-Brain Axis: Microbiome, Vagus Signaling & Systemic Inflammation
        f"""Modern clinical medicine has made a groundbreaking leap in recognizing that brain health is inextricably linked to gastrointestinal biology through the gut-brain axis. The human gut houses the enteric nervous system, often referred to as the second brain, containing over five hundred million neurons.

Furthermore, the gastrointestinal tract is colonized by trillions of microorganisms that synthesize critical neurochemicals. Over ninety percent of the body's serotonin and roughly fifty percent of its dopamine are produced in the digestive tract, influenced directly by microbial composition. When chronic stress, poor diet, or antibiotic overuse disrupts the microbiome, intestinal permeability increases—a condition commonly described as leaky gut.

Bacterial lipopolysaccharides leak into the bloodstream, triggering systemic immune activation and the release of pro-inflammatory cytokines such as interleukin-six and tumor necrosis factor-alpha. These inflammatory cytokines travel across the blood-brain barrier, triggering microglial activation in the brain. Neuroinflammation directly impairs serotonin synthesis by shunting tryptophan toward the kynurenine pathway, generating neurotoxic quinolinic acid instead of mood-stabilizing serotonin. Healing the brain, therefore, requires attending to the metabolic and microbial health of the digestive system.""",

        # Chapter 9: Sleep Architecture & Glymphatic Brain Clearance
        f"""In tandem with the gut microbiome, sleep architecture represents a non-negotiable pillar of psychiatric stabilization. During stage-three non-REM slow-wave sleep, cerebrospinal fluid surges through the interstitial spaces of the cerebral cortex via the glymphatic system. This nocturnal washing cycle purges neurotoxic metabolic waste products, including amyloid-beta and tau proteins, accumulated throughout waking consciousness.

Simultaneously, Rapid Eye Movement or REM sleep acts as an overnight emotional convalescence clinic. During REM sleep, the brain reactivates emotionally charged memories while the noradrenergic system—the chemical driver of autonomic stress—is completely silenced. This allows the hippocampus to integrate traumatic memories into long-term contextual storage while stripping away the acute visceral terror associated with the initial event.

When chronic insomnia or severe psychiatric distress fragments slow-wave and REM sleep architecture, the emotional detox process fails completely. Raw, unintegrated traumatic memories continue to trigger visceral sympathetic panic during waking hours. Restoring restorative sleep cycles through circadian entrainment and cognitive behavioral therapy for insomnia is often the single most potent intervention in stabilizing an unmoored mind.""",

        # Chapter 10: The Revolutionary Science of Adult Neuroplasticity & BDNF
        f"""Yet, in the midst of this profound darkness, clinical neuroscience and psychiatric research offer genuine, scientifically grounded hope. The single most revolutionary discovery in modern brain science is the concept of adult neuroplasticity. For over a century, medical science incorrectly assumed that the adult human brain was rigid and incapable of structural renewal. Today, we know unequivocally that the brain retains the extraordinary ability to rewire neural pathways, generate new synaptic connections, and restore emotional equilibrium throughout life.

Central to this healing process is Brain-Derived Neurotrophic Factor, or BDNF, often described as fertilizer for the brain. BDNF promotes the survival of existing neurons and encourages the growth and differentiation of new neurons and synapses—a process known as neurogenesis—particularly in the dentate gyrus of the hippocampus.

When individuals engage in targeted psychotherapies, aerobic exercise, restorative sleep, and mindfulness practices, BDNF levels surge. New neural pathways form, gradually bypassing the deeply etched ruts of chronic fear, rumination, and emotional despair. Healing is not a myth; it is an active biological and psychological reconstruction that occurs step by step, synapse by synapse.""",

        # Chapter 11: Evidence-Based Psychotherapy: CBT, DBT, ACT, and Somatic Experiencing
        f"""Through evidence-based psychotherapeutic modalities, the hyperactive default mode network can be systematically regulated and reorganized. In Cognitive Behavioral Therapy, patients learn to identify cognitive distortions—such as catastrophizing, black-and-white thinking, and emotional reasoning—and reframe them through objective reality testing.

In Acceptance and Commitment Therapy, or ACT, the objective shifts from attempting to eliminate painful thoughts to developing psychological flexibility. Patients learn cognitive defusion—observing their thoughts as passing clouds across the sky rather than absolute commands that dictate their identity.

For individuals experiencing intense emotional dysregulation and borderline traits, Dialectical Behavior Therapy provides distress tolerance, emotion regulation, and interpersonal effectiveness skills, training the prefrontal cortex to modulate intense limbic surges. Furthermore, modalities like Somatic Experiencing and EMDR address how traumatic memories are encoded in non-verbal bodily sensations, allowing the autonomic nervous system to complete thwarted fight-or-flight responses and return to homeostasis.""",

        # Chapter 12: Modern Psychiatric Horizons & Precision Medicine
        f"""Alongside psychotherapy, contemporary psychiatric medicine is advancing toward precision neuropsychiatry. Rather than treating mental health disorders as monolithic categories, modern clinicians examine underlying biological endophenotypes, sleep architecture, and genetic metabolic pathways.

In the realm of therapeutics, precision pharmacogenomics now allows clinicians to test how an individual's liver enzymes metabolize specific medications, eliminating painful months of trial and error. Non-invasive neuromodulation techniques, such as repetitive Transcranial Magnetic Stimulation, deliver magnetic pulses to stimulate underactive prefrontal circuits.

Together with emerging clinical research in neuroplastic compounds, the psychiatric landscape is expanding rapidly, offering renewed pathways for individuals who previously felt beyond help. Mental illness is shedding its medieval stigma, recognized properly as a treatable medical condition involving circuit dysregulation and neurochemical signaling deficits.""",

        # Minute 18 CTA
        cta_18m,

        # Chapter 13: Actionable Daily Somatic Protocols: Physiological Sigh & Circadian Alignment
        f"""To facilitate this neural reconstruction, clinical psychologists and neurobiologists have developed practical, evidence-based somatic protocols that directly communicate safety to the dysregulated nervous system. Because the brain and body communicate through bidirectional neural highways like the vagus nerve, we cannot simply think our way out of autonomic dysregulation; we must engage the physiology directly.

One of the fastest, most empirically validated physiological tools is the physiological sigh—a breathing pattern characterized by two quick inhales through the nose followed by a long, slow exhale through the mouth. Performing two to three physiological sighs rapidly collapses carbon dioxide levels in the lungs, triggering the vagus nerve to slow down the heart rate and disengage the sympathetic fight-or-flight response.

Similarly, consistent circadian light exposure—viewing natural sunlight within thirty minutes of waking—sets the suprachiasmatic nucleus, stabilizing cortisol awakening rhythms and optimizing nighttime melatonin synthesis for restorative slow-wave sleep. Engaging in non-sleep deep rest and somatic grounding practices allows the nervous system to experience profound safety, gradually releasing stored somatic trauma and restoring baseline autonomic resilience.""",

        # Chapter 14: Relapse Prevention & Long-Term Psychological Resilience
        f"""Sustained mental wellness is not about achieving a permanent state of euphoria or never feeling distress again; it is about building a robust psychological immune system that can weather life's inevitable storms. Clinical relapse prevention frameworks emphasize the importance of identifying early warning signs—subtle changes in sleep patterns, appetite, social withdrawal, or increased irritability—before full-blown clinical episodes emerge.

By establishing a personalized wellness contract with trusted clinicians, loved ones, and oneself, individuals can activate pre-planned support systems without having to make high-stakes executive decisions while in distress. Creating strong social connection buffers against isolation, while setting healthy boundaries around digital consumption and toxic environments preserves nervous system bandwidth.

Resilience is not the absence of vulnerability; resilience is the capacity to experience vulnerability with self-compassion, knowing that you possess the internal and external resources to navigate difficult terrain. Each time you notice your mind slipping into distress and gently guide it back to safety, you strengthen the neural scaffolding of lasting psychological health.""",

        # Chapter 15: Epilogue: A Testament to Human Dignity, Self-Compassion, and Recovery
        f"""As we conclude this profound investigation into {title}, let us re-anchor in the fundamental truth that defines your worth. If you are currently fighting this silent battle, or if you are supporting someone who is, understand this deeply: you are not weak, you are not permanently broken, and you are not a failure.

The suffering you experience is a real, biological response of a delicate human nervous system navigating immense stress and neurological imbalance. Just as a broken bone requires casting, rest, and rehabilitation, a dysregulated brain requires compassion, evidence-based care, and patient healing.

Recovery is rarely a linear journey. There will be days of gentle progress followed by days where the shadows feel suffocating once again. But with every breath, every compassionate thought toward yourself, and every small step toward professional support, you are actively rewiring your brain. You deserve patience, you deserve dignity, and you deserve healing. Thank you for walking this path of understanding with us today, and we look forward to supporting you in our next psychological documentary."""
    ]

    return "\n\n".join(sections).strip()

def generate_deep_hindi_psychology_script(ep_info: Dict[str, Any]) -> str:
    title = ep_info["title"]
    theme = ep_info["theme"]
    focus = ep_info["focus"]
    ep_num = ep_info["episode"]

    cta_3m = "आगे बढ़ने से पहले, अगर आप या आपका कोई अपना इस खामोश लड़ाई से गुजरा है, तो कृपया इस चैनल को सब्सक्राइब अवश्य करें। हम मानसिक स्वास्थ्य, न्यूरोसाइंस और सच्ची सहानुभूति का एक सुरक्षित मंच तैयार कर रहे हैं ताकि कोई भी अकेला महसूस न करे।"
    cta_10m = "अगर यह वैज्ञानिक विश्लेषण आपको या आपके किसी अपने को समझने में थोड़ी भी मदद कर रहा है, तो इस वीडियो को लाइक करें और नीचे कमेंट में अपने अनुभव या विचार जरूर साझा करें। आपका एक सकारात्मक शब्द किसी जरूरतमंद के लिए उम्मीद की किरण बन सकता है।"
    cta_18m = "मानसिक स्वास्थ्य कोई मंजिल नहीं, बल्कि आत्म-करुणा और धैर्य की एक निरंतर यात्रा है। अपने विचार और सुझाव कमेंट में जरूर साझा करें, और हमारी अगली मनोवैज्ञानिक वृत्तचित्रों से जुड़े रहने के लिए चैनल को सब्सक्राइब करें।"

    sections = [
        # अध्याय 1: भूमिका: कलंक का अंत और वास्तविक पीड़ा
        f"""आज के इस विशेष और गहन मनोवैज्ञानिक वृत्तचित्र में आपका स्वागत है। आज हम मानव मन और मस्तिष्क की एक ऐसी स्थिति की गहराई से वैज्ञानिक और मानवीय जांच कर रहे हैं, जिसे अक्सर समाज में सबसे ज्यादा गलत समझा जाता है: {title}।

मानसिक स्वास्थ्य से जुड़ी चुनौतियों को अक्सर बाहर से देखकर समझना नामुमकिन होता है। हमारा समाज अक्सर गहरी न्यूरोलॉजिकल और भावनात्मक पीड़ा को महज एक चारित्रिक कमजोरी, इच्छाशक्ति की कमी, या आलस मान लेता है। जब कोई इंसान इस गहरी बीमारी के बोझ तले दब रहा होता है, तो अक्सर आसपास के लोग कहते हैं कि सकारात्मक सोचो, सब ठीक हो जाएगा, या बाहर टहल कर आओ। लेकिन आधुनिक न्यूरोसाइंस, क्लिनिकल साइकियाट्री और न्यूरोबायोलॉजी हमें एक बिल्कुल अलग और संवेदनशील सच्चाई बताती हैं। {focus}

{theme} को समझने के लिए हमें मानव मस्तिष्क की उस जटिल रासायनिक संरचना में उतरना होगा जहाँ न्यूरॉन्स, रिसेप्टर्स और न्यूरल सर्किट्स दिन-रात काम करते हैं। मानव तंत्रिका तंत्र एक अत्यंत संवेदनशील संगीत वाद्ययंत्र की तरह है। जब इस स्थिति का प्रभाव पड़ता है, तो मस्तिष्क के मुख्य क्षेत्र—जैसे डीफॉल्ट मोड नेटवर्क, अमिग्डाला, प्रीफ्रंटल कॉर्टेक्स और हिप्पोकैम्पस—अत्यधिक असंतुलन की स्थिति में चले जाते हैं।

उस व्यक्ति की आंतरिक स्थिति की कल्पना कीजिए जो हर सुबह इस एहसास के साथ जागता है। यह केवल उदासी या चिंता नहीं है; यह एक गहरा शारीरिक, मानसिक और अस्तित्वगत थकावट है। मस्तिष्क का रिवॉर्ड सिस्टम यानी खुशी महसूस कराने वाला तंत्र पूरी तरह से सुन्न हो जाता है। छोटी-छोटी दैनिक जिम्मेदारियां किसी पहाड़ चढ़ने जैसी भारी लगने लगती हैं, और व्यक्ति का आंतरिक संवाद एक क्रूर आलोचक में बदल जाता है जो लगातार उसे उसकी असफलताओं की याद दिलाता रहता है।""",

        # 3 मिनट का सब्सक्राइब CTA
        cta_3m,

        # अध्याय 2: न्यूरोकेमिकल संरचना और न्यूरोट्रांसमीटर का असंतुलन
        f"""आइए अब मस्तिष्क की उस सूक्ष्म आणविक दुनिया को समझें जो हमारी भावनाओं, प्रेरणा और मानसिक शांति को नियंत्रित करती है। हमारे मस्तिष्क में लगभग छियासी अरब न्यूरॉन्स होते हैं, जो खरबों सिनैप्टिक सिग्नल्स के माध्यम से रासायनिक संदेशवाहकों—यानी न्यूरोट्रांसमीटर—द्वारा बातचीत करते हैं।

इनमें सबसे प्रमुख है डोपामाइन, जिसे प्रेरणा, लक्ष्य-उन्मुख व्यवहार और खुशी का रसायन कहा जाता है। जब मस्तिष्क के न्यूक्लियस अकम्बेंस में डोपामाइन रिसेप्टर्स कम सक्रिय हो जाते हैं, तो व्यक्ति एनहेडोनिया (Anhedonia) का शिकार हो जाता है। एनहेडोनिया वह स्थिति है जहाँ व्यक्ति उन चीजों में भी कोई खुशी या उत्साह महसूस नहीं कर पाता, जिनसे उसे कभी सबसे ज्यादा लगाव था। पसंदीदा संगीत सुनना, दोस्तों से मिलना, या कोई शौक पूरा करना—सब कुछ बेजान और व्यर्थ लगने लगता है।

इसी तरह सेरोटोनिन हमारे मूड, नींद और भावनात्मक स्थिरता का मुख्य आधार है। जब सेरोटोनिन पाथवे में असंतुलन आता है, तो मस्तिष्क भावनात्मक तनाव को झेलने की अपनी क्षमता खो देता है। इसके अलावा, उत्तेजक ग्लूटामेट और शांत करने वाले गाबा (GABA) न्यूरोट्रांसमीटर के बीच का संतुलन बिगड़ने से तंत्रिका तंत्र लगातार हाइपर-अलर्ट स्थिति में रहने लगता है। यह कोई मानसिक कल्पना नहीं है; यह मस्तिष्क के स्कैन और रक्त परीक्षणों में देखा जाने वाला एक ठोस जैविक तथ्य है।""",

        # अध्याय 3: तनाव का चक्रव्यूह: HPA एक्सिस और कोर्टिसोल का प्रभाव
        f"""अब हम ऑटोनोमिक नर्वस सिस्टम और दीर्घकालिक तनाव के उस शारीरिक प्रभाव को समझेंगे जो पूरे शरीर को भीतर से खोखला कर देता है। हमारे नर्वस सिस्टम के दो मुख्य हिस्से होते हैं: सिम्पैथेटिक नर्वस सिस्टम, जो खतरे के समय हमें लड़ने या भागने (Fight or Flight) के लिए तैयार करता है, और पैरासिम्पैथेटिक नर्वस सिस्टम, जो शरीर को आराम और मरम्मत की स्थिति में लाता है।

जब मस्तिष्क किसी भारी खतरे या भावनात्मक आघात का सामना करता है, तो हाइपोथैलेमिक-पिट्यूटरी-एड्रीनल एक्सिस (HPA Axis) तुरंत सक्रिय हो जाता है। एड्रीनल ग्रंथियां रक्तप्रवाह में कोर्टिसोल और एड्रेनालाईन जैसे तनाव हार्मोन्स की बाढ़ ला देती हैं। किसी तात्कालिक शारीरिक खतरे में यह प्रक्रिया जान बचाती है।

लेकिन जब कोई व्यक्ति लंबे समय तक इस मानसिक बीमारी से जूझता है, तो यह HPA एक्सिस कभी बंद नहीं होता। कोर्टिसोल का लगातार उच्च स्तर मस्तिष्क के हिप्पोकैम्पस क्षेत्र को नुकसान पहुंचाने लगता है, जो याददाश्त और भावनात्मक संदर्भ को नियंत्रित करता है। हिप्पोकैम्पस में नए न्यूरॉन्स का बनना रुक जाता है, जबकि अमिग्डाला—जो मस्तिष्क का डर का अलार्म है—अत्यधिक संवेदनशील हो जाता है। इसके परिणामस्वरूप, व्यक्ति हर सामान्य बात में भी किसी भयानक अनहोनी का डर महसूस करने लगता है।""",

        # अध्याय 4: पॉलीवेगल थ्योरी और फ्रीज रिस्पॉन्स
        f"""डॉ. स्टीफन पोर्जेस द्वारा प्रतिपादित पॉलीवेगल थ्योरी (Polyvagal Theory) हमें यह समझने में गहरी अंतर्दृष्टि देती है कि मानसिक आघात और अत्यधिक तनाव में इंसान का शरीर कैसे प्रतिक्रिया करता है। वेगस नर्व, जो हमारे मस्तिष्क से लेकर पेट, हृदय और फेफड़ों तक फैली होती है, हमारे तंत्रिका तंत्र का सबसे मुख्य राजमार्ग है।

पॉलीवेगल संरचना के अनुसार, जब खतरा इतना बड़ा हो जाता है कि लड़ना या भागना संभव नहीं रहता, तो नर्वस सिस्टम अपनी सबसे पुरानी रक्षा प्रणाली को सक्रिय करता है: डॉर्सल वेगल शटडाउन (Dorsal Vagal Shutdown)। यह एक शारीरिक फ्रीज (Freeze) अवस्था है।

इस अवस्था में हृदय गति धीमी हो जाती है, ऊर्जा का स्तर शून्य हो जाता है, और चेतना एक प्रकार के मानसिक सुन्नपन या विरक्ति में चली जाती है। जो लोग गंभीर डिप्रेशन या आघात से पीड़ित होते हैं, वे अक्सर खुद को शारीरिक रूप से पंगु और भावनाओं से कटा हुआ महसूस करते हैं। यह जानना बेहद जरूरी है कि यह कोई आलस या अनिच्छा नहीं है; यह आपके नर्वस सिस्टम द्वारा आपको असहनीय मानसिक दर्द से बचाने के लिए उठाया गया एक जैविक कदम है।""",

        # अध्याय 5: हार्मोनल संतुलन और थायरॉयड का गहरा प्रभाव
        f"""नर्वस सिस्टम के साथ-साथ हमारे शरीर का एंडोक्राइन यानी हार्मोनल सिस्टम भी मानसिक स्थिति को गहराई से प्रभावित करता है। हमारी गर्दन में स्थित थायरॉयड ग्रंथि जो हार्मोन्स बनाती है, वे मस्तिष्क की हर कोशिका की ऊर्जा उत्पादन गति को नियंत्रित करते हैं।

जब थायरॉयड हार्मोन का स्तर कम हो जाता है, जिसे सबक्लिनिकल हाइपोथायरायडिज्म कहते हैं, तो मस्तिष्क में सेरोटोनिन और डोपामाइन का निर्माण धीमा हो जाता है। व्यक्ति को अत्यधिक सुस्ती, निराशा और गहरा अवसाद महसूस होने लगता है, जिसे कई बार गलत समझकर केवल मानसिक कमजोरी मान लिया जाता है।

इसी प्रकार, महीनों तक अत्यधिक तनाव में रहने के बाद एड्रीनल ग्रंथियां थक जाती हैं। सुबह के समय कोर्टिसोल का स्तर गिर जाता है, जिससे व्यक्ति सुबह उठते ही भारी थकावट महसूस करता है लेकिन रात में बेचैनी के कारण सो नहीं पाता। इन अंतःस्रावी ग्रंथियों और न्यूरोट्रांसमीटर्स का संतुलन सुधारना मन की शांति के लिए अत्यंत आवश्यक है।""",

        # अध्याय 6: डीफॉल्ट मोड नेटवर्क (DMN) और आत्म-आलोचना का भंवर
        f"""मस्तिष्क की इस पीड़ा को और गहराई से समझने के लिए हमें डीफॉल्ट मोड नेटवर्क यानी DMN को समझना होगा। यह मस्तिष्क के कई क्षेत्रों का एक नेटवर्क है जो तब सक्रिय होता है जब हम कोई बाहरी काम नहीं कर रहे होते—जैसे खाली बैठना, अपने बारे में सोचना, या पुरानी यादों में खो जाना।

एक स्वस्थ व्यक्ति में, जैसे ही वह किसी काम पर ध्यान केंद्रित करता है, यह डीफॉल्ट मोड नेटवर्क शांत हो जाता है। लेकिन क्लिनिकल अध्ययनों से पता चलता है कि अवसाद, गंभीर चिंता और मानसिक विकारों से पीड़ित लोगों में यह नेटवर्क असामान्य रूप से अति-सक्रिय और आपस में कसकर बंध जाता है।

इसके कारण व्यक्ति नकारात्मक विचारों के एक अंतहीन भंवर में फंस जाता है जिसे रूमिनेशन (Rumination) कहा जाता है। मस्तिष्क बार-बार पुरानी गलतियों, पछतावे और असफलताओं को दोहराता रहता है। चेतना पर एक ऐसा गहरा चश्मा चढ़ जाता है जिसके माध्यम से भविष्य केवल अंधकारमय और निराशाजनक दिखाई देता है। व्यक्ति अपने ही विचारों का बंदी बन जाता है, और उसका मन लगातार यह झूठा संदेश देता है कि वह किसी के प्यार या सम्मान के योग्य नहीं है।""",

        # अध्याय 6: दैनिक जीवन की जमीनी सच्चाई और सामाजिक मुखौटा
        f"""आइए अब उस इंसान के दैनिक जीवन के अनुभव को समझें जो हर रोज इस स्थिति का मुकाबला करता है। बाहर से देखने पर वह एक सामान्य इंसान लग सकता है—जो ऑफिस जाता है, परिवार के साथ बैठता है, और कभी-कभी मुस्कुरा भी देता है। समाज अक्सर इस मुस्कान को देखकर मान लेता है कि वह पूरी तरह ठीक है।

लेकिन उस सामाजिक मुखौटे के पीछे ऊर्जा का एक भारी क्षय छुपा होता है। सुबह बिस्तर से उठना, नहाना, या नाश्ता बनाना भी किसी भारी जंग की तरह लगता है। प्रीफ्रंटल कॉर्टेक्स की कार्यक्षमता कमजोर होने के कारण साधारण निर्णय लेना भी अत्यधिक कष्टकारी हो जाता है। दिनभर खुद को सामान्य दिखाने की कोशिश में शाम तक मानसिक ऊर्जा पूरी तरह समाप्त हो जाती है।

जब वह शाम को घर लौटता है, तो उसके पास बात करने तक की ताकत नहीं बचती। दोस्त और रिश्तेदार अक्सर इस चुप्पी को उपेक्षा या घमंड समझ लेते हैं, जिससे व्यक्ति और अधिक अकेला पड़ जाता है। यह अकेलापन उसके भीतर इस अपराधबोध को और गहरा कर देता है कि वह अपने चाहने वालों पर एक बोझ बन चुका है।""",

        # 10 मिनट का लाइक और कमेंट CTA
        cta_10m,

        # अध्याय 7: गट-ब्रेन एक्सिस: पेट और दिमाग का गहरा नाता
        f"""आधुनिक चिकित्सा विज्ञान ने हाल के वर्षों में एक क्रांतिकारी खोज की है: हमारा मानसिक स्वास्थ्य हमारे पेट के स्वास्थ्य से सीधे तौर पर जुड़ा हुआ है। हमारी आंतों में पांच सौ मिलियन से अधिक न्यूरॉन्स होते हैं, जिसे वैज्ञानिकों ने 'दूसरा मस्तिष्क' (Second Brain) नाम दिया है।

इसके अलावा, हमारे पाचन तंत्र में खरबों लाभकारी सूक्ष्मजीव यानी माइक्रोबायोम रहते हैं, जो महत्वपूर्ण न्यूरोकेमिकल्स का निर्माण करते हैं। क्या आप जानते हैं कि हमारे शरीर का लगभग नब्बे प्रतिशत सेरोटोनिन और पचास प्रतिशत डोपामाइन हमारे पेट में बनता है?

जब खराब खानपान, अत्यधिक तनाव या एंटीबायोटिक्स के कारण आंतों का माइक्रोबायोम असंतुलित हो जाता है, तो आंतों की दीवारें कमजोर हो जाती हैं। इससे विषैले तत्व रक्तप्रवाह में प्रवेश करते हैं, जिससे सिस्टेमिक इन्फ्लेमेशन यानी सूजन पैदा होती है। यह सूजन वेगस नर्व के माध्यम से मस्तिष्क तक पहुंचती है, जहाँ यह ब्रेन फॉग, घबराहट और गहरे अवसाद को जन्म देती है। इसलिए, मन को शांत करने के लिए पेट और पाचन स्वास्थ्य पर ध्यान देना एक अनिवार्य कदम है।""",

        # अध्याय 8: नींद का चक्र और मस्तिष्क की सफाई
        f"""पेट के स्वास्थ्य के साथ-साथ, नींद हमारे मानसिक संतुलन का सबसे मजबूत स्तंभ है। गहरी नींद के तीसरे चरण (Slow-Wave Sleep) के दौरान मस्तिष्क का ग्लिम्फैटिक सिस्टम (Glymphatic System) सक्रिय होता है। यह एक प्राकृतिक सफाई तंत्र है जो मस्तिष्क के न्यूरॉन्स के बीच जमा होने वाले विषाक्त पदार्थों को धोकर बाहर निकालता है।

इसके साथ ही, आर.ई.एम. नींद (REM Sleep) हमारे भावनात्मक अनुभवों के लिए एक सुरक्षित चिकित्सालय की तरह काम करती है। सपने देखने के दौरान मस्तिष्क भावनात्मक यादों को सुलझाता है और उनके दर्दनाक तनाव को समाप्त करता है।

लेकिन जब क्रोनिक अनिद्रा या अवसाद के कारण नींद का यह चक्र टूट जाता है, तो मस्तिष्क की सफाई रुक जाती है। पुरानी दर्दनाक भावनाएं कच्ची और ज्वलंत बनी रहती हैं, जिससे जागने पर अमिग्डाला अत्यधिक घबराहट के सिग्नल भेजने लगता है। नींद को ठीक करना किसी भी मानसिक स्वास्थ्य सुधार की पहली और सबसे महत्वपूर्ण सीढ़ी है।""",

        # अध्याय 9: वयस्क न्यूरोप्लास्टिसिटी: मस्तिष्क के पुनर्जीवन का विज्ञान
        f"""इस घने अंधकार के बीच, आधुनिक न्यूरोसाइंस हमें सबसे बड़ी और सच्ची आशा देती है: एडल्ट न्यूरोप्लास्टिसिटी (Adult Neuroplasticity)। दशकों तक यह माना जाता था कि वयस्क होने के बाद मस्तिष्क की बनावट को बदला नहीं जा सकता। लेकिन आज विज्ञान साबित कर चुका है कि हमारा दिमाग जीवन के किसी भी पड़ाव पर नए न्यूरल पाथवे बनाने और खुद को दोबारा ठीक करने की क्षमता रखता है।

इस प्रक्रिया का मुख्य आधार है बी.डी.एन.एफ. (Brain-Derived Neurotrophic Factor), जिसे मस्तिष्क का उर्वरक कहा जाता है। जब कोई व्यक्ति सही मनोचिकित्सा, हल्का व्यायाम, पोषण और भावनात्मक समर्थन प्राप्त करता है, तो मस्तिष्क में BDNF का स्तर बढ़ने लगता है।

हिप्पोकैम्पस में नए न्यूरॉन्स का जन्म होता है—जिसे न्यूरोजेनेसिस कहते हैं। पुराने नकारात्मक और भयभीत रास्तों की जगह नए, लचीले और शांत न्यूरल कनेक्शन बनने लगते हैं। आप जैसे हैं, हमेशा वैसे रहने के लिए अभिशप्त नहीं हैं; आपका मस्तिष्क सक्रिय रूप से ठीक होने और बदलने के लिए डिजाइन किया गया है।""",

        # अध्याय 10: साक्ष्य-आधारित मनोचिकित्सा और उपचार
        f"""वैज्ञानिक रूप से प्रमाणित मनोचिकित्सा के माध्यम से इस हाइपर-एक्टिव डीफॉल्ट मोड नेटवर्क को शांत किया जा सकता है। कॉग्निटिव बिहेवियरल थेरेपी (CBT) में व्यक्ति उन नकारात्मक स्वचालित विचारों की पहचान करना सीखता है जो वास्तविकता से कोसों दूर होते हैं।

एक्सेप्टेंस एंड कमिटमेंट थेरेपी (ACT) हमें यह सिखाती है कि हम अपने विचारों से लड़ना बंद करें और उन्हें आकाश में तैरते बादलों की तरह देखें—विचार केवल विचार हैं, वे आपकी पहचान नहीं हैं। वहीं डायलेक्टिकल बिहेवियर थेरेपी (DBT) तीव्र भावनात्मक उतार-चढ़ाव को संभालने और रिश्तों में स्थिरता लाने की मजबूत तकनीकें देती है।

इसके अलावा, सोमैटिक एक्सपीरियंसिंग और ई.एम.डी.आर. (EMDR) जैसी पद्धतियां शरीर में दबे हुए अनकहे आघात को मुक्त करने में मदद करती हैं। आज की आधुनिक साइकियाट्री में सटीक दवाएं और न्यूरोमॉड्यूलेशन तकनीकें उन लोगों के लिए भी नए रास्ते खोल रही हैं जो लंबे समय से खुद को असाध्य मान चुके थे।""",

        # 18 मिनट का कम्युनिटी और सब्सक्राइब CTA
        cta_18m,

        # अध्याय 11: नर्वस सिस्टम को शांत करने के दैनिक शारीरिक अभ्यास
        f"""अपने तंत्रिका तंत्र को सुरक्षा का संदेश देने के लिए हम केवल सोच पर निर्भर नहीं रह सकते; हमें अपने शरीर के माध्यम से मस्तिष्क से बात करनी होगी। न्यूरोबायोलॉजिस्ट्स ने ऐसे कई शक्तिशाली अभ्यास खोजे हैं जो मिनटों में तनाव को कम कर सकते हैं।

इनमें सबसे प्रभावी है फिजियोलॉजिकल साई (Physiological Sigh)। इसमें नाक से दो बार गहरी सांस ली जाती है—एक लंबी सांस और उसके तुरंत बाद एक छोटी सांस—और फिर मुंह से धीरे-धीरे पूरी सांस बाहर छोड़ दी जाती है। दिन में केवल तीन से चार बार ऐसा करने से फेफड़ों में कार्बन डाइऑक्साइड का स्तर संतुलित होता है और वेगस नर्व तुरंत हृदय गति को धीमा करके शांति का सिग्नल भेजती है।

इसके साथ ही, सुबह उठने के तीस मिनट के भीतर प्राकृतिक धूप में दस से पंद्रह मिनट बिताना हमारे सर्केडियन रिदम को रीसेट करता है, जिससे दिन में ऊर्जा और रात में गहरी नींद मिलती है। प्रकृति में बिना जूते घास पर चलना, ठंडे पानी से चेहरा धोना, और नॉन-स्लीप डीप रेस्ट (NSDR) नर्वस सिस्टम को यह याद दिलाते हैं कि आप इस क्षण सुरक्षित हैं।""",

        # अध्याय 12: पुनरावृत्ति की रोकथाम और आत्म-करुणा की शक्ति
        f"""मानसिक स्वास्थ्य का मतलब यह नहीं है कि आपके जीवन में कभी कोई दुख या तनाव नहीं आएगा। इसका अर्थ यह है कि जब भी कोई तूफान आए, तो आपके पास उससे निपटने का एक मजबूत आंतरिक ढांचा मौजूद हो।

क्लिनिकल रिलैप्स प्रिवेंशन हमें यह सिखाता है कि हम अपने व्यक्तिगत चेतावनी संकेतों को समय रहते पहचानें—जैसे नींद में अचानक बदलाव, भूख का कम होना, या लोगों से दूरी बनाना। जब आप इन संकेतों को पहले ही पहचान लेते हैं, तो आप संकट गहराने से पहले ही अपने डॉक्टर, परिवार या आत्म-देखभाल प्रणाली को सक्रिय कर सकते हैं।

याद रखिए, खुद के प्रति कठोर होना कभी किसी को ठीक नहीं कर पाया। आत्म-करुणा (Self-Compassion) का मतलब है कि जब आप लड़खड़ाएं, तो खुद को कोसने के बजाय वही दया और सहारा दें जो आप किसी रोते हुए प्रियजन को देते।""",

        # अध्याय 13: उपसंहार: मानवीय गरिमा, सम्मान और आशा
        f"""जैसे ही हम {title} के इस गहन और वैज्ञानिक विश्लेषण के अंत की ओर बढ़ते हैं, अपने मन में इस सच्चाई को गहराई से बसा लीजिए: यदि आप इस मूक और कठिन लड़ाई को लड़ रहे हैं, तो आप कमजोर नहीं हैं, आप टूटे हुए नहीं हैं, और आप कोई बोझ नहीं हैं।

आपकी यह पीड़ा एक संवेदनशील मानव मस्तिष्क की वास्तविक जैविक प्रतिक्रिया है जो अत्यधिक दबाव और रासायनिक असंतुलन से जूझ रहा है। जिस प्रकार एक टूटी हुई हड्डी को प्लास्टर, आराम और समय की आवश्यकता होती है, उसी प्रकार एक थके हुए मस्तिष्क को करुणा, सही चिकित्सा और धैर्य की जरूरत होती है।

ठीक होने का रास्ता हमेशा सीधा नहीं होता। ऐसे दिन आएंगे जब आप आगे बढ़ेंगे, और ऐसे दिन भी आएंगे जब अंधेरा फिर से भारी लगेगा। लेकिन हर गहरी सांस के साथ, खुद के प्रति हर दयालु विचार के साथ, आप अपने मस्तिष्क को दोबारा गढ़ रहे हैं। आप सम्मान, गरिमा और एक खुशहाल जीवन के हकदार हैं। हमारे साथ इस यात्रा पर चलने के लिए आपका हृदय से धन्यवाद, और हम जल्द ही अपनी अगली मनोवैज्ञानिक वृत्तचित्र में आपसे मिलेंगे।"""
    ]

    return "\n\n".join(sections).strip()

def generate_deep_script_content(ep_info: Dict[str, Any], niche: str) -> str:
    """
    Main entry point for generating comprehensive >20 minute documentary narration.
    - Trading: English (~3,150 to 3,400 words, ~22 to 24 mins)
    - Psychology: Hindi (~2,750 to 2,900 words, ~21.5 to 23 mins)
    """
    if niche == "trading":
        return generate_deep_trading_script(ep_info)
    else:
        return generate_deep_hindi_psychology_script(ep_info)
