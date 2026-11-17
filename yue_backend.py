"""Loads YuE2 once, generates clips, converts FLAC -> WAV, handles fallbacks.

Owner: P3. All API facts verified against API_NOTES.md (official docs).
"""

import json
import os

import soundfile as sf


class GenerationError(RuntimeError):
    """Raised when YuE2 generation fails or artifacts are incomplete."""


class YueStudio:
    def __init__(self, cache_dir="hf_cache"):
        self._pipe = None
        self.cache_dir = cache_dir

    @property
    def pipe(self):
        if self._pipe is None:
            from yue2 import YuE2Pipeline
            # low_vram: keeps only active AR/NAR modules on GPU -- the 8 GB path.
            # cache_dir keeps weights project-local (supported natively).
            self._pipe = YuE2Pipeline.from_pretrained(
                "m-a-p/YuE2-3B", device="cuda", low_vram=True,
                cache_dir=self.cache_dir)
        return self._pipe

    def generate(self, request, out_dir, on_progress=None):
        """Generate one clip. on_progress: YuE2 native callback(stage, completed, total)
        for stages 'nar' and 'vae' -- wire it straight into gr.Progress."""
        os.makedirs(out_dir, exist_ok=True)
        try:
            song = self.pipe(**request, on_progress=on_progress)
            song.save_artifacts(out_dir)
        except Exception as e:
            raise GenerationError(
                "YuE2 generation failed: %s -- likely OOM on 8 GB. "
                "Try a preset instead." % e) from e

        flac = os.path.join(out_dir, "audio.flac")
        score = os.path.join(out_dir, "score.abc")
        if not (os.path.exists(flac) and os.path.exists(score)):
            raise GenerationError("Generation finished but artifacts are missing.")

        # result.json carries the truncated flag: audio can be playable even
        # when the model hit the token limit -- surface this in the UI.
        truncated = False
        result_path = os.path.join(out_dir, "result.json")
        if os.path.exists(result_path):
            with open(result_path, "r", encoding="utf-8") as f:
                truncated = bool(json.load(f).get("truncated"))

        wav = os.path.join(out_dir, "audio.wav")
        data, sr = sf.read(flac)
        sf.write(wav, data, sr, subtype="PCM_16")
        return {
            "wav": wav,
            "flac": flac,
            "score": score,
            "truncated": truncated,
            "duration_s": round(len(data) / sr, 1),
        }

    def fallback_instrumental(self, score_path, out_path):
        """Official instrumental workflow (yue2-music skill v1.2.0): move Vocal
        notes into the Ins part, then re-render with the edited ABC.

        Simple merge: rename the V:Vocal header to V:Ins (keeps the notes, so the
        melody becomes the instrumental part). If the score already carries an
        Ins voice, the agent should append the Vocal body into that section
        instead -- validate against a real score.abc at the Hour-2 smoke test.
        """
        with open(score_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        out, merged = [], False
        for line in lines:
            if line.strip().upper().startswith("V:VOCAL"):
                out.append(line.replace("Vocal", "Ins", 1))
                merged = True
            else:
                out.append(line)
        if not merged:
            raise GenerationError("No V:Vocal voice found in score -- nothing to move.")
        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(out)
        return out_path

    def read_score(self, score_path):
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return "(score not available yet -- generate a track first)"
