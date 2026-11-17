"""Renders the 3 seed-pinned showcase tracks in the background. Owner: P1.

Run in the 3.12 venv AFTER setup.bat:  python make_presets.py
Real renders replace the placeholder silent WAVs in showcase/.
"""

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
    studio = YueStudio()
    for scene, mood, style, intensity, seed in PRESETS:
        req = build_request(scene, mood, style, intensity,
                            seed=seed, track_id="showcase_%d" % seed)
        out = studio.generate(req, "showcase")
        print("done:", out["wav"], "truncated:", out["truncated"], flush=True)


if __name__ == "__main__":
    main()
