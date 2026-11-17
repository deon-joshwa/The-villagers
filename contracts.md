# OST.io — Interface Contracts (every agent codes against this)

> Single source of truth for how the pieces fit. Created at kickoff; changes require
> team sign-off in chat. File ownership: one file, one owner (see plan §7.2).

## 1. `prompt_compiler.py` (owner: P2)

```python
build_request(scene, mood, style, intensity, custom_lore="", seed=None, track_id=None)
```

- Returns a dict with EXACTLY these keys:
  - `"id": str` — `track_id` if given, else `"<scene first word>_<mood first word>"` lowercased
  - `"style": str` — compiled style string (language-first, instrumental tags last)
  - `"lyrics": ""` — always empty (instrumental; officially documented)
  - `"cot": "full"` — always (symbolic planning → editable ABC score)
  - `"seed": int` — pinned int if given, else 831001
- NO length/duration kwarg — YuE2 has none (confirmed in `docs/generation.md`).

Dropdown label sets (must match `app.py` dropdowns exactly):
- Scene: keys of `SCENE_MAP` — Mood: keys of `MOOD_MAP`
- Style: keys of `STYLE_MAP` — Intensity: keys of `BPM_MAP`

## 2. `yue_backend.py` (owner: P3)

```python
studio = YueStudio(cache_dir="hf_cache")           # lazy-loads YuE2 on first .generate
out = studio.generate(request, out_dir, on_progress=None)
```

- `on_progress`: YuE2 native signature `callback(stage, completed, total)`; stages `"nar"`, `"vae"`.
- Returns dict:
  - `"wav": str` path to 16-bit PCM WAV (converted from artifact FLAC)
  - `"flac": str` path to artifact FLAC
  - `"score": str` path to `score.abc`
  - `"truncated": bool` — from artifact `result.json`
  - `"duration_s": float` — actual audio length in seconds
- Raises `GenerationError` on failure (never lets raw exceptions escape).
- `studio.fallback_instrumental(score_path, out_path) -> str` — moves `Vocal` → `Ins`,
  returns edited ABC path. Caller re-renders with `request["abc"] = <edited file contents>`.

## 3. `app.py` (owner: P4)

- Dropdowns read label lists from `prompt_compiler` maps (single source of truth).
- `USE_STUB = os.environ.get("YUE_STUB") == "1"` → `do_generate` returns showcase files
  without touching the GPU (UI testing on any machine).
- Long generation MUST run through `demo.queue()`; all failures surface as `gr.Error(...)`.
- Status line shows duration and the truncated warning.

## 4. Showcase assets (owner: P1)

- `showcase/showcase_<seed>.wav` + `showcase/showcase_<seed>.abc` for seeds
  **831001, 831002, 831003** — produced by `make_presets.py` (real renders replace the
  placeholder silent WAVs committed with the scaffold).
- Seeds are pinned; never change them without updating `app.py` labels.

## 5. Ground rules

- One file, one owner. Nobody edits another person's file — propose in chat instead.
- Every kwarg in agent-produced code must exist in `API_NOTES.md`. Reject on review otherwise.
- Never commit unverified code: run the owner's verify commands first.
