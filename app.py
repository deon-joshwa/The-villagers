"""OST.io UI -- Gradio Blocks. Owner: P4.

Run:  run_app.bat  (or: python app.py)
Stub: set YUE_STUB=1 to test the UI with zero GPU (returns showcase files).

Dropdown options come ONLY from prompt_compiler maps (single source of truth).
All failures surface as gr.Error(...) with a human sentence. demo.queue() stays
-- long generations need it.
"""

import inspect
import os
import time

import gradio as gr

from prompt_compiler import (BPM_MAP, MOOD_MAP, SCENE_MAP, STYLE_MAP, TOOLTIPS,
                             build_request, compile_style)
from yue_backend import GenerationError, YueStudio

USE_STUB = os.environ.get("YUE_STUB") == "1"   # UI testing with zero GPU
_studio = None


def studio():
    global _studio
    if _studio is None:
        _studio = YueStudio()
    return _studio


SHOWCASE = [  # pre-rendered by make_presets.py, seed-pinned (see contracts.md)
    ("Boss / Menacing / Dark Orchestral", "showcase/showcase_831001.wav", "showcase/showcase_831001.abc"),
    ("Dungeon / Tense / Cyberpunk",       "showcase/showcase_831002.wav", "showcase/showcase_831002.abc"),
    ("Tavern / Whimsical / Folk",         "showcase/showcase_831003.wav", "showcase/showcase_831003.abc"),
]

SAMPLE_ABC = "X:1\nT:stub score\nM:4/4\nL:1/8\nK:Am\n"

# Plan mockup: dark theme #12121a, light text, glowing primary button.
CSS = """
.gradio-container {background: #12121a !important; color: #e8e8f0 !important;}
.gradio-container h1, .gradio-container h2, .gradio-container h3 {color: #f4f4fa !important;}
footer {display: none !important;}
button.primary {background: #7c4dff !important; border: none !important; color: white !important;}
button.primary:hover {background: #8f66ff !important;}
button.secondary, button:not(.primary):not(.lg) {background: #1d1d2b !important; color: #e8e8f0 !important; border: 1px solid #34344a !important;}
input, textarea, .wrap {background: #1d1d2b !important; color: #e8e8f0 !important;}
.block, .form {border-color: #34344a !important; background: #1d1d2b !important;}
label span {color: #c9c9d8 !important; background: transparent !important;}
.gradio-container {
  --block-label-background-fill: #1d1d2b;
  --block-label-text-color: #c9c9d8;
  --block-background-fill: #1d1d2b;
  --button-secondary-background-fill: #1d1d2b;
  --button-secondary-text-color: #e8e8f0;
}
[data-testid="file"], .file-preview {
  background: #1d1d2b !important; color: #e8e8f0 !important; border-color: #34344a !important;}
.icon-button, button.download-button {
  background: #1d1d2b !important; color: #e8e8f0 !important; border: 1px solid #34344a !important;}
.gradio-container .prose p {color: #c9c9d8 !important;}
.ostio-logo-container, .ostio-logo-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}
.ostio-logo-img {
  height: 56px;
  max-width: 220px;
  object-fit: contain;
  display: block;
  -webkit-mask-image: radial-gradient(ellipse 95% 90% at 50% 50%, black 70%, transparent 100%);
  mask-image: radial-gradient(ellipse 95% 90% at 50% 50%, black 70%, transparent 100%);
  transition: transform 0.25s ease, filter 0.25s ease;
}
.ostio-logo-container:hover .ostio-logo-img, .ostio-logo-badge:hover .ostio-logo-img {
  transform: scale(1.02);
  filter: drop-shadow(0 0 10px rgba(124, 77, 255, 0.4));
}
"""


def get_header_html():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "ostio.png")
    img_tag = ""
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        img_tag = f'<img class="ostio-logo-img" src="data:image/png;base64,{b64}" alt="OST.io Logo" />'
    return f"""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 16px; flex-wrap: wrap;">
        <div class="ostio-logo-container">
            {img_tag}
        </div>
        <div>
            <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 700; color: #f4f4fa; letter-spacing: -0.5px;">OST.io — Game words in. Game music out.</h1>
            <p style="margin: 4px 0 0 0; color: #a5a5c0; font-size: 1.05rem;">Four game-design dropdowns → an optimized music prompt → a game-ready track + the ABC score it planned.</p>
        </div>
    </div>
    """


