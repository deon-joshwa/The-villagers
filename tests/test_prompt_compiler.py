"""Unit tests for prompt_compiler -- pure string logic, no GPU. Owner: P2.

Run inside the venv:  python -m pytest tests/ -q
(or: python -m unittest tests.test_prompt_compiler -- for stdlib-only runs)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_compiler import BPM_MAP, MOOD_MAP, SCENE_MAP, STYLE_MAP, build_request, compile_style


class TestCompileStyle(unittest.TestCase):
    def test_language_is_first_tag(self):
        s = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertTrue(s.startswith("English, "))

    def test_instrumental_tag_is_last(self):
        s = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertTrue(s.endswith("instrumental, no vocals"))

    def test_all_parts_present(self):
        s = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0],
                          list(STYLE_MAP)[0], list(BPM_MAP)[0])
        for part in (STYLE_MAP[list(STYLE_MAP)[0]], MOOD_MAP[list(MOOD_MAP)[0]],
                     SCENE_MAP[list(SCENE_MAP)[0]], BPM_MAP[list(BPM_MAP)[0]]):
            self.assertIn(part, s)

    def test_lore_appended_before_instrumental_tag(self):
        s = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0],
                          list(STYLE_MAP)[0], list(BPM_MAP)[0],
                          custom_lore="a rusted clockwork automaton")
        self.assertIn("scene inspiration: a rusted clockwork automaton, instrumental, no vocals", s)

    def test_blank_lore_ignored(self):
        a = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0], custom_lore="   ")
        b = compile_style(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertEqual(a, b)


class TestBuildRequest(unittest.TestCase):
    def test_exact_keys(self):
        req = build_request(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertEqual(set(req), {"id", "style", "lyrics", "cot", "seed"})

    def test_lyrics_empty_and_cot_full(self):
        req = build_request(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0])
        self.assertEqual(req["lyrics"], "")
        self.assertEqual(req["cot"], "full")

    def test_seed_pinned(self):
        req = build_request(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0], seed=1234)
        self.assertEqual(req["seed"], 1234)

    def test_id_from_track_id(self):
        req = build_request(list(SCENE_MAP)[0], list(MOOD_MAP)[0], list(STYLE_MAP)[0], list(BPM_MAP)[0], track_id="showcase_831001")
        self.assertEqual(req["id"], "showcase_831001")


if __name__ == "__main__":
    unittest.main()
