# YuE-Studio -- Game Audio Synthesizer (Local)

**Tagline:** A no-code local GUI wrapper for YuE 2 -- score your indie game without ComfyUI or music theory.

> Target: 8-hour hackathon build. Windows + NVIDIA GPU (8 GB VRAM class). Python 3.12 + Gradio.
> YuE2 request schema and prompting rules in this document were verified against the official
> repo (`multimodal-art-projection/YuE`, `main` branch, Sept/Oct 2026) and `docs/hardware.md`.

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
| FR6 | Built-in playback with waveform (via `gr.Audio`) |
| FR7 | **Download .WAV for Unity** -- converts the artifact FLAC to 16-bit PCM WAV |
| FR8 | **"Load Preset Showcase"** -- instant playback of 3 pre-generated seed-pinned tracks (no GPU wait during the pitch) |

### 2.2 Non-functional requirements

- 100% local inference; no accounts, no API keys, no cloud.
- Runs on **Windows** with an **8 GB VRAM** NVIDIA GPU via `low_vram=True` (proven config:
  RTX 5060 Laptop 8 GB, BF16/FP8 AR, ~6,000-token cap -- see `docs/hardware.md` in the YuE repo).
- First run downloads YuE2-3B (~3B params) from Hugging Face -- do this before the demo.
- Reproducible showcase: pinned integer seeds per preset.

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

**Option A (chosen): Gradio Blocks** -- `gr.Audio` ships a waveform player; YuE 2 is a Python
pipeline; zero frontend build. FastAPI/React (Option B) is cut -- every UI hour saved goes to
model debugging on Windows.

Repo layout:

```
yue-studio/
|-- app.py               # Gradio UI (all of it)
|-- prompt_compiler.py   # dropdowns -> YuE2 request JSON
|-- yue_backend.py       # pipeline loader + generate() + FLAC->WAV
|-- make_presets.py      # background script: renders the 3 showcase tracks
|-- showcase/            # pre-generated clips + scores (made before the pitch)
|-- setup.bat            # venv + torch cu128 + pip install .
|-- run_app.bat          # activates venv, launches UI at 127.0.0.1:7860
`-- requirements.txt     # gradio, soundfile (torch/yue2 installed by setup.bat)
```

Data flow:

```
dropdowns + lore -> build_request() -> {id, style, lyrics, cot, seed}
  [Preview Compiled Prompt] : pure string join (no GPU, instant)
  [Generate Track]          : YuE2Pipeline(low_vram=True) -> save_artifacts(dir)
                              -> audio.flac + score.abc
                              -> gr.Audio (waveform) + gr.Code (ABC score)
  [Download .WAV for Unity] : soundfile FLAC -> WAV (PCM_16)
```

---

## 4. Implementation

### 4.1 `prompt_compiler.py` (complete)

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

def build_request(scene, mood, style, intensity, custom_lore="", seed=None, track_id=None):
    return {
        "id": track_id or (scene.split(" ")[0].lower() + "_" + mood.split(" ")[0].lower()),
        "style": compile_style(scene, mood, style, intensity, custom_lore),
        "lyrics": "",            # empty => instrumental; "[Instrumental]" also works
        "cot": "full",           # symbolic planning => editable ABC score (our UI feature)
        "seed": int(seed) if seed is not None else 831001,
    }
```

### 4.2 `yue_backend.py` (complete)

```python
"""Loads YuE2 once, generates clips, converts FLAC -> WAV."""
import os
import soundfile as sf

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
        song = self.pipe(**request)   # see docs/generation.md for a
        song.save_artifacts(out_dir)  # max-length/token cap on small GPUs
        flac = os.path.join(out_dir, "audio.flac")
        wav = os.path.join(out_dir, "audio.wav")
        data, sr = sf.read(flac)
        sf.write(wav, data, sr, subtype="PCM_16")
        return {"wav": wav, "flac": flac, "score": os.path.join(out_dir, "score.abc")}

    def read_score(self, score_path):
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return "(score not available yet -- generate a track first)"
```

> **TODO (Hour 1, before writing the UI):** open `docs/generation.md` in the YuE repo and find the
> exact parameter for clip length / token cap on low-VRAM devices (the 8 GB reference run used a
> 6,000-token cap). Wire it into `generate()` so a 60 s clip cannot OOM the demo.

### 4.3 `app.py` (Gradio Blocks, dark theme)

