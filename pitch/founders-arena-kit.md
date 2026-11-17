# THE COMPLETE FOUNDER'S ARENA KIT — OST.io

Day 2 final pitch. 5:00 pitch + live demo STRICT, 5:00 Q&A, repo link
submitted. This file is the single print-out: script, business, Q&A, drills.

## 0. Morning checklist (before 9:00 AM)

- [ ] Whole team present BEFORE 9:00 — event starts on the hour
- [ ] Repo made PUBLIC (GitHub → Settings → General → Danger Zone → Change
      visibility), then submit the `main` branch link — a private repo 404s
- [ ] Demo machine: power adapter in, video adapter packed, volume tested,
      app launched once to warm up
- [ ] Backup on the machine: screen recording of the stub demo + one preset
      playback
- [ ] Every member reads section 5 (Q&A) — questions can go to anyone
- [ ] One printed copy of the numbers cheat sheet per person

## 1. The 5:00 pitch — word for word (rehearse to 4:30)

### 0:00–0:40 — THE HOOK (P5)

> [Full-screen the YuE2 ComfyUI node-graph image]
> "This is what an indie game developer faces today if they want one original
> song in their game. Fifteen nodes. Acoustic tokens. A machine-learning
> workflow. The alternative: hire a composer at $50 to $500 PER MINUTE of
> music. So most indie devs ship games with no original music at all.
> We fix that. OST.io — game words in, game music out."

### 0:40–2:50 — LIVE DEMO (P4's hands, P1 calling)

| Click | Do | Say |
|---|---|---|
| 1 | Open the app (dark UI, "Game words in. Game music out." header) | "This is the entire interface." |
| 2–5 | Dropdowns: Boss Battle (Phase 1/2) → Menacing/Ominous → Dark Orchestral + Brass → High Adrenaline (120–150 BPM) | One line per click: "Big fight music — phase changes just swap the mood dropdown." |
| 6 | Boss-lore box: "A giant clockwork automaton covered in rust, weeping oil as it attacks." | "One sentence of game lore — no prompt engineering." |
| 7 | Open "Show Compiled Prompt" | "Watch the translation — game words became music prompts." |
| 8 | Press GENERATE TRACK — progress bar starts | "That will take about a minute, and that's honest — watch what it's planning." |
| 9 | Open the ABC score panel; scroll slowly | "The model plans melody and chords as symbols first — the dev sees what they're getting. No music theory required." |
| 10 | Click the Boss preset — instant playback | [let it play 5–10 seconds at full volume] |
| 11 | Full-screen `boss-fight-mock.png` while track plays | "This track took one minute on an 8 GB gaming laptop." |

### 2:50–3:30 — HOW IT WORKS (P3)

> "Under the hood is YuE2 — the first open-source model to outscore Suno v5
> on the WildSongBench benchmark. It plans the melody and chords as a
> symbolic score, then synthesizes 48-kilohertz stereo audio. It runs
> entirely locally — this app runs on an 8 gigabyte gaming laptop in
> low-VRAM mode, about a minute per song. No cloud. No subscription.
> Nothing leaves the machine."

### 3:30–4:10 — BUSINESS (P2)

> "The AI music generator market is over a billion dollars in 2026, heading
> to six billion by 2035. Our model: free forever for individuals — the
> license explicitly lets indie devs monetize royalty-free. Studios legally
> need a commercial model license, so we bundle compliance, updates and
> support into a studio license, $499 to $2,499 a year. A cloud tier at
> $9–19 a month for devs without GPUs. Enterprise from $25K for plugins and
> fine-tunes. And a preset marketplace on a 70-30 split."

### 4:10–4:45 — THE ASK (team lead)

> "We're raising $400,000 on a SAFE — $3.6M pre, $4M post — for 10 percent.
> Use of funds: the commercial model license that unlocks studio revenue,
> Unity and Unreal plugins, and two engineers. Eighteen-month milestones:
> license signed → 10,000 downloads → 100 paying studios → $120K ARR.
> And for scale: Suno just raised $400 million at a $5.4 billion valuation.
> We're priced at the floor of this category — with a working product."

