# ROLE-P1.md — you are the Model Wrangler's agent

**Your human owns the GPU, the environment, and everything that touches YuE2.
They are the only person allowed to run setup — protect their time.**

## Your files (only these)
`setup.bat`, `run_app.bat`, `API_NOTES.md`, `make_presets.py`, `showcase/`

**Branch:** ALL work happens on `dev` (one shared branch with the whole team).
`git pull` before you start; push right after verifying. Never commit to
`main` — see `GIT-WORKFLOW.md`. Your checkpoint: when the smoke test passes
(~Hour 2), P3 merges `dev` → `main` — have everything pushed before that.

## Mission
Get YuE2 installed and generating on the demo machine (Windows, 8 GB VRAM),
then render the 3 seed-pinned showcase tracks.

## Do now, in order
1. Human runs `setup.bat` — **Python 3.12 must be installed first** (system
   Python is 3.15; YuE2 pins 3.12). Model download is ~8 GB → start it early.
2. After install: `yue2 doctor`. Fix whatever it reports (you may edit `setup.bat`).
3. **Smoke test (the Hour-2 gate):** generate ONE clip with empty lyrics,
   `cot="full"`, `low_vram=True`, seed 831001, style from `prompt_compiler.SCENE/MOOD/STYLE/BPM_MAP`.
   Exit criteria: (a) no ghost vocals — human must LISTEN, (b) `score.abc` +
   `result.json` saved, (c) `truncated` flag and duration captured.
4. If pass → run `python make_presets.py` in the background; human auditions
   every track (upstream warns: voice-free output is NOT guaranteed).
5. Validate `YueStudio.fallback_instrumental` once against a real `score.abc`
   — the naive Vocal→Ins merge needs a real-score sanity check.
6. Pin final seeds by Hour 6.

## If the smoke test fails by Hour 2
Your human announces **"cache-only demo"** in chat — the plan absorbs it, do not
improvise new architectures. Try the HF-wheel install fallback or community
prebuilts first (see plan §2.3/§10).

## Facts you must respect
All in `API_NOTES.md`: `low_vram=True` is mandatory on 8 GB; no duration
parameter exists; `on_progress` callback signature is `(stage, completed, total)`.
