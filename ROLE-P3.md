# ROLE-P3.md — you are the Integration agent

**Your human owns the middle layer: everything between the dropdowns and the
generated audio.**

## Your files (only these)
`yue_backend.py`

**Branch:** ALL work happens on `dev` (one shared branch with the whole team).
`git pull` before you start; push right after verifying. Never commit to
`main` — see `GIT-WORKFLOW.md`. **You are the MERGE MASTER:** you perform every
`dev` → `main` checkpoint merge (Hours 0.5, 2, 4, 6, final) — commands in
`GIT-WORKFLOW.md`.

## Mission
Own `yue_backend.py`: pipeline loader, `generate()` (progress + truncation +
FLAC→WAV), `fallback_instrumental()`, `read_score()`.

## Current state
Scaffold is complete but has NEVER run against real YuE2 (no GPU was available
at scaffold time). Treat it as unverified until P1's smoke test.

## Do now, in order
1. Re-read the scaffold against `API_NOTES.md` — check every kwarg
   (`low_vram`, `cache_dir`, `on_progress`) and every request key.
2. Prepare the integration test you will run with P1 at the Hour-4 checkpoint:
   `build_request(...)` → `studio.generate(request, "outputs/test")` → assert
   `wav/flac/score` exist, `truncated` is read from `result.json`,
   `duration_s` is sane, WAV is PCM_16.
3. When P1 announces the model works (Hour-2 gate): pull, run the round-trip,
   fix diffs (minimal changes only).
4. Wire with P4 at Hour 4: stub off, first full end-to-end run.
5. Make error paths friendly — a failed generation must raise
   `GenerationError` with a human sentence, never a raw traceback.

## Facts you must respect
- `on_progress` signature: `callback(stage, completed, total)`, stages `"nar"`, `"vae"`.
- `result.json` carries `truncated`; audio may be playable even when truncated.
- `save_artifacts` writes `audio.flac` (48 kHz stereo) + `score.abc`; fresh
  directory per changed request.
- NO duration kwarg exists — do not add one.
