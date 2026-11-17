# Q&A Cards — every member carries these. Q&A goes to ANYONE.

One line each. Say the line, stop talking, wait for the next question.

---

## Numbers to memorize (say these cold)

| Number | Fact |
|---|---|
| $1.06B | AI music generator market, 2026 (narrow scope) → $6.26B by 2035 |
| $5.55B | AI-in-music market, 2026 (broad) → $12.86B by 2030, 23.4% CAGR |
| $5.4B | Suno valuation, June 2026 Series D ($400M, Bond Capital; $300M ARR, 2M subscribers) |
| $200M+ | Udio valuation at ~$3M revenue — proof early AI-music gets valued on market |
| 8 GB | VRAM we run on (low-VRAM mode); official spec 24 GB |
| ~1 min | Generation time per song on a consumer GPU |
| $400K / 10% | Our ask: SAFE, $3.6M pre / $4M post-money, MFN clause |
| $120K ARR | 18-month milestone (~100 studios + 300 cloud subs = break-even) |

## Card 1 — License

> "Individual devs sell games with YuE2 music royalty-free
> (CC BY-NC 4.0 + creator permission). Studios license it."

**NEVER say "copyright-free".** If pressed: individual creators get royalty-free
use for their games under CC BY-NC 4.0 plus the model creators' permission;
commercial studios beyond that scope negotiate a license.

## Card 2 — Hardware

> "Runs on an 8 GB gaming laptop with low-VRAM mode; official spec is 24 GB."

(That laptop is the one on the podium. `low_vram` is a supported
`from_pretrained` flag — see `API_NOTES.md`.)

## Card 3 — Why local

> "No cloud, no subscription, no takedowns — the weights are on the dev's machine."

If pressed: nothing leaves the laptop; the music ships with the game forever,
even if a service shuts down.

## Card 4 — Why YuE2

> "First open model to outscore Suno v5 on WildSongBench."

If pressed: and it's the *editable* kind of generation — YuE2 plans the melody
and chords as an ABC score first, which is exactly what our UI surfaces.

## Card 5 — Duration / "can I set exact length?"

> "There is no duration parameter — the UI reports the real length and any
> truncation, and precise length control via ABC editing is on the roadmap."

Never invent a YuE2 API parameter on stage (see `API_NOTES.md`).

## Card 6 — Target customer

> "Indie game devs first — music is the #1 asset they skip, and outsourcing
> costs $50–500 per minute. Then content creators, then studios."

## Card 7 — Competition / "Suno will copy you"

> "Their business model requires cloud GPUs and subscriptions; ours is the
> opposite — zero marginal cost on hardware the customer already owns."

If pressed: first-mover in game-dev vocabulary mapping, plus a preset
marketplace community. And if M-A-P ever changes terms, our compiler is
model-agnostic — ACE-Step (MIT) is the fallback engine.

## Card 8 — Who pays, when individuals are free?

> "Companies legally need a commercial model license — we bundle compliance,
> updates and support into one Studio purchase."

## Card 9 — Go-to-market / CAC

> "Game jams and itch.io first, r/gamedev and YouTube next — every generated
> track credits OST.io, so the product is its own ad. Near-zero CAC."

## Card 10 — Revenue model & unit economics

> "Free for individuals · Studio $499–2,499/yr · Cloud $9–19/mo ·
> Enterprise $25K+ · Marketplace 70-30. Studio margin is ~80%."

Break-even: ~100 studio licenses + 300 cloud subs ≈ $130K ARR, inside 18 months.

## Card 11 — "Justify $4M with zero revenue"

> "Udio hit $200M+ at ~$3M revenue; pre-seed AI norms are $3–8M post; we're
> priced at the floor with a working product and a billion-dollar market."

Suno trades at ~18× ARR — the market prices AI music as winner-take-most.

## Card 12 — Structure & exit

> "$400K on a post-money SAFE, $4M cap, MFN — 10%. Exit: Unity/Epic/Adobe
> acquire distribution, label-tech acquires licensing, or Series A on
> milestones (license → 10K downloads → 100 studios → $120K ARR)."

---

### Hard rules (from AGENTS.md / plan §10)

- License question → Card 1 wording. **Never "copyright-free".**
- Never invent a YuE2 API parameter on stage. If asked for one that doesn't
  exist (e.g. "can I set exact duration?"), the honest answer is Card 5.