def read_text(path, default=SAMPLE_ABC):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return default


def require_selections(scene, mood, style, intensity):
    """One friendly error naming what's missing, instead of a KeyError traceback."""
    missing = [name for name, value in (
        ("Scene (1)", scene), ("Mood (2)", mood),
        ("Style (3)", style), ("Intensity (4)", intensity)) if not value]
    if missing:
        raise gr.Error("Pick " + ", ".join(missing) + " first.")


def safe_preview(scene, mood, style, intensity, lore):
    """Live preview that never raises -- shows a hint until all 4 are picked."""
    try:
        require_selections(scene, mood, style, intensity)
    except gr.Error as e:
        return str(e.message) if hasattr(e, "message") else "Pick all four dropdowns first."
    return compile_style(scene, mood, style, intensity, lore)


# NOTE (P2 emergency fix, announced in chat): gradio 5 wants css on the
# Blocks constructor; gradio 6 REMOVES it there and wants it on launch().
# Detect which one this install supports. P4 owns this file -- please
# review/adopt.
_LAUNCH_TAKES_CSS = "css" in inspect.signature(gr.Blocks.launch).parameters
_BLOCKS_CSS = {} if _LAUNCH_TAKES_CSS else {"css": CSS}

with gr.Blocks(title="OST.io", **_BLOCKS_CSS) as demo:
    gr.HTML(get_header_html())

    with gr.Row():
        scene = gr.Dropdown(
            list(SCENE_MAP), label="1. Scene Context",
            info="When does this track play?", scale=1)
        mood = gr.Dropdown(
            list(MOOD_MAP), label="2. Mood / Atmosphere",
            info="What is the player feeling?", scale=1)
    with gr.Row():
        style = gr.Dropdown(
            list(STYLE_MAP), label="3. Music Style & Instruments",
            info="The sound palette", scale=1)
        intensity = gr.Dropdown(
            list(BPM_MAP), label="4. Combat Intensity",
            info="How fast is the action?", scale=1)
    with gr.Row():
        lore = gr.Textbox(
            label="ADVANCED: Custom Scene / Boss Lore (optional)",
            placeholder="A giant clockwork automaton covered in rust, weeping oil as it attacks.",
            scale=3)
        duration_slider = gr.Slider(
            minimum=15, maximum=120, value=45, step=5,
            label="Duration (seconds)",
            info="Clip length (25 tokens/s). 30-45s is fastest (~2-3 min); 80s takes ~6 min.",
            scale=1)

    with gr.Accordion("Show Compiled Prompt", open=False):
        preview = gr.Textbox(label="style", lines=4, interactive=False)
        preview_btn = gr.Button("Preview Compiled Prompt")

    generate_btn = gr.Button("GENERATE TRACK", variant="primary")
    status = gr.Markdown("Ready.")   # duration + truncated flag land here

    with gr.Row():
        audio = gr.Audio(label="Playback", type="filepath")
        score = gr.Code(label="Generated ABC Score (melody & chords)", language="markdown")
    with gr.Row():
        wav_file = gr.File(label="Download .WAV for Unity")
        fallback_btn = gr.Button("Fix Ghost Vocals (move Vocal -> Ins, re-render)")

    gr.Markdown("## Preset Showcase")
    with gr.Row():
        preset_btns = [gr.Button(name) for name, _, _ in SHOWCASE]
    preset_audio = gr.Audio(label="Showcase playback", type="filepath", autoplay=True)

    # --- preview: button + live update on every change (free, instant, no GPU) ---
    inputs5 = [scene, mood, style, intensity, lore]
    preview_btn.click(safe_preview, inputs5, preview)
    for comp in inputs5:
        comp.change(safe_preview, inputs5, preview)

    # --- tooltips: per-option hover text from prompt_compiler.TOOLTIPS (single
    #     source of truth); static hint until a selection is made ---
    _HINTS = {"scene": "When does this track play?", "mood": "What is the player feeling?",
              "style": "The sound palette", "intensity": "How fast is the action?"}

    def _tip_fn(key):
        def fn(sel):
            return gr.update(info=TOOLTIPS[key].get(sel, _HINTS[key]))
        return fn

    for comp, key in ((scene, "scene"), (mood, "mood"),
                      (style, "style"), (intensity, "intensity")):
        comp.change(_tip_fn(key), comp, comp)

    # --- generate: stub path returns showcase files; real path wires gr.Progress ---
    def do_generate(scene, mood, style, intensity, lore, duration_sec, progress=gr.Progress()):
        require_selections(scene, mood, style, intensity)
        if USE_STUB:   # zero-GPU testing for the UI owner
            progress(1.0, desc="STUB")
            w, a = SHOWCASE[0][1], SHOWCASE[0][2]
            return w, read_text(a), w, "**Stub mode:** fake track loaded (showcase_831001)."
        if not os.path.isdir("showcase"):
            raise gr.Error("showcase/ not found. Run make_presets.py first (or YUE_STUB=1).")

        def cb(stage, done, total):     # YuE2 native stages: "nar", "vae"
            progress(done / max(total, 1), desc=stage.upper())

        t0 = time.time()
        try:
            req = build_request(scene, mood, style, intensity, lore, seed=42)
            out = studio().generate(req, os.path.join("outputs", req["id"]), on_progress=cb, duration=duration_sec)
        except GenerationError as e:
            raise gr.Error(str(e))
        except Exception:
            raise gr.Error("Something went wrong. Try a preset instead.")
        elapsed = time.time() - t0
        note = "**Done in %.1fs (%.1fs track generated).**" % (elapsed, out.get("duration_s", duration_sec))
        if out["truncated"]:
            note += " ⚠️ **TRUNCATED** by the token cap (shorter than the plan asked for)."
        return out["flac"], read_text(out["score"]), out["wav"], note

    generate_btn.click(do_generate,
                       [scene, mood, style, intensity, lore, duration_slider],
                       [audio, score, wav_file, status])

    # --- ghost-vocal fallback: stub-aware, friendly error before any generation ---
    def do_fallback(scene, mood, style, intensity, lore, duration_sec, progress=gr.Progress()):
        if USE_STUB:
            progress(1.0, desc="STUB")
            w, a = SHOWCASE[0][1], SHOWCASE[0][2]
            return w, read_text(a), w, "**Stub mode:** fallback faked (no GPU here)."
        if not os.path.isdir("outputs") or not os.listdir("outputs"):
            raise gr.Error("Nothing to fix yet — generate a track first.")
        require_selections(scene, mood, style, intensity)
        last = sorted(
            os.listdir("outputs"),
            key=lambda d: os.path.getmtime(os.path.join("outputs", d)))[-1]
        d = os.path.join("outputs", last)

        def cb(stage, done, total):
            progress(done / max(total, 1), desc=stage.upper())

        try:
            edited = studio().fallback_instrumental(
                os.path.join(d, "score.abc"), os.path.join(d, "score_ins.abc"))
            req = build_request(scene, mood, style, intensity, lore, seed=42)
            req["abc"] = read_text(edited)          # official path: supply edited score
            out = studio().generate(req, d + "_ins", on_progress=cb, duration=duration_sec)
        except GenerationError as e:
            raise gr.Error(str(e))
        except Exception:
            raise gr.Error("Re-render failed. The original track is untouched — try generating again.")
        return (out["flac"], read_text(out["score"]), out["wav"],
                "**Re-rendered instrumental** (Vocal moved to Ins). Listen once more.")

    fallback_btn.click(do_fallback,
                       [scene, mood, style, intensity, lore, duration_slider],
                       [audio, score, wav_file, status])

    # --- showcase presets: instant autoplay, score loaded too ---
    for btn, (_, path, abc) in zip(preset_btns, SHOWCASE):
        btn.click(
            lambda pth=path, s=abc: (pth, read_text(s)),
            None, [preset_audio, score])


demo.queue()
if __name__ == "__main__":
    if _LAUNCH_TAKES_CSS:
        demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, css=CSS)
    else:
        demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