### 4:45–5:00 — THE CLOSE (P5)

> [Track playing over the boss-fight screen]
> "The weights live on the dev's machine. Their GPU, their music, their
> game. OST.io — compose in game design, not in acoustic tokens."

## 2. The business model (full detail)

| Layer | Price | Who | Why it works |
|---|---|---|---|
| Free | $0 forever | Individual devs, jammers, creators | License lets individuals monetize → growth engine + community |
| Studio License | $499–$2,499/yr | Companies using it commercially | Companies legally need a commercial model license — we bundle compliance + updates + support |
| Cloud | $9–19/mo | Devs without gaming GPUs | Same dropdowns, rented GPUs, licensed weights |
| Enterprise | $25K+/yr | Studios, agencies | Unity/Unreal plugins, fine-tunes on their IP, SLAs |
| Marketplace | 70-30 rev share | Sound designers | "Soulslike Boss Pack" etc. — creators become the salesforce |

Revenue model summary: free-to-paid ladder (individual → studio →
enterprise) + usage-based cloud + marketplace take-rate. Recurring revenue
from tiers 2–4, viral acquisition from tier 1, ecosystem lock-in from tier 5.

## 3. Valuation justification (the Shark Tank math)

Say it in exactly this order:

1. "We're priced at the floor of the category." Udio reached a $200M+
   valuation on ~$3M revenue. 2026 pre-seed AI norms are $3–8M post-money.
   We ask $4M post — the bottom of the standard band — with a working product.
2. "The market prices AI music as winner-take-most." Suno: $400M raise at
   $5.4B (June 2026), ~18x its $300M ARR, valuation doubled in 7 months.
   ElevenLabs: $11B.
3. "Our market is $1B+ today, growing 20–30% a year." Narrow scope:
   $1.06B → $6.26B by 2035. Broad: $5.55B → $12.86B by 2030.
4. "What $400K buys:" the commercial license (the revenue unlock), plugins
   (distribution), two engineers — 18 months of runway to $120K ARR.

NEVER say "our company is worth $4M" — say "we're raising at a $4M
post-money cap."

## 4. Investment ask & equity (exact structure)

| Item | Value |
|---|---|
| Instrument | Post-money SAFE (simplest, investor-friendly) |
| Ask | $400,000 |
| Valuation cap | $4M post-money ($3.6M pre) |
| Equity given | 10% (at the cap; MFN clause included) |
| Use of funds | ~40% commercial model license & legal · ~30% two engineers · ~20% Unity/Unreal plugin dev · ~10% cloud GPU for the Cloud tier |
| Milestones (18 mo) | License signed → 10K downloads → 100 studios → $120K ARR → priced Series A |
| Exit paths | Unity/Epic/Adobe (distribution) · label-tech (licensing) · Series A |

## 5. Q&A — all five domains (every member memorizes)

### Technical
- How does it work? Open-source YuE2 model (symbolic planning + flow
  matching) behind a Gradio UI, 100% local. Dropdowns compile to the model's
  prompt format; output is 48 kHz stereo + editable ABC score.
- Doesn't this need a data center? No — runs on 8 GB VRAM in low-VRAM mode
  (official spec 24 GB). We demo on the podium laptop.
- Vocals leaking into instrumentals? Empty lyrics + instrumental tags, plus
  a score-level fallback that re-renders ghost vocals away.
- Can I set exact song length? "There is no duration parameter — the UI
  reports the real length and any truncation; precise length control via ABC
  editing is on the roadmap." (Never invent API parameters.)
- Why YuE2 over MIT-licensed models like ACE-Step? Quality (outscored Suno v5
  on WildSongBench) + the editable score — and our compiler is
  model-agnostic, so the engine is swappable.

### Business
- Target customer? Indie game devs first (music is the #1 skipped asset;
  outsourcing $50–500/min), then creators, then studios.
