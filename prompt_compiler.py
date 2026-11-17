"""Translates game-design dropdowns into a YuE 2 request payload.

Owner: P2. Rules (see contracts.md + API_NOTES.md):
- YuE2 request keys are exactly: id, style, lyrics, cot, seed.
- Style string is language-first, then genre/instruments -> mood -> scene
  -> tempo -> lore -> instrumental tags last.
- lyrics is ALWAYS empty: YuE2 documents empty lyrics as the instrumental path,
  and it has NO duration parameter (length follows the symbolic plan / token cap).
"""

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
    """Dropdown labels -> one YuE2 style string. No GPU, instant."""
    parts = [
        "English",               # YuE2 wants the language tag FIRST
        STYLE_MAP[style],
        MOOD_MAP[mood],
        SCENE_MAP[scene],        # scene shapes arrangement/dynamics
        BPM_MAP[intensity],
    ]
    if custom_lore.strip():
        parts.append("scene inspiration: " + custom_lore.strip())
    parts.append("instrumental, no vocals")   # no instrumental mode -- enforce in text
    return ", ".join(parts)


def build_request(scene, mood, style, intensity, custom_lore="", seed=None, track_id=None):
    """Dropdown labels -> YuE2 request dict (see contracts.md for the shape)."""
    return {
        "id": track_id or (scene.split(" ")[0].lower() + "_" + mood.split(" ")[0].lower()),
        "style": compile_style(scene, mood, style, intensity, custom_lore),
        "lyrics": "",            # empty => instrumental (officially documented)
        "cot": "full",           # symbolic planning => editable ABC score (our UI feature)
        "seed": int(seed) if seed is not None else 831001,
    }
