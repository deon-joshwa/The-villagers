# Q&A Cards — hold these for the judges' questions

One line each. Say the line, stop talking, wait for the next question.

---

## Card 1 — License

> "Individual devs sell games with YuE2 music royalty-free
> (CC BY-NC 4.0 + creator permission). Studios license it."

**NEVER say "copyright-free".** If pressed: individual creators get royalty-free
use for their games under CC BY-NC 4.0 plus the model creators' permission;
commercial studios beyond that scope negotiate a license.

## Card 2 — Hardware

> "Runs on an 8 GB gaming laptop with low-VRAM mode; official spec is 24 GB."

(That laptop is the one on the podium. `low_vram` is a supported
`from_pretrained` flag — see `API_NOTES.md`.)

## Card 3 — Why local

> "No cloud, no subscription, no takedowns — the weights are on the dev's machine."

If pressed: nothing leaves the laptop; the music ships with the game forever,
even if a service shuts down.

## Card 4 — Why YuE2

> "First open model to outscore Suno v5 on WildSongBench."

If pressed: and it's the *editable* kind of generation — YuE2 plans the melody
and chords as an ABC score first, which is exactly what our UI surfaces.

---

### Hard rules (from AGENTS.md / plan §10)

- License question → the exact wording above. **Never "copyright-free".**
- Never invent a YuE2 API parameter on stage. If asked for one that doesn't
  exist (e.g. "can I set exact duration?"), the honest answer is: "there is no
  duration parameter — the UI reports the real length and any truncation,
  and precise length control via ABC editing is on the roadmap."
