# YuE-Studio -- Game Audio Synthesizer (Local)

**Tagline:** A no-code local GUI wrapper for YuE 2 -- score your indie game without ComfyUI or music theory.

> **Build mode: 100% AI-driven.** Five people orchestrate AI coding agents; no manual coding.
> Humans write specs and prompts, run commands, paste errors back to agents, review diffs, and verify.
> Target: 8-hour hackathon MVP, then a production roadmap (section 11).
> YuE2 request schema and prompting rules verified against the official repo
> (`multimodal-art-projection/YuE`, `main` branch, Sept/Oct 2026) and `docs/hardware.md`.
> This document (v2) is the single source of truth and supersedes all earlier snippets.

---

## 1. Problem Statement (final, pitch-ready)

State-of-the-art open-source music models like **YuE 2** are trapped behind intimidating terminal
setups, fragmented dependencies, and complex ComfyUI node graphs. Meanwhile, the vast majority of
indie game developers have zero music-theory background -- they think in game-design terms
("menacing boss", "quiet tavern"), not acoustic tokens ("staccato cello ostinato in D minor, 140 BPM").

There is no streamlined **local desktop application** that lets a developer generate scene-specific,
game-ready music from simple, intuitive game-design presets.

**YuE-Studio** translates four game-design dropdowns (Scene, Mood, Style, Intensity) plus one
optional sentence of boss lore into an optimized YuE 2 prompt -- and shows the generated
melody-and-chord plan under the hood.

**License claim (use this exact wording -- do NOT say "copyright-free"):**
> Music you generate is yours to ship: individual devs can sell games with YuE 2 music royalty-free,
> no subscription, no takedowns (YuE 2 weights: CC BY-NC 4.0 + individual creator permission;
> large studios need a commercial license from the YuE 2 team).

---

## 2. Requirements

### 2.1 Functional requirements

| ID | Requirement |
|----|-------------|
| FR1 | Four dropdowns: **Scene Context**, **Mood / Atmosphere**, **Music Style & Instruments**, **Combat Intensity** |
| FR2 | Optional **Custom Scene / Boss Lore** textarea, appended to the compiled prompt |
| FR3 | **"Preview Compiled YuE Prompt"** -- shows the exact `style` string the dropdowns produce (free, instant, no GPU) |
| FR4 | **"Generate Track"** -- runs YuE 2 locally, produces a 30-60 s stereo clip + an **ABC score (melody/chord plan)** |
| FR5 | **ABC score viewer** in the UI (`gr.Code`) -- the "white-box" feature; judges see the composition the dropdowns produced |
| FR6 | Built-in playback with waveform (via `gr.Audio`), autoplay on showcase presets |
| FR7 | **Download .WAV for Unity** -- converts the artifact FLAC to 16-bit PCM WAV |
| FR8 | **"Load Preset Showcase"** -- instant playback of 3 pre-generated seed-pinned tracks (no GPU wait during the pitch) |
| FR9 | Clip-length control (30 / 45 / 60 s) in the UI |
| FR10 | Friendly failure: OOM or crash shows a clean message, never a traceback |

### 2.2 Non-functional requirements

- 100% local inference; no accounts, no API keys, no cloud.
- Runs on **Windows** with an **8 GB VRAM** NVIDIA GPU via `low_vram=True` (proven config:
  RTX 5060 Laptop 8 GB, BF16/FP8 AR, ~6,000-token cap -- see `docs/hardware.md` in the YuE repo).
- Model weights land in a **project-local cache** (`HF_HOME=%~dp0hf_cache`).
- Reproducible showcase: pinned integer seeds per preset.
- **Build constraint: no manual coding.** All code is produced by AI agents from written specs
  (section 5); humans never type application code.

### 2.3 Hardware & software prerequisites

- Windows 10/11, NVIDIA GPU >= 8 GB VRAM (24 GB = official spec; 8 GB works with `low_vram=True`).
- Python **3.12**, Git, ~10 GB free disk (model weights + venv).
- PyTorch **2.10.0 + cu128** (the version YuE 2 pins on Windows), then `pip install .` from the cloned YuE repo.
- Validate with `yue2 doctor`.
- Host RAM matters in `low_vram` mode (weights stream between CPU and GPU) -- 32 GB comfortable, 16 GB workable.

### 2.4 License constraints

