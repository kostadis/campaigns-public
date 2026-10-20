# Semantic read of summary-native NPC dossier drafts (READ-ONLY)

Campaign: {CAMPAIGN_NAME}, dir {CAMPAIGN_DIR}
Drafts:   {RANGE_DIR}/draft/<stem>.md
Evidence: {RANGE_DIR}/evidence/<stem>.md   (the ONLY source a draft may use)

Your drafts: {STEMS}

Each draft sentence carries citations like `[ch 054 / 054.06]` (a scene), `[ch 054 / entry]` (the NPC's
`### Entry` in that chapter), `[ch 054 / moment]` (a `### Moment` block in that chapter). In the evidence file,
find the item under `## Chapter NNN` → `### Scene NNN.SS …` / `### Entry — …` / `### Moment …`.
Shortcut: `python3 {NDC} --campaign-dir {CAMPAIGN_DIR} evidence <stem> 054/054.06 054/entry` prints those items.

A mechanical verifier already confirmed quotes are verbatim and citations resolve. It does NOT check that the
cited item supports the sentence. That is your job. For every claim in every draft line, read the cited item(s)
and check the claim is actually supported.

Report problems of these kinds:
- wrong speaker / wrong actor (someone else said or did it)
- unsupported: nothing in the cited items (or anywhere in this NPC's evidence) supports it
- inference stated as fact (source says "suspect", "appears", "seems", party guess) → stated as fact
- invented motive, emotion, or intent not in the source ("out of cruelty", "deeply anxious", "loyalty")
- contradiction (source says otherwise: number, order, who, outcome, alive/dead, first time)
- wrong chapter/time (claim placed at the wrong point; "first" that isn't first)
- overgeneralisation (one incident turned into a habit: "frequently", "always", "often")
- a relationship label the source doesn't support (e.g. calling an NPC "a party member")
- a fact the party had not learned yet at that point (knowledge leak)
- a canon conflict between evidence items (e.g. he/she disagree across chapters) — report it, don't pick a side

Do NOT report: style, tone, omissions, things the evidence supports, typography, or the known verify failures
listed below (they are being fixed separately).

Known verify failures to skip (stem: lines): {SKIP}

Work method: Read the whole draft. For each line with claims, read the cited items. Be precise; check before
you report. Prefer fewer, solid findings over many weak ones. Be calibrated: if the source plausibly
supports it, don't report it. Do not edit any file.

Output (final message), one block per finding:

### <stem> L<line>
- claim: "<exact draft words at issue>"
- problem: <kind> — <one sentence>
- evidence: <item id, e.g. ch 054 / 054.06> — "<short verbatim source excerpt>"
- fix: <minimal replacement sentence/phrase. Any text you put in quote marks MUST be copied verbatim from this
  NPC's evidence; keep or correct the citation(s)>
- confidence: high | medium

End with a line: `checked: <stems> — <N> findings`.