- Suno copies your dropdowns — then what? Their model REQUIRES cloud GPUs
  and subscriptions; ours is architecturally opposite: zero marginal cost on
  hardware the customer owns. First-mover in game vocabulary + marketplace.
- Who pays when individuals are free? Companies legally need a commercial
  model license — we bundle it. The license is the moat turned into revenue.
- Biggest risk? Model-license dependence — mitigated by the model-agnostic
  compiler (ACE-Step is the MIT fallback).

### Marketing
- GTM? Game jams + itch.io first, r/gamedev, YouTube demos. Every generated
  track credits OST.io — the product is its own ad.
- CAC? Near zero — sharing is built into the output; marketplace creators
  are the salesforce.

### Financial
- Unit economics? Studio license ~$1K/yr at ~$200 support cost → ~80%
  margin. Cloud: ~$0.03 GPU cost/song vs $10–15/mo subs.
- Break-even? ~100 studios + 300 cloud subs ≈ $130K ARR — inside 18 months.

### Investment
- Justify $4M with no revenue? Section 3's four-step answer.
- Structure? $400K SAFE, $4M cap, MFN, 10%.
- Exit? Table in section 4.
- What if the model creators change terms? Multi-model architecture;
  commercial-license revenue path; compiler swaps engines.

### The two lines that must ALWAYS be said correctly
1. "Individual devs monetize royalty-free (CC BY-NC 4.0 + creator
   permission). Studios buy a license." — NEVER "copyright-free".
2. "Runs on an 8 GB gaming laptop with low-VRAM mode; official spec is 24 GB."

## 6. Slide plan (PPT optional — max 8, use 6)

| # | Slide | Content |
|---|---|---|
| 1 | Title | OST.io — "Game words in. Game music out." + team |
| 2 | Problem | Node-graph screenshot + "$50–500 per minute" |
| 3 | Product | 2 app screenshots (dropdowns / ABC score) |
| 4 | Architecture | One diagram: dropdowns → compiler → YuE2 (local GPU) → WAV + ABC |
| 5 | Business | Market line + revenue table (5 rows) |
| 6 | The Ask | $400K · $4M post · 10% · use of funds · milestones · Suno anchor |

Build in Google Slides (all 5 can edit), download as .pptx to the demo
machine — never depend on venue wifi. Business content = slides 5–6 only;
never read slides aloud.

## 7. Failure drills

- Live generation errors/OOM on stage: the app shows a friendly red message
  → click a different preset, keep talking. NEVER debug live.
- Whole app dead: play the pre-recorded backup video over the boss mock.
  The pitch does not stop for technology.
- Ghost vocals in a preset: swap presets — the fix button is rehearsal-only.
- Timer warning at 4:30: skip straight to the close line. Ending at 4:45
  beats negative marks.

## 8. The three sentences of team discipline

1. TIME: the clock is a judge — 4:30 is the target, 5:00 is a hard wall.
2. HANDS: only P4 touches the machine after 2:40; everyone else presents
   facing the judges.
3. NUMBERS: every member can say the eight cheat-sheet numbers cold — that
   is the "every member understands the product" requirement, satisfied.

## Numbers cheat sheet (print one per person)

| Number | Fact |
|---|---|
| $1.06B | AI music generator market, 2026 (narrow) → $6.26B by 2035 |
| $5.55B | AI-in-music market, 2026 (broad) → $12.86B by 2030, 23.4% CAGR |
| $5.4B | Suno valuation, June 2026 ($400M Series D, $300M ARR, 2M subscribers) |
| $200M+ | Udio valuation at ~$3M revenue |
| 8 GB | VRAM we run on (low-VRAM mode); official spec 24 GB |
| ~1 min | Generation time per song on a consumer GPU |
| $400K / 10% | Ask: SAFE, $3.6M pre / $4M post, MFN |
| $120K ARR | 18-month milestone (~100 studios + 300 cloud subs = break-even) |
