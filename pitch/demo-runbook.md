# OST.io — 3-Minute Demo Runbook (one page)

**Cache-first law:** the showcase presets carry the moment. Live generation is
**kicked off and checked back on** — never the load-bearing part of the pitch.

## Pre-show (T-60 min, P5 human)

- [ ] `git pull` on `dev`; confirm `showcase\` has 3 `.wav` + 3 `.abc` files
- [ ] `run_app.bat` → browser opens `127.0.0.1:7860`; volume check on speakers
- [ ] Close all other tabs/windows. Open `pitch\slide1_yue2_comfyui_nodegraph.png`
      and `pitch\boss-fight-mock.png` in the image viewer, ready to full-screen
- [ ] Click each of the 3 preset buttons ONCE — audio must autoplay. Leave the
      preset tab alone afterwards (state stays warm)
- [ ] **Backup recorded:** screen-record the stub demo (`set YUE_STUB=1` +
      `python app.py`) and one preset playback. If the laptop dies, play the video.

## The 3-minute arc — exact click order

| Clock | Beat | Do exactly this |
|---|---|---|
| 0:00–0:40 | **The before** | Full-screen `pitch\slide1_yue2_comfyui_nodegraph.png`. Say the script (see `slide-1-the-before.md`). **Click 1:** switch to the OST.io browser tab. |
| 0:40–1:30 | **The four clicks** | **Click 2:** dropdown **"1. Scene Context"** → **Boss Battle (Phase 1 / 2)**. **Click 3:** **"2. Mood / Atmosphere"** → **Menacing / Ominous**. **Click 4:** **"3. Music Style & Instruments"** → **Dark Orchestral + Brass**. **Click 5:** **"4. Combat Intensity"** → **High Adrenaline / Combat (120-150 BPM)**. **Click 6:** in **"ADVANCED: Custom Scene / Boss Lore (optional)"** type: *"A giant clockwork automaton covered in rust, weeping oil as it attacks."* **Click 7:** open the **"Show Compiled YuE Prompt"** accordion → click **"Preview Compiled YuE Prompt"**. Point at the compiled **style** box: "watch the translation — game words became music prompts." |
| 1:30–2:30 | **Kick off + white-box reveal** | **Click 8:** press **"GENERATE TRACK (YuE 2)"** — the progress bar starts (NAR stage, then VAE). Say: "That will take a couple of minutes, and that's honest — watch what it's planning." **Click 9:** under **"Preset Showcase"** click **"Boss / Menacing / Dark Orchestral"** — the **"Showcase playback"** panel starts playing instantly (cache). Point at the **"Generated ABC Score (melody & chords)"** panel that just filled: "YuE 2 plans the melody and chords as symbols first — our UI surfaces that plan so the dev can see *what* they are getting. No music theory required." Scroll the score slowly. |
| 2:30–3:00 | **The close** | **Click 10:** switch to the full-screen `pitch\boss-fight-mock.png` while the preset track plays. Close line: "100% local, 8 GB GPU, and the music is yours to ship — individual devs sell games with YuE 2 music royalty-free. OST.io: compose in game design, not in acoustic tokens." |
| After Q&A | **Check back** | Glance at the live generation: the **"Playback"** panel + **"Download .WAV for Unity"** are filled and the status line shows "Done in … s" (or the honest "TRUNCATED by token cap" note). If it errored — the UI shows a friendly message — say "and that's why presets carry the demo," and show the recorded backup. |

## Talk-ammo (P2's dropdown HELP lines, from prompt_compiler.py)

Drop one of these per beat 2 click — they explain game value, not music theory:
- Boss Battle: *"Big fight music — phase changes just swap the mood dropdown."*
- Dungeon / Stealth: *"Quiet exploration where getting heard is a fail state."*
- Tense / Suspenseful: *"On edge — the enemy is close but hasn't spotted you."*

## Failure drills

- **Live gen errors/OOM on stage:** the friendly red message appears — click a
  different preset button and keep talking. Never debug live.
- **Ghost vocals in a preset:** click **"Fix Ghost Vocals (move Vocal -> Ins, re-render)"**
  only during rehearsal, never on stage — use a different preset instead.
- **Whole app dead:** play the pre-recorded backup video over `boss-fight-mock.png`.

## Verify (P5, before every rehearsal)

1. This file is one page. 2. Every click above exists in `app.py` as shipped
(checked against labels: 4 dropdowns, boss-lore textbox, "Preview Compiled YuE
Prompt", "GENERATE TRACK (YuE 2)", preset buttons, playback/score panels).
3. Timing hits 3:00 in rehearsal #1 (Hour 4–5), #2 (Hour 6–7), final 7.5.
