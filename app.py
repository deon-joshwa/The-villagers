"""OST.io UI -- Gradio Blocks. Owner: P4.

Run:  run_app.bat  (or: python app.py)
Stub: set YUE_STUB=1 to test the UI with zero GPU (returns showcase files).
"""

import os

import gradio as gr

from prompt_compiler import (BPM_MAP, MOOD_MAP, SCENE_MAP, STYLE_MAP,
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
CSS = ".gradio-container {background: #12121a; color: #e8e8f0;}"


def read_text(path, default=SAMPLE_ABC):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return default


with gr.Blocks(css=CSS, title="OST.io") as demo:
    gr.Markdown("# OST.io: Game Audio Synthesizer (Local)")
    with gr.Row():
        scene = gr.Dropdown(list(SCENE_MAP), label="1. Scene Context")
        mood = gr.Dropdown(list(MOOD_MAP), label="2. Mood / Atmosphere")
    with gr.Row():
        style = gr.Dropdown(list(STYLE_MAP), label="3. Music Style & Instruments")
        intensity = gr.Dropdown(list(BPM_MAP), label="4. Combat Intensity")
    lore = gr.Textbox(
        label="ADVANCED: Custom Scene / Boss Lore (optional)",
        placeholder="A giant clockwork automaton covered in rust, weeping oil as it attacks.")

    with gr.Accordion("Show Compiled YuE Prompt", open=False):
        preview = gr.Textbox(label="style", lines=3, interactive=False)
        preview_btn = gr.Button("Preview Compiled YuE Prompt")

    generate_btn = gr.Button("GENERATE TRACK (YuE 2)", variant="primary")
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

    preview_btn.click(
        lambda s, m, st, i, l: compile_style(s, m, st, i, l),
        [scene, mood, style, intensity, lore], preview)

    def do_generate(scene, mood, style, intensity, lore, progress=gr.Progress()):
        if USE_STUB:   # zero-GPU testing for the UI owner
            w, a = SHOWCASE[0][1], SHOWCASE[0][2]
            return w, read_text(a), w, "Stub mode: fake track loaded."
        if not os.path.isdir("showcase"):
            raise gr.Error("showcase/ not found. Run make_presets.py first (or YUE_STUB=1).")

        def cb(stage, done, total):     # YuE2 native stages: "nar", "vae"
            progress(done / max(total, 1), desc=stage.upper())

        try:
            req = build_request(scene, mood, style, intensity, lore, seed=42)
            out = studio().generate(req, os.path.join("outputs", req["id"]), on_progress=cb)
        except GenerationError as e:
            raise gr.Error(str(e))
        except Exception:
            raise gr.Error("Something went wrong. Try a preset instead.")
        note = "Done in %s s" % out["duration_s"]
        if out["truncated"]:
            note += " -- TRUNCATED by token cap (shorter than the plan asked for)"
        return out["flac"], read_text(out["score"]), out["wav"], note

    generate_btn.click(do_generate,
                       [scene, mood, style, intensity, lore],
                       [audio, score, wav_file, status])

    def do_fallback(scene, mood, style, intensity, lore):
        """Move Vocal -> Ins in the last generated score, re-render with abc=..."""
        if not os.path.isdir("outputs") or not os.listdir("outputs"):
            raise gr.Error("Nothing to fix yet -- generate a track first.")
        last = sorted(
            os.listdir("outputs"),
            key=lambda d: os.path.getmtime(os.path.join("outputs", d)))[-1]
        d = os.path.join("outputs", last)
        edited = studio().fallback_instrumental(
            os.path.join(d, "score.abc"), os.path.join(d, "score_ins.abc"))
        req = build_request(scene, mood, style, intensity, lore, seed=42)
        req["abc"] = read_text(edited)          # official path: supply edited score
        out = studio().generate(req, d + "_ins", on_progress=lambda s, c, t: None)
        return (out["flac"], read_text(out["score"]), out["wav"],
                "Re-rendered instrumental (Vocal moved to Ins). Listen once more.")

    fallback_btn.click(do_fallback,
                       [scene, mood, style, intensity, lore],
                       [audio, score, wav_file, status])

    for btn, (_, path, abc) in zip(preset_btns, SHOWCASE):
        btn.click(
            lambda p, a, pth=path, s=abc: (pth, read_text(s)),
            None, [preset_audio, score])


demo.queue()
demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
