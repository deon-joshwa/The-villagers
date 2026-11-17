# Slide 1 — "The Before" (0:00–0:40)

**Show on the projector:** `slide1_yue2_comfyui_nodegraph.png`
(backup / alt crop: `yue2_official_template_cover.webp`)

## What is on screen

The **official YuE2 ComfyUI workflow** "YuE2: Text to Music":

- JSON (ground truth, unchanged): `audio_yue2_text2music.json`, downloaded from
  <https://github.com/Comfy-Org/workflow_templates> (`templates/audio_yue2_text2music.json`)
- Rendered image: `slide1_yue2_comfyui_nodegraph.png` — 15 nodes, rendered **directly
  from the official JSON** by `render_nodegraph.py` (positions, widgets and links are
  the real ones; nothing is invented).
- Regenerate it any time with:
  `python pitch\render_nodegraph.py`
- For maximum authenticity in the room you may instead open the JSON in a live
  ComfyUI (v0.36.0+) and screenshot the real editor — the graph is identical.

## Caption (verbatim, on the slide)

> **"This is what an indie game dev faces."**

## Speaker script (40 seconds)

"This is state-of-the-art open-source music. This is what an indie game dev
faces. Nodes, tokens, VRAM flags, music theory." *(let the graph sit on screen
while you say it — the wall of nodes IS the argument.)*

Point at three things, then move on:

1. **#24 YuE2GenerateABC** — "the model plans the melody and chords as symbols first"
2. **#36 / #37 PrimitiveStringMultiline** — "and you write *this* — acoustic tokens and section tags"
3. **#8 KSampler + #5 EmptyYuE2LatentAudio** — "…and wire this by hand"

Then click away to OST.io (runbook step 1).

## Talk-track trap

Do NOT explain the graph. Every second spent explaining the before is a second
stolen from the after. If it looks intimidating, it is working.
