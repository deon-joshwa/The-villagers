# ROLE-P4.md — you are the UI agent

**Your human owns everything the user sees and clicks. You have ZERO GPU
dependency — stub mode means you can build and test the whole interface today.**

## Your files (only these)
`app.py`

## Mission
Own `app.py`: 4 dropdowns + boss-lore box, compiled-prompt preview, generate
button with live progress bar, ABC score viewer, WAV download, ghost-vocal
fallback button, instant showcase autoplay.

## Do now, in order
1. Install gradio in any Python: `pip install gradio` (full env comes later
   from P1's setup.bat).
2. Run in stub mode and click EVERYTHING:
   ```
   set YUE_STUB=1
   python app.py
   ```
3. Improve against the plan mockup (plan §2): dark theme `#12121a`, numbered
   dropdowns, lore placeholder text, "Ready." status line that becomes the
   duration/truncated report.
4. When P3's backend passes the Hour-4 checkpoint: flip stub off, test the
   real round-trip (coordinate with P1 — the GPU is busy).
5. Test the fallback button path — it must fail with a friendly `gr.Error`
   when no track was generated yet.

## Verify commands
```
set YUE_STUB=1 && python app.py     → click every button, confirm no tracebacks
python -m unittest tests.test_prompt_compiler   → still green (you didn't touch it)
```

## Hour targets
Dropdowns + preview + stub playback by Hour 2 · real backend wired by Hour 5 ·
polish + showcase autoplay by Hour 6 · bugfix standby after.

## Rules
- Dropdown options come ONLY from `prompt_compiler` maps (single source of truth).
- All failures surface as `gr.Error(...)` with a human sentence.
- `demo.queue()` stays — long generations need it.
