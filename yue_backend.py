"""Loads YuE2 once, generates clips, converts FLAC -> WAV, handles fallbacks.

Owner: P3. All API facts verified against API_NOTES.md (official docs).
"""

import json
import os
import re

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import soundfile as sf


class GenerationError(RuntimeError):
    """Raised when YuE2 generation fails or artifacts are incomplete."""


class YueStudio:
    def __init__(self, cache_dir="hf_cache", quantization="fp8"):
        self._pipe = None
        self.cache_dir = cache_dir
        self.quantization = quantization

    @property
    def pipe(self):
        if self._pipe is None:
            try:
                from yue2 import YuE2Pipeline
            except ImportError as e:
                raise GenerationError(
                    "YuE2 package is not installed. Please run setup.bat inside your Python 3.12 venv, "
                    "or set YUE_STUB=1 for zero-GPU testing."
                ) from e

            try:
                # low_vram: keeps only active AR/NAR modules on GPU -- the 8 GB path.
                # cache_dir keeps weights project-local (supported natively).
                # quantization="fp8": FP8 AR linear layers for 8 GB GPUs (RTX 40/50 series).
                load_kwargs = {
                    "device": "cuda",
                    "low_vram": True,
                    "cache_dir": self.cache_dir,
                }
                if self.quantization:
                    load_kwargs["quantization"] = self.quantization
                self._pipe = YuE2Pipeline.from_pretrained(
                    "m-a-p/YuE2-3B", **load_kwargs)
            except Exception as e:
                err_str = str(e).lower()
                if "out of memory" in err_str:
                    raise GenerationError(
                        "GPU out of memory while loading YuE2 model. Ensure other GPU processes are closed."
                    ) from e
                elif "cuda" in err_str and ("not available" in err_str or "no kernel" in err_str):
                    raise GenerationError(
                        "CUDA is not available or compatible GPU not detected. "
                        "YuE2 requires an NVIDIA GPU (or set YUE_STUB=1)."
                    ) from e
                else:
                    raise GenerationError(
                        "Failed to load YuE2 model from '%s': %s" % (self.cache_dir, e)
                    ) from e
        return self._pipe

    def generate(self, request, out_dir, on_progress=None, duration=None):
        """Generate one clip. on_progress: YuE2 native callback(stage, completed, total)
        for stages 'nar' and 'vae' -- wire it straight into gr.Progress.
        duration: Clip length in seconds (default: 45.0s, rate: 25 tokens/s).
        """
        os.makedirs(out_dir, exist_ok=True)
        dur = float(duration) if duration is not None else 45.0
        # 25 tokens per second for semantic AR audio (hop: 1920 @ 48kHz)
        semantic_tokens = min(3000, max(250, int(dur * 25)))
        # ABC planning: ~15 tokens per second (min 300, max 1200)
        abc_tokens = min(1200, max(300, int(dur * 15)))

        from yue2.protocol import Sampling
        abc_sampling = Sampling(temperature=0.7, top_p=0.9, top_k=30, repetition_penalty=1.005,
                                penalty_window=100, min_tokens=32, max_tokens=abc_tokens)
        semantic_sampling = Sampling(temperature=1.0, top_p=0.95, top_k=100, repetition_penalty=1.2,
                                     penalty_window=50, min_tokens=100, max_tokens=semantic_tokens)

        try:
            try:
                song = self.pipe(**request, abc_sampling=abc_sampling,
                                 semantic_sampling=semantic_sampling, on_progress=on_progress)
            except TypeError:
                song = self.pipe(**request, on_progress=on_progress)
            song.save_artifacts(out_dir)
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
        except GenerationError:
            raise
        except Exception as e:
            err_str = str(e).lower()
            if "out of memory" in err_str:
                raise GenerationError(
                    "YuE2 ran out of GPU memory (CUDA OOM on 8 GB). "
                    "Try a preset, lower intensity, or shorter scene prompt."
                ) from e
            elif "cuda" in err_str and ("not available" in err_str or "device" in err_str):
                raise GenerationError(
                    "CUDA device error during generation: %s. "
                    "Check NVIDIA driver or set YUE_STUB=1." % e
                ) from e
            else:
                raise GenerationError(
                    "YuE2 generation failed: %s. Try a preset instead." % e
                ) from e

        flac = os.path.join(out_dir, "audio.flac")
        score = os.path.join(out_dir, "score.abc")
        if not os.path.exists(flac):
            raise GenerationError("Generation completed but audio.flac is missing from %s." % out_dir)
        if not os.path.exists(score):
            raise GenerationError("Generation completed but score.abc is missing from %s." % out_dir)

        # result.json carries the truncated flag: audio can be playable even
        # when the model hit the token limit -- surface this in the UI.
        truncated = False
        result_path = os.path.join(out_dir, "result.json")
        if os.path.exists(result_path):
            try:
                with open(result_path, "r", encoding="utf-8") as f:
                    truncated = bool(json.load(f).get("truncated"))
            except Exception:
                truncated = False

        wav = os.path.join(out_dir, "audio.wav")
        try:
            data, sr = sf.read(flac)
            sf.write(wav, data, sr, subtype="PCM_16")
        except Exception as e:
            raise GenerationError("Audio conversion (FLAC -> PCM_16 WAV) failed: %s" % e) from e

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
        if not os.path.exists(score_path):
            raise GenerationError("Score file not found at '%s' -- generate a track first." % score_path)

        try:
            with open(score_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            raise GenerationError("Could not read score file at '%s': %s" % (score_path, e)) from e

        out, merged = [], False
        for line in lines:
            if re.match(r"^\s*V:\s*Vocal\b", line, re.IGNORECASE):
                out.append(re.sub(r"(?i)\bvocal\b", "Ins", line, count=1))
                merged = True
            else:
                out.append(line)

        if not merged:
            raise GenerationError(
                "No 'V:Vocal' voice found in score ('%s') -- nothing to move." % score_path
            )

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.writelines(out)
        except OSError as e:
            raise GenerationError("Could not write edited score to '%s': %s" % (out_path, e)) from e

        return out_path

    def read_score(self, score_path):
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return "(score not available yet -- generate a track first)"


def run_hour4_integration_test(out_dir="outputs/test_hour4", mock=False, studio=None):
    """Hour-4 Checkpoint Integration Test.

    Verification steps:
    1. build_request(...) via prompt_compiler
    2. studio.generate(request, out_dir)
    3. Assertions:
       - wav, flac, score exist on disk
       - truncated read directly from result.json matches out['truncated']
       - duration_s is sane (> 0 and < 600s)
       - WAV is 16-bit PCM (PCM_16)
    """
    from prompt_compiler import (BPM_MAP, MOOD_MAP, SCENE_MAP, STYLE_MAP,
                                 build_request)

    print("=" * 60)
    print("OST.io Hour-4 Checkpoint Integration Test")
    print("Mode: %s" % ("MOCK (artifact simulation)" if mock else "LIVE (YuE2 Model on CUDA)"))
    print("Output directory: %s" % out_dir)
    print("=" * 60)

    # 1. build_request
    scene = list(SCENE_MAP)[0]
    mood = list(MOOD_MAP)[0]
    style = list(STYLE_MAP)[0]
    intensity = list(BPM_MAP)[0]
    request = build_request(
        scene=scene,
        mood=mood,
        style=style,
        intensity=intensity,
        seed=831001,
        track_id="hour4_integration",
    )
    print("[1/4] Built request: id=%r, seed=%r" % (request["id"], request["seed"]))
    print("      Style prompt: %s..." % request["style"][:60])

    # 2. Prepare studio
    if studio is None:
        studio = YueStudio()

    if mock:
        class _MockSong:
            def __init__(self, truncated=False):
                self.truncated = truncated

            def save_artifacts(self, target_dir):
                import numpy as np
                os.makedirs(target_dir, exist_ok=True)
                flac_path = os.path.join(target_dir, "audio.flac")
                sr = 48000
                # Generate 2.0s of 48 kHz stereo audio
                samples = np.zeros((sr * 2, 2), dtype=np.float32)
                sf.write(flac_path, samples, sr, format="FLAC")

                score_path = os.path.join(target_dir, "score.abc")
                with open(score_path, "w", encoding="utf-8") as f:
                    f.write("X:1\nT:Hour 4 Checkpoint Test\nM:4/4\nL:1/8\nK:Am\nV:Vocal\nz8|]\nV:Ins\nz8|]\n")

                result_path = os.path.join(target_dir, "result.json")
                with open(result_path, "w", encoding="utf-8") as f:
                    json.dump({"truncated": self.truncated}, f)

        class _MockPipe:
            def __call__(self, *args, **kwargs):
                cb = kwargs.get("on_progress")
                if callable(cb):
                    cb("nar", 1, 2)
                    cb("nar", 2, 2)
                    cb("vae", 1, 1)
                return _MockSong(truncated=False)

        studio._pipe = _MockPipe()

    # Progress tracking callback
    stages_seen = []

    def on_progress(stage, done, total):
        stages_seen.append((stage, done, total))
        print("      [Progress] stage=%-4s completed=%d/%d" % (stage, done, total))

    # 3. generate
    print("[2/4] Calling studio.generate()...")
    out = studio.generate(request, out_dir=out_dir, on_progress=on_progress)
    print("      Generation finished successfully.")

    # 4. Assertions
    print("[3/4] Running checkpoint assertions...")

    # Assert wav, flac, score exist
    assert os.path.exists(out["wav"]), "Assertion failed: WAV file missing: %s" % out["wav"]
    assert os.path.exists(out["flac"]), "Assertion failed: FLAC file missing: %s" % out["flac"]
    assert os.path.exists(out["score"]), "Assertion failed: score.abc missing: %s" % out["score"]
    print("      PASS: wav, flac, and score.abc exist on disk.")

    # Assert truncated read from result.json
    result_path = os.path.join(out_dir, "result.json")
    assert os.path.exists(result_path), "Assertion failed: result.json missing at %s" % result_path
    with open(result_path, "r", encoding="utf-8") as f:
        result_data = json.load(f)
    assert "truncated" in result_data, "Assertion failed: 'truncated' key not found in result.json"
    expected_truncated = bool(result_data["truncated"])
    assert out["truncated"] == expected_truncated, (
        "Assertion failed: out['truncated'] (%r) does not match result.json (%r)"
        % (out["truncated"], expected_truncated)
    )
    print("      PASS: truncated flag (%r) successfully read from result.json." % out["truncated"])

    # Assert duration sane
    duration = out["duration_s"]
    assert isinstance(duration, (int, float)), "Assertion failed: duration_s is not numeric: %r" % duration
    assert 0.0 < duration < 600.0, "Assertion failed: duration_s is not sane (got %r s)" % duration
    print("      PASS: duration_s is sane (%.1f s)." % duration)

    # Assert WAV is PCM_16
    wav_info = sf.info(out["wav"])
    assert wav_info.format == "WAV", "Assertion failed: expected format WAV, got %s" % wav_info.format
    assert wav_info.subtype == "PCM_16", "Assertion failed: expected subtype PCM_16, got %s" % wav_info.subtype
    print("      PASS: WAV is PCM_16 (%d Hz, %d channels, subtype=%s)."
          % (wav_info.samplerate, wav_info.channels, wav_info.subtype))

    print("[4/4] ALL HOUR-4 CHECKPOINT ASSERTIONS PASSED!")
    print("=" * 60)
    return out


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Hour-4 integration test")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with mock pipeline (for testing without GPU / uninstalled weights)",
    )
    parser.add_argument(
        "--out-dir",
        default="outputs/test_hour4",
        help="Directory to save test outputs (default: outputs/test_hour4)",
    )
    args = parser.parse_args()
    run_hour4_integration_test(out_dir=args.out_dir, mock=args.mock)

