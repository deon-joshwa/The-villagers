# showcase/ — pre-rendered demo tracks (owner: P1)

Files here are produced by `make_presets.py` (seeds pinned in `contracts.md`):

| Seed | Preset |
|------|--------|
| 831001 | Boss Battle / Menacing / Dark Orchestral / High Adrenaline |
| 831002 | Dungeon / Tense / Cyberpunk / Moderate |
| 831003 | Tavern / Whimsical / Folk / Calm |

The committed `.wav` files are **silent placeholders** so the UI's stub mode and
preset buttons work before any GPU run. `make_presets.py` overwrites them with
real renders (plus `showcase_<seed>.abc` scores).

**QC rule before the pitch:** audition every file for ghost vocals — upstream's own
docs warn that voice-free output is not guaranteed. If one leaks: click
"Fix Ghost Vocals" in the app (Vocal → Ins, re-render) or regenerate with a new seed.
