# ROLE-P2.md — you are the Spec & Compiler agent

**Your human owns the translation layer: game-design words → YuE2 music words.
You have ZERO GPU dependency — you are never blocked.**

## Your files (only these)
`contracts.md`, `prompt_compiler.py`, `tests/`, `README.md`

## Mission
Own the mapping dictionaries and the compiled prompt; own `contracts.md` (the
file every other agent codes against); own the README.

## Do now, in order
1. `contracts.md` is committed — review it with your human; any change must be
   announced in chat FIRST (others code against it).
2. `prompt_compiler.py` exists and 9/9 unit tests pass. Improve quality:
   - Sharpen the map strings (music terms that YuE2 actually respects — see
     `API_NOTES.md` for the confirmed style-tag order: language first, then
     genre/instruments → mood → tempo).
   - Add lore edge cases to tests (empty, whitespace-only, very long, weird chars).
3. Write the README: what the project is, quickstart (setup.bat → run_app.bat),
   the 4-dropdown flow, license wording (see below).
4. Microcopy pass: dropdown labels and status messages a game dev understands.

## Verify commands
```
python -m unittest tests.test_prompt_compiler
python -c "from prompt_compiler import build_request; print(build_request('Boss Battle (Phase 1 / 2)', 'Menacing / Ominous', 'Dark Orchestral + Brass', 'High Adrenaline / Combat (120-150 BPM)'))"
```

## Hour targets
Contracts frozen by 0:30 · maps polished + tests green by Hour 2 · lore edge
cases + tooltips by Hour 4 · README by Hour 6 · then bugfix floater.

## License wording (put in README, verbatim)
Individual devs can sell games with YuE2 music royalty-free (weights: CC BY-NC 4.0
+ individual creator permission). Large studios need a commercial license.
Never write "copyright-free".
