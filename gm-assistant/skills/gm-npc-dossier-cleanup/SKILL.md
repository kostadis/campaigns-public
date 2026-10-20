---
name: gm-npc-dossier-cleanup
description: Drive a campaign's summary-native NPC dossiers from "registered but undrafted / failing verify" to "GM-signed and published", in the order proven on Obelisk and Out of the Abyss — assess → identity checks → re-link → draft (Spark) → verify fixes + semantic read → ONE GM corrections page → apply → freeze → offline flag classification → create review exactly once → ≥90%-policy flags → GM sign-off page → ledger → publish → commit. Wraps CampaignGenerator's summary_native CLI; never reimplements it. Every wording change, sign-off, and identity ruling goes to the GM. Invoke as /gm-npc-dossier-cleanup [campaign-dir], or when the user says "clean up the NPC dossiers", "draft the remaining NPCs", "run the NPC workflow".
---

# gm-npc-dossier-cleanup

The procedure, its history and the reasons behind each step are in
`gm-assistant/working/summary-native-npc-dossiers/WORKFLOW.md`. Read it once per session before
starting. This skill is the runnable form of it: the order, the commands, and the checkpoints.

**Script:** `NDC="python3 <this skill>/scripts/ndc.py"`. Run it from the campaign directory. It reads the
range from `config/grounding.yaml summary_native` and keeps every run file in
`docs/npcs/summary_native/<range>/cleanup/<tag>/`. Those files are the record of what the GM was asked, so they
are committed. Pick one `<tag>` per run (e.g. `w2-20261012`) and pass `--run <tag>` to every call.

`SN="CG_BACKEND=claude-code ~/.venv/bin/summary_native"`. The backend guard refuses `summary_native`
without `CG_BACKEND`; `claude-code` is harmless for the deterministic subcommands. Drafting uses
`--backend dgx` with `CG_BACKEND=dgx`.

## Human checkpoints (never automate these)

| Step | Decision | Why |
|---|---|---|
| 0 | Scope, batching, Spark use | It costs the GM's review time and someone else's Spark |
| 1 | Any identity question (rename, alias, pair vs individuals, new entity, not-an-entity) | Identity is a scope decision |
| 5 | The wording of every edit (corrections page) | It changes canon prose the GM signs |
| 5 | Canon conflicts the readers surface (pronouns, names) | Precision decision; show every source |
| 8 | Sign-off per draft, and any checker flag under 90% confidence | Publication authority |
| 8 | Which source wins when a reject contradicts the summaries | The GM was at the table; show the VTT |

**GM policy (2026-10-11):** checker flags you are at least 90% sure the GM would approve are yours to
approve, with reviewer `Claude (GM-delegated policy)` and a reason. It never covers sign-offs, wording
changes, or names. An unanswered or ambiguous question is not a decision: re-ask. A DISCUSS note is not
a pre-approval: state your reading and confirm it; bring invented wording back as its own question.

Above roughly 12 rulings, use a review page, not chat (`../../CLAUDE.md`). Pages use the shared
review-page tools (`~/src/mytools/dotfiles/codex/skills/_shared/review-page/`, `CONTRACT.md`). Serve them
with `serve_review.py` over Tailscale so the GM can review on the phone. Check `ss -ltnp` for a free port,
and stop the server by the PID from `ss`, never with `pkill -f`.

## Phase 0 — Assess and scope (checkpoint)

1. Find the campaign's server: `ss -ltnp | grep 500` plus each PID's `--campaign-dir`. One server per
   campaign; start one with `python -m server.main --campaign-dir <dir> --config-dir config --port 5001`
   from `~/src/CampaignGenerator`.
