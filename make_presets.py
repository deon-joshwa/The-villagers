"""Renders the 3 seed-pinned showcase tracks in the background. Owner: P1.

Run in the 3.12 venv AFTER setup.bat:  python make_presets.py
Real renders replace the placeholder silent WAVs in showcase/.
"""

import os
import shutil

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

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


def main():
    from yue2 import YuE2Pipeline
    from yue2.protocol import GenerationConfig, Sampling
    studio = YueStudio()
    pipe = YuE2Pipeline.from_pretrained(
        "m-a-p/YuE2-3B",
        device="cuda",
        low_vram=True,
        cache_dir="hf_cache",
        quantization="fp8",
        local_files_only=True
    )
    pipe.generation_config = GenerationConfig(
        abc=Sampling(0.7, 0.9, 30, 1.005, 100, 32, 1200),
        semantic=Sampling(1.0, 0.95, 100, 1.2, 50, 200, 2000),
        ode_steps=32
    )
    studio._pipe = pipe
    def on_progress(stage, completed, total):
        print(f"  [{stage}] {completed}/{total}", flush=True)

    for scene, mood, style, intensity, seed in PRESETS:
        target_wav = os.path.join("showcase", "showcase_%d.wav" % seed)
        target_abc = os.path.join("showcase", "showcase_%d.abc" % seed)
        if os.path.exists(target_wav) and os.path.getsize(target_wav) > 1_000_000 and not os.environ.get("REGEN_ALL"):
            print("Skipping seed %d: already rendered (%d bytes)" % (seed, os.path.getsize(target_wav)), flush=True)
            continue

        print(f"\n--- Generating Preset {seed}: {scene} / {mood} ---", flush=True)
        req = build_request(scene, mood, style, intensity,
                            seed=seed, track_id="showcase_%d" % seed)
        run_dir = os.path.join("outputs", "build_%d" % seed)
        out = studio.generate(req, run_dir, on_progress=on_progress)
        shutil.copy2(out["wav"], target_wav)
        shutil.copy2(out["score"], target_abc)
        print("Done: %s -> %s (truncated: %s, duration: %.1fs)" % (
            out["wav"], target_wav, out["truncated"], out.get("duration_s", 0.0)), flush=True)


if __name__ == "__main__":
    main()
