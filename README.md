# OST.io — game words in, game music out

OST.io is a local game-music generator built on the **YuE2** model. You pick
four dropdowns in *game-design language* ("Boss Battle", "Menacing", "Dark
Orchestral", "High Adrenaline"), it compiles them into a proper music prompt
and renders an instrumental track — no music theory, no prompt engineering,
no cloud. Everything runs on your own machine.

Built for the 8-hour hackathon sprint documented in `ost-io-hackathon-plan.md`.

## Quickstart (Windows)

```bat
setup.bat    :: first run only — creates a Python 3.12 venv and pulls the YuE2 weights
run_app.bat  :: every run — starts the OST.io UI and opens it in your browser
```

- No NVIDIA GPU? You can still try the UI: set `YUE_STUB=1` before
  `run_app.bat` and the app returns pre-rendered showcase tracks instead of
  live generations.
- Weights are cached project-local in `hf_cache/` (created by `setup.bat`).

## The 4-dropdown flow

1. **Scene** — *when does this track play?* Boss battle, dungeon/stealth,
   safe room/tavern, open-world exploration.
2. **Mood** — *what should the player feel?* Menacing, tragic, whimsical, tense.
3. **Style** — *what does it sound like?* Dark orchestral, cyberpunk synth,
   retro chiptune, acoustic folk.
4. **Intensity** — *how fast?* Calm ambient → moderate exploration → combat
   adrenaline → frenetic enraged (BPM ranges are shown on the labels).

Optionally, a **custom lore** box lets you describe your scene in one line
("a rusted clockwork automaton guards the mine") — it is woven into the prompt
safely (whitespace collapsed, control characters stripped, capped length).

Under the hood, `prompt_compiler.py` translates the four picks into the exact
YuE2 request shape (empty lyrics = instrumental, `cot="full"` so you also get
an editable ABC score, a pinned seed for reproducibility). Track length is
customizable via the Duration Slider (15s–120s, default 45s), backed by 25 tokens/s
dynamic sampling budgeting that cuts render times down to ~3 minutes.

## Ownership / team layout

Five humans, five AI agents, one shared `dev` branch (see `AGENTS.md` and
`GIT-WORKFLOW.md`). `contracts.md` is the single source of truth every agent
codes against. `main` is the showcase branch — never commit to it directly.

## License & usage (important)

Individual devs can sell games with YuE2 music royalty-free (weights:
CC BY-NC 4.0 + individual creator permission). Large studios need a
commercial license.

OST.io itself only *drives* the model — it adds no extra restrictions and
does not claim ownership of the tracks you generate. Please respect the
upstream YuE2 weights license when shipping your game. Never describe this
setup as "copyright-free"; it is not.

## UI copy reference (for P4)

Status messages written for game devs — drop-in text for the app status line:

| Event | Message |
|-------|---------|
| Start | `Rendering track… (this can take several minutes on one GPU)` |
| Progress | `Composing… stage {stage} — step {completed}/{total}` |
| Done | `Done — {duration_s}s of music. Seed {seed} is saved; reuse it to get this exact track again.` |
| Truncated | `⚠ The model hit its length limit — track may end abruptly. Try "Moderate" intensity for a cleaner loop.` |
| Fallback used | `Instrumental pass finished — vocals removed from the score and re-rendered.` |
| Failure | `Generation failed: {message}. Check the console window for details.` |

Hover tooltips for the four dropdowns are ready in `prompt_compiler.TOOLTIPS`
(one-liners explaining *when the track plays*, in game-design words) — wire
them as `gr.Dropdown(..., info=...)` whenever convenient; nothing is required.

## Performance & VRAM notes

- The backend defaults to **FP8 AR weights** (`quantization="fp8"`, P3's
  Hour-2 gate). Verified on an RTX 4060 Laptop (8 GB VRAM) with hardware FP8
  acceleration and software emulation fallback.
- **Fast generation with ComfyUI token ceilings:** Duration maps to 25 semantic
  tokens/sec and capped ABC planning (max 1,200 tokens), dropping live generation
  from ~30 minutes down to **~3 minutes** for 45s clips on 8 GB cards with zero OOM.
- **Truncation is normal:** Length follows the symbolic plan under the token budget.
  The UI surfaces the `truncated` flag from `result.json` when the requested duration
  is met.
- One generation = one output directory. Re-running a changed request into
  the same directory overwrites artifacts; `make_presets.py` builds per-seed
  `outputs/build_<seed>/` dirs for this reason.

## Credits

- YuE2: `multimodal-art-projection/YuE` (verified API facts in `API_NOTES.md`)
- OST.io: the Villagers hackathon team
