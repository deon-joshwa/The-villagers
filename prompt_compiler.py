"""Translates game-design dropdowns into a YuE 2 request payload.

Owner: P2. Rules (see contracts.md + API_NOTES.md):
- YuE2 request keys are exactly: id, style, lyrics, cot, seed.
- Style tag order (confirmed in API_NOTES.md): language FIRST, then
  genre/instruments -> mood -> tempo (BPM tag) -> scene -> lore ->
  instrumental tags LAST.
- lyrics is ALWAYS empty: YuE2 documents empty lyrics as the instrumental path,
  and it has NO duration parameter (length follows the symbolic plan / token cap).
"""

LORE_MAX_LEN = 200  # keep the style string tag-sized; longer lore gets cut

STYLE_MAP = {
    "Dark Orchestral + Brass":
        "dark cinematic orchestra, low brass stabs, taiko war drums, staccato cellos",
    "Cyberpunk / Industrial Synth":
        "gritty industrial synth, distorted analog bass, metallic percussion, dark arpeggio sequencer",
    "8-bit / 16-bit Retro Chiptune":
        "chiptune, square-wave lead, pulse-wave arpeggios, bit-crushed noise drums, NES-style bass",
    "Acoustic Folk / World":
        "acoustic folk, fingerpicked nylon guitar, warm fiddle, wooden flute, hand claps and foot stomps",
}

MOOD_MAP = {
    "Menacing / Ominous":      "ominous, menacing, slow-building dread, low register",
    "Tragic / Melancholic":    "melancholic, sorrowful, lyrical minor-key melody, weeping strings",
    "Whimsical / Playful":     "playful, whimsical, staccato pizzicato, bright major key",
    "Tense / Suspenseful":     "suspenseful, tense ostinato, creeping dynamics, unresolved harmony",
}

SCENE_MAP = {
    "Boss Battle (Phase 1 / 2)": "epic boss battle theme, driving percussion, rising intensity, layered climax",
    "Dungeon / Stealth":         "sparse stealth textures, sustained low drones, eerie ambience, sparse hits",
    "Safe Room / Tavern":        "cozy tavern ambience, intimate small ensemble, gentle loop-friendly phrase",
    "Open World Exploration":    "expansive exploration theme, evolving layered arrangement, wide stereo space",
}

BPM_MAP = {
    "Calm / Ambient (< 80 BPM)":              "slow tempo, 70 BPM",
    "Moderate / Exploration (90-110 BPM)":    "moderate tempo, 100 BPM",
    "High Adrenaline / Combat (120-150 BPM)": "fast driving tempo, 140 BPM",
    "Frenetic / Enraged (160+ BPM)":          "frenetic tempo, 170 BPM",
}

# Optional hover text for the UI dropdowns (P4 wires these into gr.Dropdown(info=...)).
# Copy a game dev understands: when this track plays, what is the player doing?
TOOLTIPS = {
    "scene": {
        "Boss Battle (Phase 1 / 2)": "Big fight music — phase changes just swap the mood dropdown",
        "Dungeon / Stealth":         "Quiet exploration where getting heard is a fail state",
        "Safe Room / Tavern":        "Rest, save points, no immediate threat",
        "Open World Exploration":    "Roaming the map between objectives — long-session friendly",
    },
    "mood": {
        "Menacing / Ominous":   "Something dangerous is near",
        "Tragic / Melancholic": "Loss, aftermath, sad story beats",
        "Whimsical / Playful":  "Light, comedic, cozy moments",
        "Tense / Suspenseful":  "On edge — enemy is close but hasn't spotted you",
    },
    "style": {
        "Dark Orchestral + Brass":      "Fantasy / AAA trailer sound",
        "Cyberpunk / Industrial Synth": "Sci-fi, neon, machines",
        "8-bit / 16-bit Retro Chiptune": "Retro / SNES-era sound",
        "Acoustic Folk / World":        "Villages, camps, low-fantasy warmth",
    },
    "intensity": {
        "Calm / Ambient (< 80 BPM)":              "Ambient / menus",
        "Moderate / Exploration (90-110 BPM)":    "Normal gameplay",
        "High Adrenaline / Combat (120-150 BPM)": "Combat encounters",
        "Frenetic / Enraged (160+ BPM)":          "Chases, final phase, panic",
    },
}


def _clean_lore(custom_lore):
    """Make custom lore safe for a comma-tag style string.

    - Collapses ALL whitespace (newlines, tabs, runs of spaces) to one space.
    - Strips control characters that could confuse the tag parser.
    - Truncates to LORE_MAX_LEN so the style string stays manageable.
    Returns "" when nothing usable is left.
    """
    text = "".join(ch for ch in str(custom_lore)
                   if ord(ch) >= 32 or ch in "\t\r\n")   # drop control junk, keep whitespace
    text = " ".join(text.split())                        # collapse ALL whitespace to one space
    if len(text) > LORE_MAX_LEN:
        text = text[:LORE_MAX_LEN].rsplit(" ", 1)[0]
    return text.strip()


def compile_style(scene, mood, style, intensity, custom_lore=""):
    """Dropdown labels -> one YuE2 style string. No GPU, instant."""
    parts = [
        "English",               # YuE2 wants the language tag FIRST
        STYLE_MAP[style],        # genre/instruments
        MOOD_MAP[mood],          # mood
        BPM_MAP[intensity],      # tempo (BPM tag lives here per API_NOTES.md)
        SCENE_MAP[scene],        # scene shapes arrangement/dynamics
    ]
    lore = _clean_lore(custom_lore)
    if lore:
        parts.append("scene inspiration: " + lore)
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
