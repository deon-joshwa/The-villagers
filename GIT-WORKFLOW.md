# GIT-WORKFLOW.md — five people, one shared branch, zero drama

**The rule in one sentence:** ALL work happens on `dev`; `main` is only updated
at checkpoints by the merge master (P3). Nobody ever commits to `main` directly.

## The two branches

| Branch | What it is | Who touches it |
|---|---|---|
| `dev` | The workshop. All code, docs, tests, pitch assets — everything, all day | All 5 people, constantly |
| `main` | The showcase. A known-good snapshot, updated only at checkpoints | P3 (merge master) only, via merge |

## First-time setup (once per person)

```
git clone https://github.com/deon-joshwa/The-villagers.git
cd The-villagers
git checkout dev
```

## The loop (every session, all day)

1. `git pull` — BEFORE you start prompting your AI (get everyone's latest)
2. Work with your AI — on YOUR files only (see the ownership map in `AGENTS.md`)
3. Verify it runs (tests / stub mode / click through the app)
4. Commit and push immediately:
   ```
   git add <your files>
   git commit -m "what works"
   git push
   ```

Push immediately after verifying. On a shared branch, unpushed work is
invisible to the team — the whole sync system runs on push-often.

## Checkpoint merges: `dev` → `main`

`main` only ever moves at these moments. The MERGE MASTER for every checkpoint
is **P3** — one person, no exceptions.

| Clock | Merge when... | Must be true on `dev` first |
|---|---|---|
| Hour 0.5 | Contracts + compiler land | `contracts.md`, `prompt_compiler.py`, green tests — everyone codes against this |
| Hour 2 | Model gate decided | P1's smoke test passed OR "cache-only" announced; setup scripts work |
| Hour 4 | Full round-trip works | First real song through the whole app (P3+P4 wired) |
| Hour 6 | Content freeze | The demo version is complete; from here only bugfixes |
| Final | The pitch version | Whatever the pitch shows is on `main` |

Merge-master commands (P3 only):

```
git checkout main
git pull
git merge dev --no-ff -m "Checkpoint Hour X: <what landed>"
git push
git checkout dev
git merge main
```

(The last `git merge main` keeps `dev` current with `main`, so nobody later
re-merges the same changes.)

## The revert drill (practice once at kickoff)

A broken commit on `dev` reaches everyone at their next pull — so undo it in
the open, in one minute:

```
git revert <commit-id>
git push
```

Everyone else: `git pull` and move on. The rules:

- NEVER `git reset --hard` on `dev` and NEVER force-push — that rewrites
  history all five people share.
- `git revert` is always safe: it adds a new commit that undoes an old one,
  so history stays intact and everyone stays in sync.

## If two people touch the same file anyway

The ownership map in `AGENTS.md` gives every file exactly one owner, so this
should never happen. If it does: the OWNER's version wins; the other person
re-applies their idea through the owner's AI. Never let two agents "merge"
each other's work by hand.

## Optional: make it physically enforced

GitHub repo → Settings → Branches → Add branch protection rule for `main`:
require a pull request before merging (blocks direct pushes). Then checkpoint
merges go through a `dev` → `main` PR, still performed by P3.
