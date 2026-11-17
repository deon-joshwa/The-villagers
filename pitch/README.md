# pitch/ — P5 Pitch & Demo assets

All files owned by P5 (see AGENTS.md). Nothing here touches code.

| File | What it is |
|---|---|
| `slide-1-the-before.md` | Slide 1 script + source provenance for "the before" beat (0:00–0:40) |
| `slide1_yue2_comfyui_nodegraph.png` | The official YuE2 "Text to Music" ComfyUI node graph (15 nodes), rendered from the official JSON — show this full-screen |
| `slide1_yue2_comfyui_nodegraph` renderer | `render_nodegraph.py` regenerates the PNG: `python pitch\render_nodegraph.py` |
| `audio_yue2_text2music.json` | Official workflow JSON, unmodified, from Comfy-Org/workflow_templates |
| `yue2_official_template_cover.webp` | Official template cover art (alt slide visual) |
| `boss-fight-mock.png` | Mock boss-fight screen for the 2:30–3:00 close (1920×1080) |
| `make_boss_mock.py` | Regenerates the mock: `python pitch\make_boss_mock.py` |
| `demo-runbook.md` | One-page runbook — 5:00 Founder's Arena arc, exact click order, cache-first |
| `qa-cards.md` | Judge Q&A, all five domains (technical/business/marketing/financial/investment) — say the line, stop |

## Upgrading the boss-fight mock

The shipped mock is code-drawn (deterministic, no external service). To replace
it with an AI-generated image, generate from this prompt and save as
`boss-fight-mock.png` (1920×1080):

> Dramatic video-game boss fight screen, cinematic 16:9 widescreen. A colossal
> rusted clockwork automaton towers over a tiny armored player in a ruined
> foundry arena; its joints weep thick black oil like tears, brass gears exposed
> through corroded plating, one great piston arm raised to strike. Embers,
> smoke, molten rim light below, dark storm sky. AAA dark-fantasy action-RPG
> aesthetic, painterly concept-art finish. No text, no UI, no watermark.

Nothing else in the kit changes — the runbook references the filename only.

## Verify

```
python pitch\render_nodegraph.py     # rebuilds the node-graph PNG
python pitch\make_boss_mock.py       # rebuilds the boss-fight mock
```

Runbook checks: fits on one page; every click exists in `app.py` as shipped.
Branch: all of this lives on `dev`; merges to `main` happen only at the
Hours 5–6 checkpoint (via P3).
