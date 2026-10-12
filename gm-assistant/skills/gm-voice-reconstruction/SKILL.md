---
name: gm-voice-reconstruction
description: Voice-reconstruct the verbatim quote blocks in scene_extractions_new/ against each PC's voice file. Strips filler words and collapses false-start fragments; does not invent content. Produces a human-review table before touching any files. Invoke when the user says "voice reconstruct", "clean up the dialogue", "apply voice files to the scenes", "/gm-voice-reconstruction", or asks to reconstruct player dialogue against a voice file. Operates on one session directory at a time.
---

# gm-voice-reconstruction

Takes raw VTT-sourced dialogue in `scene_extractions_new/` and rewrites each PC's lines toward how that character would actually have said it, using their voice file as the target register. Output replaces the originals in-place after human review.

This skill is a **renderer, not an architect.** It makes lines feel like the character; it does not re-scope, re-attribute, or re-order. Quote-level VTT error correction (`/session-summary-consistency`) should be run first — this skill assumes proper nouns and garbled phrases are already fixed.

## When to invoke

Trigger phrases:
- "voice reconstruct the scenes"
- "clean up the dialogue against the voice files"
- "apply voice files to scene extractions"
- "/gm-voice-reconstruction"

## Inputs

- **session-dir** — the `summaries/YYYYMMDD/` directory to process. Default: CWD. Must contain `scene_extractions_new/`.
- **characters** — which PCs to reconstruct. Default: all PCs who have a voice file under `voice/` AND have lines in the scene files. Pass names to limit scope.

## Required context

- `voice/<character>_voice.md` for each PC being reconstructed — authoritative for register, vocabulary, speech patterns, and what they would never say.
- All `scene_extractions_new/*.md` files — source material.

## Workflow

### 1. Locate files

```bash
ls <session-dir>/scene_extractions_new/
ls <campaign-root>/voice/
```

If `scene_extractions_new/` is missing, stop. If no voice files exist, stop.

Walk up from `session-dir` to find the campaign root (directory containing `voice/`).

### 2. Read voice files

Read every `voice/<character>_voice.md` for the characters in scope. The **Speech Patterns — [Player] at the table** section is the primary reference for reconstruction — it describes what the player actually says out loud, not what the GM narrates. The narration sections describe in-world register and are secondary reference.

### 3. Reconstruct — parallel agents, one per scene

Spawn one agent per scene file. Each agent:

1. Reads the scene file.
2. For each PC line in `## Verbatim moments`, applies reconstruction per that character's voice profile.
3. Writes output to `<scene-name>_voiced.md` alongside the original.

**Reconstruction rules (apply to every PC line):**

| Rule | Detail |
|---|---|
| Strip filler | Remove "like", "you know", "um", "I mean", "Oh" as sentence-openers when they carry no content |
| Collapse false starts | Three lines converging on a decision → the one line they converged on |
| Flag unclear | If the meaning is genuinely unrecoverable, use `[unclear — probable "X"]` rather than guessing |
| Keep roll results | Damage math, initiative numbers, skill totals — verbatim even if oddly phrased |
| Keep single-word responses | "Yep." "Dead." "Good." "True." — these are already at the target register |
| Keep dry one-liners | Flat humor that is already characterful stays exactly as-is |
| Never add content | Do not invent anything not present in the original |

**GM/NPC/Calmer lines: always verbatim.** Only named PC lines get reconstructed.

**Speaker labels:** Character names only — player names must not appear in speaker labels.

### 4. Human review

Compile a before/after table of every changed line, grouped by scene:

```
## Scene N — filename.md

| Before | After |
|---|---|
| "original VTT line" | "reconstructed line" |
| "original VTT line" | `[unclear — probable "X"]` |
```

Present the full table in the conversation. Do not touch any files yet.

Ask:
> "These all look good, or do you want to change any calls?"

### 5. Apply corrections

If the user corrects specific calls, update the relevant `_voiced.md` files before the swap.

### 6. Swap files

Once the user approves:

```bash
for each scene file:
  mv <scene>.md <scene>.md.old
  mv <scene>_voiced.md <scene>.md
```

Originals are preserved as `.md.old`. The voiced files are now the live `.md` files.

Report the final count of reconstructed lines per character.

## Voice profile quick reference

The voice file's **Speech Patterns** section contains the authoritative table of what to strip and what to keep for each player. Common patterns across campaigns:

- **Tactical players** (mechanics-focused, minimal in-character voice): single-word responses and damage calls are already at target register — strip filler only, never rewrite the structure of a tactical declaration.
- **Narrative players** (voice their character extensively at table): the reconstruction is heavier — strip filler, collapse exploratory multi-line riffs into the statement they landed on.
- **Quiet players** (5–10% of table speech): their lines are usually already minimal; reconstruction may change almost nothing.

## Checkpoints

- **Before reconstruction:** run `/session-summary-consistency` first — this skill does not fix proper noun errors or VTT garbles. Both skills can run on the same session but this one should be second.
- **After compilation, before swap:** the human review table is a mandatory checkpoint. Never swap files without explicit user approval.
- **After swap:** the `.md.old` files preserve the pre-reconstruction originals. They are not committed unless the user requests it.

## What this skill is NOT for

- Fixing proper noun errors, garbled phrases, or VTT mishears (use `/session-summary-consistency`)
- Writing in-world narration from scratch (use `gm-session-prep` or the CampaignGenerator pipeline)
- Checking canon consistency between dialogue and grounding docs (use `/consistency-check`)
- Building or updating voice files (use `gm-npc-voice` for NPCs; for PCs, edit `voice/<character>_voice.md` directly after player correction)
