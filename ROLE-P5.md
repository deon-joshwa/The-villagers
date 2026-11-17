# ROLE-P5.md — you are the Pitch & Demo agent

**Your human owns the 3 minutes that decide everything: the pitch. You start at
Hour 0, not Hour 6 — the pitch is half the judges' score.**

## Your files (only these)
`pitch/` (create it: slides, runbook, mock assets)

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

## The 3-minute arc (from plan §9)
ComfyUI node-graph horror (40 s) → 4 dropdowns + one boss-lore sentence + show
the compiled prompt (50 s) → the ABC score reveal while the progress bar runs
(60 s) → play the track, license close (30 s).

## Verify
Runbook fits on one page. Every demo click exists in `app.py` as shipped.
Backup: screen-record the stub demo + preset playback in case of live failure.