```python
import gradio as gr
from prompt_compiler import (SCENE_MAP, MOOD_MAP, STYLE_MAP, BPM_MAP,
                             compile_style, build_request)
from yue_backend import YueStudio

studio = YueStudio()

SHOWCASE = [  # pre-rendered by make_presets.py, seed-pinned
    ("Boss / Menacing / Dark Orchestral", "showcase/showcase_831001.wav", "showcase/showcase_831001.abc"),
    ("Dungeon / Tense / Cyberpunk",       "showcase/showcase_831002.wav", "showcase/showcase_831002.abc"),
    ("Tavern / Whimsical / Folk",         "showcase/showcase_831003.wav", "showcase/showcase_831003.abc"),
]

CSS = ".gradio-container {background: #12121a; color: #e8e8f0;}"

with gr.Blocks(css=CSS, title="YuE-Studio") as demo:
    gr.Markdown("# YuE-Studio: Game Audio Synthesizer (Local)")
    with gr.Row():
        scene     = gr.Dropdown(list(SCENE_MAP), label="1. Scene Context")
        mood      = gr.Dropdown(list(MOOD_MAP),  label="2. Mood / Atmosphere")
    with gr.Row():
        style     = gr.Dropdown(list(STYLE_MAP), label="3. Music Style & Instruments")
        intensity = gr.Dropdown(list(BPM_MAP),   label="4. Combat Intensity")
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
    preset_audio = gr.Audio(label="Showcase playback", type="filepath")

    preview_btn.click(
        lambda s, m, st, i, l: compile_style(s, m, st, i, l),
        [scene, mood, style, intensity, lore], preview)

    def do_generate(s, m, st, i, l):
        req = build_request(s, m, st, i, l, seed=42)
        out = studio.generate(req, "outputs/" + req["id"])
        return out["flac"], studio.read_score(out["score"]), out["wav"]

    generate_btn.click(do_generate,
                       [scene, mood, style, intensity, lore],
                       [audio, score, wav_file])

    for btn, (_, path, abc) in zip(preset_btns, SHOWCASE):
        btn.click(lambda p, a: (p, a), [path, abc], [preset_audio, score])

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
call .venv\Scripts\activate
python app.py
```

---

## 5. 8-Hour Execution Checklist

| Hours | Task | Exit criteria |
|-------|------|---------------|
| **0-1** | Environment gauntlet: `setup.bat`, `yue2 doctor`, trigger model download | Doctor passes; weights on disk |
| **1-2** | **Instrumental smoke test** (hardcoded request: empty lyrics, `cot="full"`, `low_vram=True`) | (1) No ghost vocals (2) clip <= 60 s (3) `score.abc` in artifacts. **Gate: if not working by hour 2 -> cache-only demo** |
| **2-4** | `prompt_compiler.py` + `yue_backend.py` + **start `make_presets.py` in background** | Compiler unit-tested; 3 preset renders running |
| **4-6** | `app.py` UI: 4 dropdowns, lore, preview accordion, score viewer, audio, WAV export, `run_app.bat` | Full round-trip works on one preset |
| **6-7** | Showcase mode + polish (theme, labels, error messages) | Instant playback of 3 presets; live gen optional garnish |
| **7-8** | Pitch prep + buffer | 3-min pitch rehearsed once end-to-end |

---

## 6. The 3-Minute Pitch (script)

1. **(0:00-0:40) The before.** Show the *official YuE2 ComfyUI workflow* node graph on the projector.
   "This is state-of-the-art open-source music. This is what an indie game dev faces. Nodes, tokens, VRAM flags, music theory."
2. **(0:40-1:30) The four clicks.** YuE-Studio on your laptop: Boss Battle -> Menacing -> Dark Orchestral -> High Adrenaline. Type one sentence of boss lore: *"A giant clockwork automaton covered in rust, weeping oil as it attacks."* Hit **Preview Compiled Prompt** -- show the translation happening live.
3. **(1:30-2:30) The white-box reveal.** Generate (or switch to showcase preset) and open the **ABC score**: "YuE 2 plans the melody and chords as symbols first -- our UI surfaces that plan so the dev can see *what* they are getting. No music theory required."
4. **(2:30-3:00) The close.** Play the track over a mock boss-fight screen (optional). "100% local, 8 GB GPU, and the music is yours to ship -- individual devs sell games with YuE 2 music royalty-free. YuE-Studio: compose in game design, not in acoustic tokens."

**Demo hygiene:** cache carries the moment; live generation is something you *kick off and check back on*, never the load-bearing part of the pitch.

---

## 7. Risks & Fallbacks

| Risk | Likelihood | Mitigation / Fallback |
|------|-----------|----------------------|
| Ghost vocals bleed into "instrumental" output | Medium | Empty lyrics + `instrumental, no vocals` tag; audition all presets in Hour 1-2; regenerate offenders with different seeds |
| OOM / OOM-adjacent stall on 8 GB | Medium | `low_vram=True`, 30-60 s clips, find the token-cap parameter in `docs/generation.md` at Hour 1 |
| Generation too slow for live demo | High (expected) | Cache-first showcase -- preset buttons are the demo; live gen is garnish |
| Windows install friction | Medium | `setup.bat` run hours ahead; `yue2 doctor` as the objective check |
| Judge asks about licensing | Low | Use the exact corrected wording from section 1 -- never say "copyright-free" |
