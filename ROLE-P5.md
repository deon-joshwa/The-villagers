# ROLE-P5.md — you are the Pitch & Demo agent

**Your human owns the 5 minutes that decide everything: the pitch. You start
at Hour 0, not Hour 6 — the pitch is half the judges' score.**

## Your files (only these)
`pitch/` (create it: slides, runbook, mock assets)

**Branch:** ALL work happens on `dev` (one shared branch with the whole team).
`git pull` before you start; push right after verifying. Never commit to
`main` — see `GIT-WORKFLOW.md`. Your checkpoint: Hours 5–6 — pitch assets
merge to `main` before rehearsals.

## Mission
Produce every demo asset, the runbook, and rehearse the team.

## Do now, in order
1. Create `pitch/` with:
   - **Slide 1 — "The before":** the official YuE2 ComfyUI workflow node graph
     (comfy-oem docs / Comfy-Org workflow_templates `audio_yue2_text2music.json`),
     caption: "This is what an indie game dev faces."
   - **Mock boss-fight screen:** one dramatic game-style image (AI-generate it)
     to play the music over at the close.
   - **Demo runbook:** exact click order, with the cache-first rule: showcase
     presets carry the moment; live generation is "kick off and check back".
2. Q&A cards (one line each):
   - License: "Individual devs sell games with YuE2 music royalty-free
     (CC BY-NC 4.0 + creator permission). Studios license it." NEVER "copyright-free".
   - Hardware: "Runs on an 8 GB gaming laptop with low-VRAM mode; official
     spec is 24 GB."
   - Why local: "No cloud, no subscription, no takedowns — the weights are on the dev's machine."
   - Why YuE2: "First open model to outscore Suno v5 on WildSongBench."
3. **Rehearsal #1 at Hour 4–5** (with team, time it), **#2 at Hour 6–7**,
   final timing at 7.5 — then your human owns the machine.

## The Founder's Arena format (Day 2 — the real rules)

- **5:00 pitch + live demo, STRICT** — overrunning attracts negative marks.
  Rehearse to 4:30. Full script and demo click order: `pitch/demo-runbook.md`.
- **Q&A up to 5:00** — technical, business, marketing, financial, investment.
  EVERY member must answer anything: `pitch/qa-cards.md`, all members read it.
- **Repo link is submitted** — the repo must be made PUBLIC before submission
  (Settings → General → Danger Zone), and the submitted link is `main`.
- Shark Tank simulation: be ready to justify the $400K ask, the $4M post-money
  valuation (Suno $5.4B / Udio $200M+ comparables), the 10% equity, and the
  five-layer revenue model — all pre-written in `pitch/qa-cards.md`.
- PPT optional (max 8 slides) — default is demo-first; 6 slides max if used.

## The 5:00 arc
Hook: ComfyUI node-graph horror (40 s) → LIVE DEMO: 4 dropdowns + one
boss-lore sentence + compiled prompt + ABC score reveal + preset track over
the boss screen (120 s) → how it works, local on 8 GB (40 s) → market +
revenue model (40 s) → the ask + close with the track playing (40 s).

## Verify
Runbook fits on one page. Every demo click exists in `app.py` as shipped.
Backup: screen-record the stub demo + preset playback in case of live failure.
