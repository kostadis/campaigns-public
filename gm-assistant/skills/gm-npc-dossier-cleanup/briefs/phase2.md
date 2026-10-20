# Phase 2: turn your findings into exact edits (still READ-ONLY on the drafts)

1. Re-check each of your findings against the evidence, adversarially. Drop any where the source plausibly
   supports the draft, or where your fix would itself overstate. Keep only findings you'd defend to the GM.
2. Read {RUN_DIR}/edits/verify.json. It holds mechanical fixes {id, stem, line, old, new, why} already
   prepared for some lines. If one of your edits touches the same text span as a verify fix, write ONE
   combined edit that includes the verify fix's change too, and put that verify fix id in "supersedes".
   Otherwise leave verify fixes alone.
3. For each kept finding write an edit against the CURRENT draft file ({RANGE_DIR}/draft/<stem>.md):
   - "old": an exact substring of that line (copy it byte-for-byte from the file, including curly quotes,
     em dashes, asterisks). It must occur exactly once in that line. Keep it as short as possible while
     unique, but include the whole clause you change. Never span a line break.
   - "new": the replacement. Any text inside quote marks in "new" MUST be copied verbatim from this NPC's
     evidence file (no "…" inside a quote). Every sentence that makes a claim must keep a citation in the
     draft's format `[ch NNN / NNN.SS]`, `[ch NNN / entry]` or `[ch NNN / moment]`, and the cited item must be
     in this NPC's evidence. For a deletion, "new" may drop the clause entirely (keep the line grammatical).
   - Edits on the same line must not overlap each other.
   - A canon conflict (pronoun, name) gets NO edit: list it in your final message for the GM instead.
4. Write a JSON array to {RUN_DIR}/edits/sem_{TAG}.json with objects:
   {"id": "<stem-short>-L<line>-<n>", "stem": "npc_x", "line": <int>, "old": "...", "new": "...",
    "kind": "wrong speaker|unsupported|inference as fact|invented motive|contradiction|wrong time|overgeneralisation|relationship label|knowledge leak",
    "why": "<one sentence for the GM>", "evidence": "<item id> — \"<short verbatim excerpt>\"",
    "confidence": "high|medium", "supersedes": "<verify fix id or empty>"}
   Writing this one JSON file is the only write you may make.
5. Final message: the file path, how many findings you kept and how many you dropped (one line each on why
   dropped), and any canon conflicts for the GM.
