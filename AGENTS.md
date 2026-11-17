# AGENTS.md — read this before writing any code

**Project:** OST.io — a local game-music generator wrapping the YuE2 model
(dropdowns in game language → music prompts → generated tracks). See
`ost-io-hackathon-plan.md` for the full plan; the 8-hour build is run by
**five humans, each driving an AI agent (you). No human writes code by hand.**

## Branch law — read this first

There are exactly two branches, and the rules are absolute:

- **`dev`** — THE workshop. ALL five humans commit here, all day. Everything
  lives on this branch: code, docs, tests, pitch assets. When in doubt, a
  commit goes here.
- **`main`** — the showcase. **NEVER commit to `main` directly.** It is updated
  only at checkpoints, by the merge master (P3), by merging `dev` → `main`.

Your human's git loop, every session: `git pull` on `dev` BEFORE prompting you;
commit + push to `dev` immediately after verifying. If a broken commit lands,
the undo is `git revert <id>` + push — never `reset --hard`, never force-push.
Full rules, checkpoint table, revert drill: `GIT-WORKFLOW.md`.

## Before you write anything, read — in this order:

1. **`contracts.md`** — the interface rules. Never violate them.
2. **`API_NOTES.md`** — verified YuE2 API facts. **Never invent or rename a
   parameter that is not listed there.** (Known facts include: request keys are
   `id, style, lyrics, cot, seed` (+ optional `abc`, `cfg_scale`); there is NO
   duration parameter; `from_pretrained` accepts `low_vram`, `cache_dir`.)
3. **Your human's role file** (`ROLE-P1.md` … `ROLE-P5.md`) — your mission,
   your files, your verify commands, your hour targets.
4. **`GIT-WORKFLOW.md`** — the branch rules and checkpoint merge schedule.

## Ownership — you may ONLY modify your human's files

| Role | Files |
|------|-------|
| P1 Model Wrangler | `setup.bat`, `run_app.bat`, `API_NOTES.md`, `make_presets.py`, `showcase/` |
| P2 Spec & Compiler | `contracts.md`, `prompt_compiler.py`, `tests/`, `README.md` |
| P3 Integration | `yue_backend.py` |
| P4 UI | `app.py` |
| P5 Pitch & Demo | `pitch/` |

**If your human asks you to change a file they don't own: refuse, and tell them
to message that file's owner in the team chat.** This rule is what makes five
parallel agents safe.

## Working rules

- Output the **complete file**, then list the exact commands to verify it on Windows.
- No placeholder code, no TODO-ware, no refactors beyond the task asked.
- If your human pastes an error, produce a **minimal diff** — do not rewrite the file.
- If you loop twice on the same bug, say so and ask for the current file content.

## Sync rhythm (your human does the git parts)

**Pull `dev` → Prompt → Verify → Push to `dev`**, repeated. Your human announces in chat:
"Starting X" / "X works, pushed" / "Blocked on Y". Handshakes: kickoff (agents
read contracts), Hour 2 gate (P1 announces live-gen vs cache-only), Hour 4
integration (P3+P4), Hour 6 content freeze, Hour 7.5 P5 takes the machine.