2. Branch the campaign repo first (one campaign per branch): `git switch -c <campaign>/npc-dossiers-<tag>`.
3. `$NDC targets --run <tag> --server http://127.0.0.1:<port> --min-entries 1` prints the
   (draft, verify, published, exclusion) tally and how many `not in registry` names are **unruled**. Names
   ruled in an earlier triage page (`<range>/triage/*/`) are subtracted (CampaignGenerator#575).
4. Ask the GM, in one AskUserQuestion: which NPCs (by entry count; single-entry NPCs make thin dossiers),
   one batch or waves, and whether the Sparks are free. Expect about 6 corrections per draft. Then
   rerun `targets` with the chosen `--min-entries`.

## Phase 1 — Identity pass (checkpoint)

Before drafting, scan the target subjects for identity smells: parenthesised descriptors
(`X (Y)`), pairs (`A and B`), titles that duplicate another subject, descriptors that aren't names.
Read each one's `### Entry` text and its registry entry, then ask the GM. Rulings seen so far:
- a garbled canonical name → hand-edit `name:` in `docs/entity_registry.yaml`. There is no rename verb, so get
  explicit GM approval for the hand edit, add a `note:` recording the ruling, then `registry project .`;
- a pair (`Topsy and Turvy`) can be a legitimate entity for the twins together, next to the
  individuals. Ask; don't merge.
Unruled `not in registry` names go to an entity-triage page (WORKFLOW.md Phase 11 and Round 3 item 5;
template `working/.../scripts/entity_triage.html`). Save its items and decisions to
`<range>/triage/<tag>/` so later runs subtract them. Registry writes go only through
`~/.venv/bin/registry add|alias|mark-distinct|merge` (or the approved hand edit), then `registry project`.

**Never change the registry while a draft run is in flight.** The run records the registry sha.

## Phase 2 — Re-link and draft

1. If the registry or summaries changed: `$SN build ... --force`, then `$SN npc-link ... --force`
   (range args: `--summaries-dir docs/summaries --since S --until U`). Check `git status` on
   `evidence/`: if published NPCs' evidence changed, their sign-offs go stale. Say so.
2. Preview: `$SN npc-draft <range args> --backend dgx --name <subjects…> --dump-only`. Confirm that
   `runs/<id>/selection.json` `included` is exactly the targets, then **delete that run dir**.
3. Draft (background):
   `CG_BACKEND=dgx ~/.venv/bin/summary_native npc-draft <range args> --backend dgx --endpoints
   http://192.168.1.147:8001/v1 http://192.168.1.121:8001/v1 --parallel 2 --name <subjects…>`.
   `--parallel` is **per endpoint**. Expect ~2–3 min per NPC per slot; `0.0s` timings in the log are a
   display quirk. If it dies, `--resume <run-id>`.
4. `$NDC targets --run <tag> --from-draft-run <run-id>` pins the targets to what was actually drafted.

## Phase 3 — Verify fixes + semantic read (read-only on drafts)

1. `$NDC verify --run <tag>` writes `verify_failures.json`. For each failure, write the minimal fix as an
   edit in `cleanup/<tag>/edits/verify.json` (`[{id, stem, line, old, new, why}]`). Fix kinds:
   paraphrase in quotes → quote verbatim or drop the marks; case-only → match the source; outside-evidence
   cite → drop it; malformed cite → normalise. Check spans in the **evidence** file, with Python `re`.
2. Semantic read: split the targets into ~6 groups balanced by **evidence size**, and launch one read-only
   reader agent per group (Agent tool, `model: sonnet`, in one message). Fill `briefs/reader.md`'s
   `{CAMPAIGN_NAME} {CAMPAIGN_DIR} {RANGE_DIR} {STEMS} {SKIP} {NDC}`. `SKIP` = the verify-failure lines.
3. Send each reader `briefs/phase2.md` (SendMessage, same agent; fill `{RUN_DIR} {RANGE_DIR} {TAG}`). Each
   writes `edits/sem_<tag>.json`.
4. `$NDC check-edits --run <tag>`: every `old` occurs once, no overlaps, and the scratch copy still
   passes verify. Fix the edits until it exits 0. Then **spot-check ~15 edits yourself** against the
   evidence (`$NDC evidence <stem> 054/054.06`). Drop or fix anything that overstates.
5. Sweep for siblings: after a quoted-paraphrase fix, grep the draft and `gm/` copy for the same wording
   unquoted.

## Phase 4 — Canon conflicts (checkpoint)

For each conflict the readers raise: check the module (5etools `search`/`get_section`), then the canon
chain (`registry_resolve_name`). If nothing settles it, put one hand-written card per conflict in a JSON
file (same card schema) and pass it with `--extra`. After the ruling, fix the **source** summary
(`summaries/<session>/session-summary.md`) and mirror the identical line into `docs/summaries/`. Then add a
registry note and fix every draft that mentions the NPC (as edits).

`--extra` card ids are recorded in `corrections/extra_ids.json`. `approved-ids` lists them as RULINGs and keeps
them out of `approved_ids.json`: you carry out each ruling yourself (source fix, then edits).

**A source fix breaks custody on every earlier review that read that summary.** `npc-publish` refuses an
NPC whose review's custody sources changed, so the dossiers published by earlier waves can no longer be
republished until they are re-signed. Before you edit a source summary, tell the GM which earlier
reviews it will break. Then `build --force` and `npc-link --force`. Registry note edits also need
`build --force`.

## Phase 5 — GM corrections page (checkpoint)

`$NDC corrections-page --run <tag> [--extra conflicts.json]` builds one card per wording edit.
Citation-only edits get no card and are listed in the footer. Serve the page, give the GM the URL, and wait.
Then run `$NDC approved-ids --run <tag> --decisions <saved decisions.json>`. It validates the save and lists
every DISCUSS, UNDECIDED and note. Resolve each DISCUSS with AskUserQuestion, carrying the exact proposed
wording, and re-ask each UNDECIDED. Read notes on approved cards too, because a note can be a task. Record
follow-up wording as new edits, then add their ids to `approved_ids.json`.

## Phase 6 — Apply and freeze

`$NDC apply --run <tag> --ids cleanup/<tag>/corrections/approved_ids.json` dry-runs, writes, then runs
`npc-verify` and `npc-compose`. Every target must pass. From here on the drafts are **frozen**: any edit
after the review exists voids every sign-off in it (custody trap).

## Phase 7 — Offline flags, then create the review once

1. `$NDC flags --run <tag>` classifies the number/ordinal advisories as covered, chapter-ref or inspect.
   Read every **inspect** line against its cited items. A real citation gap or error goes back to
   Phase 5 as a correction (a small chat round if 12 or fewer) **before** the review exists.
2. `$NDC selection --run <tag>` refuses if any draft fails verify.
3. First review on a campaign: `$SN authority init --campaign-dir .` and `$SN review init --campaign-dir .`.
   Then `$SN review create --kind npc_verification --selection <path> --campaign-dir . --json`. Use the
   CLI, because the HTTP API hides the real error code.

## Phase 8 — Policy flags, sign-off page, ledger (checkpoint)

1. `$NDC policy --run <tag> --review <id>` approves typography and covered/chapter-ref flags and lists the
   rest in `gm_flags.json`. Check each one by hand. For the ones at ≥90%, write
   `{item_id: reason}` to a JSON file and rerun with `--approve-extra`. Apply every
   `ledger/policy_NN.json`: `$SN review decide <id> --decisions <file> --campaign-dir . --json`.
2. `$NDC signoff-page --run <tag> --review <id> --footer "<n> checker flags approved under your ≥90% policy"`.
   This gives one card per draft (full text and sha256) plus the flags still under 90%. Serve it and wait.
3. Every REJECT that contradicts the summaries gets checked against the VTT
   (`$NDC ctx <vtt> "<regex>" 3 3`). Show the GM the evidence and let them rule. If a claim fix is needed,
   that draft's bytes change: tell the GM it voids that sign-off, then follow WORKFLOW.md Phase 9 (split
   review).
4. `$NDC ledger --run <tag> --review <id> --decisions <saved json>` asserts that the draft bytes still match
   the page, then writes `ledger/gm_NN.json`. Apply them with `review decide`. UNMARKED is re-asked.
5. `$NDC gate --run <tag>` must say N/N. `$SN review status <id> --campaign-dir .` should show 0 pending.

## Phase 9 — Publish and ship

`$SN npc-publish <range args> --all` (expect refusals for undrafted NPCs). Commit on the campaign branch:
drafts, gm copies, evidence, `cleanup/<tag>/`, `triage/`, `docs/reviews/<id>/`, `docs/authority/`, the
registry and its projections. **Exclude** `.review-runtime/` and `docs/authority/.lock`. Then push and
open + merge the PR with `mcp__github__*`.
One campaign per commit/PR. Changes to this skill ship separately (gm-assistant).
