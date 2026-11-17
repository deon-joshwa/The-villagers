"""Unit tests for prompt_compiler -- pure string logic, no GPU. Owner: P2.

Run inside the venv:  python -m pytest tests/ -q
(or: python -m unittest tests.test_prompt_compiler -- for stdlib-only runs)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_compiler import (
    BPM_MAP, LORE_MAX_LEN, MOOD_MAP, SCENE_MAP, STYLE_MAP,
    build_request, compile_style,
)


def _first(**_):
    return tuple()


class TestCompileStyle(unittest.TestCase):
    def setUp(self):
        self.args = (list(SCENE_MAP)[0], list(MOOD_MAP)[0],
                     list(STYLE_MAP)[0], list(BPM_MAP)[0])

    def test_language_is_first_tag(self):
        self.assertTrue(compile_style(*self.args).startswith("English, "))

    def test_instrumental_tag_is_last(self):
        self.assertTrue(compile_style(*self.args).endswith("instrumental, no vocals"))

    def test_all_parts_present(self):
        s = compile_style(*self.args)
        for part in (STYLE_MAP[self.args[2]], MOOD_MAP[self.args[1]],
                     SCENE_MAP[self.args[0]], BPM_MAP[self.args[3]]):
            self.assertIn(part, s)

    def test_tag_order_matches_api_notes(self):
        # API_NOTES.md: language -> genre/instruments -> mood -> tempo.
        s = compile_style(*self.args)
        self.assertLess(s.index("English, "), s.index(STYLE_MAP[self.args[2]]))
        self.assertLess(s.index(STYLE_MAP[self.args[2]]), s.index(MOOD_MAP[self.args[1]]))
        self.assertLess(s.index(MOOD_MAP[self.args[1]]), s.index(BPM_MAP[self.args[3]]))
        self.assertLess(s.index(BPM_MAP[self.args[3]]), s.index(SCENE_MAP[self.args[0]]))
        self.assertLess(s.index(SCENE_MAP[self.args[0]]), s.index("instrumental, no vocals"))

    def test_lore_appended_before_instrumental_tag(self):
        s = compile_style(*self.args, custom_lore="a rusted clockwork automaton")
        self.assertIn("scene inspiration: a rusted clockwork automaton, instrumental, no vocals", s)

    def test_lore_empty_ignored(self):
        self.assertEqual(compile_style(*self.args, custom_lore=""),
                         compile_style(*self.args))

    def test_lore_whitespace_only_ignored(self):
        for junk in ("   ", "\n\t \t\n", " \u00a0 "):
            self.assertEqual(compile_style(*self.args, custom_lore=junk),
                             compile_style(*self.args))

    def test_lore_newlines_and_tabs_collapsed(self):
        s = compile_style(*self.args,
                          custom_lore="haunted\r\nmine\tshaft,\t one lantern")
        self.assertIn("scene inspiration: haunted mine shaft, one lantern", s)
        self.assertNotIn("\n", s)
        self.assertNotIn("\t", s)

    def test_lore_control_chars_stripped(self):
        s = compile_style(*self.args, custom_lore="c\x00r\x1beep\x07y corridor")
        self.assertIn("scene inspiration: creepy corridor", s)

    def test_lore_very_long_truncated(self):
        long_lore = "word " * 200  # 1000 chars
        s = compile_style(*self.args, custom_lore=long_lore)
        self.assertIn("scene inspiration: ", s)
        self.assertNotIn("word word word word " * 20, s)  # clearly cut down
        self.assertLess(s.index("instrumental, no vocals") - s.index("scene inspiration: "),
                        LORE_MAX_LEN + len("scene inspiration: ") + 2)

    def test_lore_cannot_break_instrumental_tag(self):
        # Even if the lore mentions vocals, the enforced instrumental tag stays last.
        s = compile_style(*self.args, custom_lore="a ghost choir of vocals sings")
        self.assertTrue(s.endswith("instrumental, no vocals"))

    def test_all_map_values_are_single_line_tags(self):
        for mapping in (STYLE_MAP, MOOD_MAP, SCENE_MAP, BPM_MAP):
            for label, tags in mapping.items():
                self.assertNotRegex(tags, r"[\r\n]", f"{label!r} in {mapping}")
                self.assertLess(len(tags), 200, f"{label!r} in {mapping}")


class TestBuildRequest(unittest.TestCase):
    def setUp(self):
        self.args = (list(SCENE_MAP)[0], list(MOOD_MAP)[0],
                     list(STYLE_MAP)[0], list(BPM_MAP)[0])

    def test_exact_keys(self):
        req = build_request(*self.args)
        self.assertEqual(set(req), {"id", "style", "lyrics", "cot", "seed"})
        self.assertNotIn("duration", {k.lower() for k in req})  # YuE2 has NO duration kwarg

    def test_lyrics_empty_and_cot_full(self):
        req = build_request(*self.args)
        self.assertEqual(req["lyrics"], "")
        self.assertEqual(req["cot"], "full")

    def test_seed_pinned(self):
        self.assertEqual(build_request(*self.args, seed=1234)["seed"], 1234)
        self.assertEqual(build_request(*self.args)["seed"], 831001)  # contract default

    def test_id_from_track_id(self):
        req = build_request(*self.args, track_id="showcase_831001")
        self.assertEqual(req["id"], "showcase_831001")

    def test_id_default_from_words(self):
        req = build_request("Boss Battle (Phase 1 / 2)", "Menacing / Ominous",
                            list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertEqual(req["id"], "boss_menacing")


if __name__ == "__main__":
    unittest.main()