- YuE 2 **code**: Apache 2.0. **Weights**: CC BY-NC 4.0 + additional creator permission.
- Individual creators may monetize outputs; companies must obtain a commercial license.
- Attribution optional (encouraged: credit "YuE 2" / #YuE2).

---

## 3. Architecture & tech stack

**Gradio Blocks** -- `gr.Audio` ships a waveform player; YuE 2 is a Python pipeline; zero frontend
build. FastAPI/React is cut -- every UI hour saved goes to model debugging on Windows.

Repo layout (all files authored by AI agents from `contracts.md` + the specs in section 4):

```
yue-studio/
|-- app.py               # Gradio UI (all of it)
|-- prompt_compiler.py   # dropdowns -> YuE2 request JSON
|-- yue_backend.py       # pipeline loader + generate() + FLAC->WAV
|-- make_presets.py      # background script: renders the 3 showcase tracks
|-- contracts.md         # interface contracts -- every agent codes against this
|-- API_NOTES.md         # pasted official YuE2 docs -- prevents agent hallucination
|-- showcase/            # pre-generated clips + scores (made before the pitch)
|-- setup.bat            # venv + torch cu128 + pip install .
|-- run_app.bat          # HF_HOME + activates venv + launches 127.0.0.1:7860
`-- requirements.txt     # gradio, soundfile (torch/yue2 installed by setup.bat)
```

Data flow:

```
dropdowns + lore + clip length -> build_request() -> {id, style, lyrics, cot, seed, ...}
  [Preview Compiled Prompt] : pure string join (no GPU, instant)
  [Generate Track]          : YuE2Pipeline(low_vram=True) -> save_artifacts(dir)
                              -> audio.flac + score.abc
                              -> gr.Audio (waveform) + gr.Code (ABC score)
  [Download .WAV for Unity] : soundfile FLAC -> WAV (PCM_16)
```

---

## 4. Implementation (v2 -- all fixes baked in)

### 4.1 `prompt_compiler.py`

Key rules baked in:
- YuE2 request keys are **`id, style, lyrics, cot, seed`** (there is no `genre_prompt` -- that was YuE 1).
- Style string is **language-first**, then genre/instruments -> mood -> scene -> tempo -> lore -> instrumental tags last.
- `lyrics` is **empty** (NOT `[Intro]\n[Verse]...` -- that is a *vocal* song scaffold and risks ghost vocals).
- BPM lives inside the style string (see `examples/song.json`: "..., 88 BPM").

```python
"""Translates game-design dropdowns into a YuE 2 request payload."""

STYLE_MAP = {
    "Dark Orchestral + Brass":
        "dark cinematic orchestra, heavy brass stabs, pounding war drums, cello",
    "Cyberpunk / Industrial Synth":
        "distorted 808 sub-bass, aggressive synthesizers, industrial percussion",
    "8-bit / 16-bit Retro Chiptune":
        "chiptune synth, square lead, 8-bit arpeggio, energetic drum machine",
    "Acoustic Folk / World":
        "acoustic nylon guitar, warm violin, flute, campfire atmosphere",
}

MOOD_MAP = {
    "Menacing / Ominous":      "ominous, terrifying, relentless, dark tension",
    "Tragic / Melancholic":    "sorrowful, emotional, minor scale, weeping strings",
    "Whimsical / Playful":     "lighthearted, bouncing rhythm, curious, bright major scale",
    "Tense / Suspenseful":     "tense, suspenseful, pulsing ostinato, creeping dread",
}

SCENE_MAP = {
    "Boss Battle (Phase 1 / 2)": "epic battle theme, driving percussion, layered arrangement, rising tension",
    "Dungeon / Stealth":         "sparse textures, low drones, suspense, haunting",
    "Safe Room / Tavern":        "intimate small ensemble, warm acoustics, gentle looping ambience",
    "Open World Exploration":    "expansive, evolving layers, adventurous, airy",
}

BPM_MAP = {
    "Calm / Ambient (< 80 BPM)":              "70 BPM",
    "Moderate / Exploration (90-110 BPM)":    "100 BPM",
    "High Adrenaline / Combat (120-150 BPM)": "140 BPM",
    "Frenetic / Enraged (160+ BPM)":          "170 BPM",
}

CLIP_LENGTHS = {"30 s": 30, "45 s": 45, "60 s": 60}

def compile_style(scene, mood, style, intensity, custom_lore=""):
    parts = [
        "English",               # YuE2 wants the language tag FIRST
        STYLE_MAP[style],
        MOOD_MAP[mood],
        SCENE_MAP[scene],        # scene shapes arrangement/dynamics
        BPM_MAP[intensity],
    ]
    if custom_lore.strip():
        parts.append("scene inspiration: " + custom_lore.strip())
    parts.append("instrumental, no vocals")   # YuE2 has no instrumental mode -- enforce in text
    return ", ".join(parts)

def build_request(scene, mood, style, intensity, custom_lore="",
                  clip_seconds=45, seed=None, track_id=None):
    request = {
        "id": track_id or (scene.split(" ")[0].lower() + "_" + mood.split(" ")[0].lower()),
        "style": compile_style(scene, mood, style, intensity, custom_lore),
        "lyrics": "",            # empty => instrumental; "[Instrumental]" also works
        "cot": "full",           # symbolic planning => editable ABC score (our UI feature)
        "seed": int(seed) if seed is not None else 831001,
    }
    # HOUR-1 TODO (P1): replace "max_seconds" with the REAL duration / token-cap
    # parameter name from docs/generation.md (the 8 GB reference run used a
    # 6,000-token cap). Delete this line if YuE2 takes no such kwarg.
    request["max_seconds"] = int(clip_seconds)
    return request
```

### 4.2 `yue_backend.py`

```python
"""Loads YuE2 once, generates clips, converts FLAC -> WAV."""
import os
import soundfile as sf

class GenerationError(RuntimeError):
    """Raised when YuE2 generation fails or artifacts are incomplete."""

class YueStudio:
    def __init__(self):
        self._pipe = None

    @property
    def pipe(self):
        if self._pipe is None:
            from yue2 import YuE2Pipeline
            # low_vram: keeps only active AR/NAR modules on GPU -- the 8 GB path
            self._pipe = YuE2Pipeline.from_pretrained(
                "m-a-p/YuE2-3B", device="cuda", low_vram=True)
        return self._pipe

    def generate(self, request, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        try:
            song = self.pipe(**request)   # kwargs must match API_NOTES.md exactly
            song.save_artifacts(out_dir)
        except Exception as e:
            raise GenerationError(
                "YuE2 generation failed: %s -- likely OOM on 8 GB. "
                "Try a shorter clip or a preset." % e) from e
        flac = os.path.join(out_dir, "audio.flac")
        wav = os.path.join(out_dir, "audio.wav")
        score = os.path.join(out_dir, "score.abc")
        if not (os.path.exists(flac) and os.path.exists(score)):
            raise GenerationError("Generation finished but artifacts are missing.")
        data, sr = sf.read(flac)
        sf.write(wav, data, sr, subtype="PCM_16")
        return {"wav": wav, "flac": flac, "score": score}

    def read_score(self, score_path):
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return "(score not available yet -- generate a track first)"
```

### 4.3 `app.py` (queue + error handling + stub mode + clip length + autoplay)

```python
import os
import gradio as gr
from prompt_compiler import (SCENE_MAP, MOOD_MAP, STYLE_MAP, BPM_MAP,
                             CLIP_LENGTHS, compile_style, build_request)
from yue_backend import YueStudio, GenerationError

USE_STUB = os.environ.get("YUE_STUB") == "1"   # UI testing with zero GPU
_studio = None

def studio():
    global _studio
    if _studio is None:
        _studio = YueStudio()
    return _studio

SHOWCASE = [  # pre-rendered by make_presets.py, seed-pinned
    ("Boss / Menacing / Dark Orchestral", "showcase/showcase_831001.wav", "showcase/showcase_831001.abc"),
    ("Dungeon / Tense / Cyberpunk",       "showcase/showcase_831002.wav", "showcase/showcase_831002.abc"),
    ("Tavern / Whimsical / Folk",         "showcase/showcase_831003.wav", "showcase/showcase_831003.abc"),
]

SAMPLE_ABC = "X:1\nT:stub score\nM:4/4\nL:1/8\nK:Am\n"
CSS = ".gradio-container {background: #12121a; color: #e8e8f0;}"

with gr.Blocks(css=CSS, title="YuE-Studio") as demo:
    gr.Markdown("# YuE-Studio: Game Audio Synthesizer (Local)")
    with gr.Row():
        scene     = gr.Dropdown(list(SCENE_MAP), label="1. Scene Context")
        mood      = gr.Dropdown(list(MOOD_MAP),  label="2. Mood / Atmosphere")
    with gr.Row():
        style     = gr.Dropdown(list(STYLE_MAP), label="3. Music Style & Instruments")
        intensity = gr.Dropdown(list(BPM_MAP),   label="4. Combat Intensity")
    clip_len = gr.Dropdown(list(CLIP_LENGTHS), value="45 s", label="5. Clip Length")
    lore = gr.Textbox(
        label="ADVANCED: Custom Scene / Boss Lore (optional)",
        placeholder="A giant clockwork automaton covered in rust, weeping oil as it attacks.")

    with gr.Accordion("Show Compiled YuE Prompt", open=False):
        preview = gr.Textbox(label="style", lines=3, interactive=False)
        preview_btn = gr.Button("Preview Compiled YuE Prompt")

    generate_btn = gr.Button("GENERATE TRACK (YuE 2)", variant="primary")
    gr.Markdown("Generation on an 8 GB GPU takes several minutes -- showcase presets below play instantly.")

    with gr.Row():
        audio = gr.Audio(label="Playback", type="filepath")
        score = gr.Code(label="Generated ABC Score (melody & chords)", language="markdown")
    wav_file = gr.File(label="Download .WAV for Unity")

    gr.Markdown("## Preset Showcase")
    with gr.Row():
        preset_btns = [gr.Button(name) for name, _, _ in SHOWCASE]
    preset_audio = gr.Audio(label="Showcase playback", type="filepath", autoplay=True)

    preview_btn.click(
        lambda s, m, st, i, l: compile_style(s, m, st, i, l),
        [scene, mood, style, intensity, lore], preview)

    def do_generate(scene, mood, style, intensity, clip_len, lore):
        if USE_STUB:   # zero-GPU testing for the UI owner
            w, a = SHOWCASE[0][1], SHOWCASE[0][2]
            return w, open(a, encoding="utf-8").read() if os.path.exists(a) else SAMPLE_ABC, w
        try:
            req = build_request(scene, mood, style, intensity, lore,
                                clip_seconds=CLIP_LENGTHS[clip_len], seed=42)
            out = studio().generate(req, "outputs/" + req["id"])
            return out["flac"], studio().read_score(out["score"]), out["wav"]
        except GenerationError as e:
            raise gr.Error(str(e))
        except Exception:
            raise gr.Error("Something went wrong. Try a shorter clip or a preset.")

    generate_btn.click(do_generate,
                       [scene, mood, style, intensity, clip_len, lore],
                       [audio, score, wav_file])

    for btn, (_, path, abc) in zip(preset_btns, SHOWCASE):
        btn.click(lambda p, a: (p, open(a, encoding="utf-8").read()), [path, abc],
                  [preset_audio, score])

demo.queue()
demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
```

### 4.4 `make_presets.py` (runs in background from Hour 2)

```python
from prompt_compiler import build_request
from yue_backend import YueStudio

PRESETS = [
    ("Boss Battle (Phase 1 / 2)", "Menacing / Ominous",  "Dark Orchestral + Brass",
     "High Adrenaline / Combat (120-150 BPM)", 831001),
    ("Dungeon / Stealth",         "Tense / Suspenseful", "Cyberpunk / Industrial Synth",
     "Moderate / Exploration (90-110 BPM)", 831002),
    ("Safe Room / Tavern",        "Whimsical / Playful", "Acoustic Folk / World",
     "Calm / Ambient (< 80 BPM)", 831003),
]

studio = YueStudio()
for scene, mood, style, intensity, seed in PRESETS:
    req = build_request(scene, mood, style, intensity, seed=seed, track_id="showcase_%d" % seed)
    out = studio.generate(req, "showcase")
    print("done:", out["wav"], flush=True)
```

### 4.5 `setup.bat` / `run_app.bat`

```bat
:: setup.bat  (run ONCE, hours before the hackathon -- model download is large)
python -m venv .venv
call .venv\Scripts\activate
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128
git clone https://github.com/multimodal-art-projection/YuE.git yue2-repo
python -m pip install .\yue2-repo
python -m pip install gradio soundfile
yue2 doctor
```

```bat
:: run_app.bat
@echo off
cd /d %~dp0
set HF_HOME=%~dp0hf_cache
call .venv\Scripts\activate
python app.py
```

---

## 5. AI-Driven Build Protocol (no manual coding)

Every person drives an AI coding agent (OpenCode / Claude / Cursor / Copilot Workspace -- any
agentic coder). **Humans never type application code.** Humans do five things:

1. **Spec** -- write/own the spec for their workstream (section 4 + `contracts.md`).
2. **Prompt** -- paste the spec + `API_NOTES.md` into their agent (prompt kit in section 6).
3. **Run** -- execute the commands the agent produces (setup, tests, app launch).
4. **Verify** -- review the agent's diff against the contract; run the smoke test; if wrong,
   paste the error output back to the agent ("fix per this traceback").
5. **Merge** -- commit working files to the shared repo; never commit unverified code.

**Hard rules (prevent AI failure modes):**
- `API_NOTES.md` contains the **pasted official YuE2 README quick-start + `docs/hardware.md`
  excerpts**. Agents must not invent YuE2 parameters -- any kwarg not in `API_NOTES.md` is
  rejected in review. The `max_seconds` kwarg in section 4.1 is the ONLY tolerated unknown,
  and P1 must resolve it against `docs/generation.md` by Hour 1.
- One file, one owner: no two people's agents edit the same file (merge conflicts are the
  #1 time-killer in parallel AI builds).
- Every agent prompt includes: the contract, the file spec, and "output the complete file,
  then list the exact commands to verify it".
- If an agent loops twice on the same bug, the human switches prompt strategy: paste the
  ACTUAL error + file content, ask for a minimal diff instead of a rewrite.

---

## 6. AI Prompt Kit (copy-paste starters)

**Kickoff (P1, Hour 0):**
> Create `contracts.md` in the repo root containing exactly these interface definitions:
> build_request(scene, mood, style, intensity, custom_lore, clip_seconds, seed, track_id)
> -> {"id": str, "style": str, "lyrics": "", "cot": "full", "seed": int, "max_seconds": int};
> generate(request, out_dir) -> {"wav": path, "flac": path, "score": path};
> showcase files: showcase/showcase_<seed>.wav and .abc for seeds 831001-831003.

**Any workstream (P2/P3/P4):**
> You are implementing <FILE> for YuE-Studio. Code EXACTLY against contracts.md and the spec
> below. YuE2 API facts are in API_NOTES.md -- do not invent or rename any parameter.
> Spec: <paste section 4.x>. Output the complete file, then list the exact commands
> to verify it on Windows.

**Error loop (everyone):**
> Here is the file and the actual error output: <paste>. Produce a minimal diff that fixes
> it. Do not refactor anything else.

**Docs harvest (P1, Hour 0.5):**
> From the following YuE2 documentation text, extract: the exact pipeline constructor kwargs,
> the request JSON fields, and any parameter controlling clip length / token cap / low VRAM.
> Write them to API_NOTES.md as a table with source line quotes.
> <paste README quick-start + docs/generation.md + docs/hardware.md text>

---

## 7. Team Split v2 -- five AI orchestrators

### 7.1 Roles (people drive agents; nobody hand-codes)

| Person | Role | Drives AI to produce / do | Verify duty |
|--------|------|---------------------------|-------------|
| **P1** | Model Wrangler | `setup.bat`, `run_app.bat`, `API_NOTES.md` harvest, smoke-test script, `make_presets.py` | **Runs everything GPU**: `yue2 doctor`, smoke test, preset renders, audio QC (ghost vocals), resolves the `max_seconds` TODO |
| **P2** | Spec & Compiler owner | `prompt_compiler.py` + unit tests, `contracts.md`, README, in-app microcopy | Runs the unit tests the agent writes; reviews every map string for music-term sanity |
| **P3** | Integration owner | `yue_backend.py`, queue/progress/error wiring, `outputs/` management | Full round-trip: compiler -> backend -> artifacts on disk; rehearsal support on failure paths |
| **P4** | UI owner | `app.py` (stub-first), theme, showcase buttons | Launches with `YUE_STUB=1` and clicks EVERY path; screenshot-diffs against the mockup |
| **P5** | Pitch & Demo owner | Slides, mock boss-fight screen, demo runbook, backup recordings -- all agent-generated assets | Rehearsals; times the 3-minute pitch; owns Q&A (license, hardware, why-YuE2) |

### 7.2 Ownership map (one file, one owner)

```
P1: setup.bat, run_app.bat, API_NOTES.md, make_presets.py, showcase/
P2: contracts.md, prompt_compiler.py, tests/, README.md
P3: yue_backend.py
P4: app.py
P5: pitch/ (slides, runbook, assets)
Shared (no writes): repo config, .gitignore (P2 sets up at kickoff)
```

### 7.3 Hour-by-hour assignment

| Hours | P1 Model | P2 Compiler | P3 Backend | P4 UI | P5 Pitch |
|-------|----------|-------------|------------|-------|----------|
| **0-1** | Agent writes setup.bat -> run it -> `yue2 doctor` -> harvest `API_NOTES.md` | Agent writes `contracts.md` + `prompt_compiler.py` + tests | Agent writes `yue_backend.py` skeleton | Agent writes `app.py` against stub | Agent makes ComfyUI "before" slide |
| **1-2** | **SMOKE TEST gate**: no vocals, <=60 s, `score.abc` saved; resolve `max_seconds` | Run unit tests via agent; fix diffs | Wire real kwargs from `API_NOTES.md` | Click every stub path; polish theme | Agent makes mock boss screen |
| **2-4** | Render 3 presets in background; QC audio | Lore edge cases; tooltips | FLAC->WAV + `read_score` + progress queue | Real backend behind stub flag; full click-through | Pitch script v1; Q&A cards |
| **4-6** | Tune token cap; regenerate offenders | README final | Integration fixes | Score viewer + WAV button polish | **Rehearsal #1** (with team) |
| **6-7** | Pin final seeds | Merge README | Friendly errors verified | Final showcase buttons | **Rehearsal #2**, freeze runbook |
| **7-8** | Standby: live-gen | Bugfix standby | Bugfix standby | Bugfix standby | Final timing; deliver pitch |

### 7.4 Checkpoints

| Time | Checkpoint | Decisions made |
|------|-----------|----------------|
| **Hour 0.5** | Kickoff (10 min) | Repo created; P2 commits `contracts.md`; everyone's agent reads it before writing code |
| **Hour 2** | Smoke-test gate | P1 decides: live generation in pitch vs cache-only; everyone adapts |
| **Hour 4** | Integration checkpoint | P3+P4 merge; full round-trip must work on 1 preset (or stub stays for safety) |
| **Hour 6** | Content freeze | New features stop; polish and bugfixes only |
| **Hour 7.5** | Last rehearsal | Hands off agents; P5 owns the machine from here |

**Staffing notes:**
- P1 is the bottleneck (one GPU, one environment) -- protect their time; nobody else runs setup.
- P2 and P4 have zero GPU dependency for their first 4 hours; agents keep them unblocked.
- P5 starts demo prep at Hour 0 -- the pitch is half the judges' score.
- If P1 clears the smoke test early, P1's agent pivots to helping P3 with integration.
- AI velocity bonus: if Hours 0-4 go clean, pull ONE item from the 11.2 roadmap into Hour 6-8
  (recommended: seamless loop export -- biggest real-world value).

---

## 8. 8-Hour Execution Checklist (unchanged targets, AI-driven means faster code, same GPU gates)

| Hours | Task | Exit criteria |
|-------|------|---------------|
| **0-1** | Agents write setup/run scripts; P1 runs them; `yue2 doctor`; model download | Doctor passes; weights on disk |
| **1-2** | **Instrumental smoke test** (empty lyrics, `cot="full"`, `low_vram=True`) | (1) No ghost vocals (2) clip <= 60 s (3) `score.abc` in artifacts. **Gate: fail by hour 2 -> cache-only demo** |
| **2-4** | Compiler + backend done; **presets rendering in background** | Unit tests green; 3 preset renders running |
| **4-6** | UI complete; stub swapped for real backend | Full round-trip works on one preset |
| **6-7** | Showcase mode + polish | Instant autoplay of 3 presets; live gen optional garnish |
| **7-8** | Pitch prep + buffer | 3-min pitch rehearsed twice, end-to-end |

---

## 9. The 3-Minute Pitch (script)

1. **(0:00-0:40) The before.** Show the *official YuE2 ComfyUI workflow* node graph on the projector.
   "This is state-of-the-art open-source music. This is what an indie game dev faces. Nodes, tokens, VRAM flags, music theory."
2. **(0:40-1:30) The four clicks.** YuE-Studio on your laptop: Boss Battle -> Menacing -> Dark Orchestral -> High Adrenaline. Type one sentence of boss lore: *"A giant clockwork automaton covered in rust, weeping oil as it attacks."* Hit **Preview Compiled Prompt** -- show the translation happening live.
3. **(1:30-2:30) The white-box reveal.** Generate (or switch to showcase preset) and open the **ABC score**: "YuE 2 plans the melody and chords as symbols first -- our UI surfaces that plan so the dev can see *what* they are getting. No music theory required."
4. **(2:30-3:00) The close.** Play the track over a mock boss-fight screen (optional). "100% local, 8 GB GPU, and the music is yours to ship -- individual devs sell games with YuE 2 music royalty-free. YuE-Studio: compose in game design, not in acoustic tokens."

**Demo hygiene:** cache carries the moment; live generation is something you *kick off and check back on*, never the load-bearing part of the pitch.

---

## 10. Risks & Fallbacks

| Risk | Likelihood | Mitigation / Fallback |
|------|-----------|----------------------|
| **AI agent invents YuE2 API parameters** | High (the #1 AI risk) | `API_NOTES.md` with pasted official docs; review rejects any kwarg not in it; smoke test validates against the real pipeline by Hour 2 |
| Ghost vocals bleed into "instrumental" output | Medium | Empty lyrics + `instrumental, no vocals` tag; audition all presets Hours 1-2; regenerate with different seeds |
| OOM / OOM-adjacent stall on 8 GB | Medium | `low_vram=True`, clip-length dropdown, token cap resolved at Hour 1 |
| Generation too slow for live demo | High (expected) | Cache-first showcase -- preset buttons are the demo; live gen is garnish |
| Agent merge conflicts / drift | Medium | One file, one owner (7.2); `contracts.md` is the single interface truth |
| Agent loops on the same bug | Medium | Switch to minimal-diff prompting with the actual traceback pasted (section 5, rule 4) |
| Windows install friction | Medium | `setup.bat` run hours ahead; `yue2 doctor` as the objective check |
| Judge asks about licensing | Low | Use the exact corrected wording from section 1 -- never say "copyright-free" |

---

## 11. Completeness Audit & Production Roadmap

**Verdict: sections 1-10 cover 100% of the hackathon MVP, including the AI-driven build mode.
A shippable product additionally needs section 11.2 (~2-3 weeks).**

### 11.1 Fix list -- already folded into the section 4 code (v2)

`demo.queue()` | `GenerationError` + `gr.Error` friendly failures | `YUE_STUB` mode in code |
clip-length dropdown (`CLIP_LENGTHS` + `max_seconds` TODO) | `HF_HOME` pinned in `run_app.bat` |
`autoplay=True` on showcase | FLAC->WAV verified in smoke test

### 11.2 Post-hackathon roadmap (what "final product" means beyond the demo)

| Feature | Why it matters | Effort |
|---------|---------------|--------|
| Desktop packaging (PyInstaller, or Tauri/Electron shell around embedded Python) | "double-click a .bat, browser tab opens" is a hackathon answer, not a product | 2-3 days |
| First-run wizard: model download with progress bar, VRAM detection (auto-selects `low_vram` + token cap), embedded `yue2 doctor` check | A 3B-parameter download happening silently on first use is a support nightmare | 1-2 days |
| Seamless LOOP export (loop markers / crossfade loop for Unity) | Game audio must loop cleanly; a 60 s one-shot with a hard ending is not game-ready music | 1-2 days |
| Best-of-N variations + audition picker | YuE2 benchmarks score with best-of-8 -- single-shot output quality varies; devs need choices | 1 day |
| ABC score edit -> re-render | YuE2 supports score editing natively; "tweak the chords in the plan, re-render" is the unique differentiator | 2-3 days |
| Scene sequencer: multi-scene soundtrack with transitions | Real games need per-scene tracks that hand off smoothly, not isolated clips | 3+ days |
| Settings persistence + project save/load | Nobody should re-pick 4 dropdowns every launch | 1 day |
| Installer + code signing + auto-update + opt-in crash logging | Distribution basics for any desktop product | ~2 days |
| Test suite + CI beyond the compiler unit tests | Only P2's tests exist in the hackathon scope | ongoing |

**Bottom line:** for the hackathon, build sections 3-8 through AI agents per the section 5
protocol. The 11.2 roadmap is what turns the weekend build into the product the tagline promises.
