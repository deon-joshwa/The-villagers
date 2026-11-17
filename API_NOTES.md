# API_NOTES.md — Verified YuE2 API Facts (harvested from official docs, Nov 17 2026)

> Source: `multimodal-art-projection/YuE` @ `main` — README quick-start,
> `docs/generation.md`, `docs/hardware.md`. Latest release: `yue2-v0.1.6`
> (skill release: `yue2-music-v1.2.0`). Agents: **do not invent or rename anything
> not in this file.**

## Pipeline construction

```python
from yue2 import YuE2Pipeline
YuE2Pipeline.from_pretrained(
    "m-a-p/YuE2-3B",       # model repo on Hugging Face
    device="cuda",          # cuda | mps | xpu | cpu | auto
    low_vram=True,          # keep only active AR/NAR modules on GPU (8 GB path)
    cache_dir="hf_cache",   # project-local weight cache
    quantization="fp8",     # FP8 AR linear layers for Ada Lovelace (CC >= 8.9: RTX 40/50 series)
    # also supported: local_files_only=True, revision=..., vae_revision=...,
    # vae="m-a-p/YuE2-Vae" (default) | "m-a-p/YuE2-Vae-legacy" (benchmark decoder)
)
```

## Request JSON (one song)

| Key | Type | Notes |
|-----|------|-------|
| `id` | str | output identifier |
| `style` | str | comma tags, **language first**, then genre/instruments → mood → tempo. BPM goes here as a tag |
| `lyrics` | str | **empty string = instrumental (officially documented)**; section tags like `[Verse]` are for vocal songs |
| `cot` | str | `"full"` (melody+chords plan, default) \| `"melody"` \| `"off"` |
| `seed` | int | reproducibility |
| `abc` | str | optional: supply an edited score directly (requires `cot="full"` or `"melody"`) |
| `cfg_scale` | float | optional text-guidance; defaults are fine |

- **There is NO duration / clip-length / token-cap parameter.** Length follows the
  symbolic plan; on low VRAM it is effectively capped by the token budget (8 GB
  reference run used ~6,000 tokens, `low_vram=True`).
- `generate` and `batch` validate request fields before loading models
  (CLI: `yue2 validate --request examples/song.json`).

## Generation & progress

```python
song = pipe(**request, on_progress=callback)   # callback(stage, completed, total)
# stages: "nar" (midpoint steps), "vae" (tiles)
song.save_artifacts(out_dir)
print(song.truncated)
```

- One pipeline call = one candidate. A pipeline processes ONE request at a time.

## Artifacts (save_artifacts retains)

`audio.flac` (48 kHz stereo), `score.abc` (when applicable), `plan.json`, semantic
tokens, `latent.npy`, effective configuration, timings, model identities, integrity
records — plus `result.json` with **`truncated` flags**. Audio can be playable even
when the model hit a token limit. Use a fresh directory per changed request.

## Instrumental music (official)

- Use empty lyrics + describe instrumental in `style` ("instrumental, no vocals").
- **Upstream warning: vocal rests do not guarantee voice-free audio — listen to every result.**
- Fallback workflow (yue2-music skill v1.2.0): move every `Vocal` note into the `Ins`
  part of the ABC score (preserving pitch/onset/duration), then re-render with the
  edited ABC. The native score has exactly two voices: `Vocal` and `Ins`.

## Staged API (advanced)

`pipe.plan(**request)` → `SymbolicPlan.load(dir)` → `pipe.generate_semantic(plan)` →
`pipe.synthesize(semantic)` → `pipe.decode(latents)`. Saved latents can be re-decoded
without re-sampling (`yue2 decode runs/... /latent.npy --vae m-a-p/YuE2-Vae`).

## Hardware (docs/hardware.md, native reports)

- Official: Linux/Windows + NVIDIA, Python 3.12, BF16, 24 GB VRAM; PyTorch pinned
  **2.10.0** on Windows → install `torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128`.
- Low memory: `low_vram=True` (Python) / `--low-vram --budget 8` (CLI). FP8 AR weights
  optional on supported NVIDIA GPUs. Transfers need host RAM and reduce speed.
- Native report: **Windows, RTX 5060 Laptop 8 GB — completed songs** with BF16/FP8 AR,
  `low_vram=True`, 6,000-token cap. Length limits on small GPUs are not yet stable —
  long KV caches can still exhaust memory.
- Check environment: `yue2 doctor`.

## Environment facts (verified locally)

- This machine: Windows, Python 3.12 installed via `py -3.12` (system default Python 3.12.10).
- GPU verified: NVIDIA GeForce RTX 4060 Laptop GPU (8.0 GiB VRAM, compute capability 8.9).
- Setup verified: `torch==2.10.0+cu128`, `transformers==4.57.6`, `yue2-infer==0.1.6`.
- `yue2 doctor` passed with `dependencies_ready: true`.
- Smoke test located at `showcase/smoke_test.py`.
