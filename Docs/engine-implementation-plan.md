# Implementation Plan

Phased build plan for the discovery engine. Derived from `engine-context.md` and `engine-architecture.md`.

**Rule for the whole plan: do not start a phase until the previous phase has been run and its output inspected by hand.** Each phase ends with a human verification step. On this project the verification matters more than usual — a classifier that quietly mislabels records produces confident, wrong findings, and nothing downstream will catch it.

---

## Phase 1 — Project setup and read-only inputs

**Goal:** get the three corpora in place without any risk of mutating them.

**Tasks**
1. Create the directory structure from the architecture.
2. Copy the three source files into `data/input/`. Set them read-only.
3. Write `requirements.txt`: LLM client, `pyyaml`, `python-docx`, `openpyxl`. Install.
4. Write `config/taxonomy.yaml` with the five dimensions and their exact allowed values.
5. Write `config/ownership.yaml` with the blocker-to-owner mapping.
6. Write `config/filters.yaml` with the term list and pattern rules.

**Verify**
- All three files open and their record counts match expectation: 63,014 Play Store, 7 Reddit threads, 39 survey rows.
- Taxonomy loads and every dimension has an `unclear` or `none` option.

---

## Phase 2 — Ingestion

**Goal:** three sources, one schema, nothing lost.

**Tasks**
1. Write the Play Store loader — straight JSONL read into the common schema, `rating` and `matched_terms` into `meta`.
2. Write the Reddit loader — parse the DOCX, split on thread headings, produce one record per post and comment, `thread_id` in `meta` so threads can be reassembled.
3. Write the survey loader — one record per response; `text` is the concatenation of chosen options and free text; the full structured answers preserved in `meta`.
4. Write `stage_01_ingested.jsonl` and the first `funnel.json` entries.

**Verify before proceeding**
- Total ingested equals 63,014 + Reddit records + 39.
- Print one record from each source. Schema identical, `meta` correctly populated.
- Reddit: pick a thread and confirm its comments share a `thread_id` and are all present.
- Survey: confirm `meta` retains the elasticity question verbatim. Stage 5 depends entirely on this field surviving intact.

---

## Phase 3 — Filtering

**Goal:** 63,014 down to a classifiable set, with every drop counted.

**Tasks**
1. Implement the four gates in sequence, counting entry and exit at each.
2. Pass Reddit and survey records through untouched.
3. Write both the broad set (gates 1–3) and the narrow set (all four).
4. Extend `funnel.json`.

**Verify before proceeding**
- Counts balance at every gate. Entering equals surviving plus dropped, with no exceptions.
- Broad set lands near 1,590; narrow set near 196–325. A large deviation means a gate is wrong.
- **Read 20 records the narrow gate dropped.** If genuinely relevant material is being discarded, the pattern list needs widening before anything downstream is built on it.
- Read 20 records it kept. If most are irrelevant, the gate is too loose.

This double-sided check is the most valuable half hour in the project. Every finding rests on this filter being roughly right.

---

## Phase 4 — Classification

**Goal:** valid enum tags on every record, with enforcement that actually holds.

**Tasks**
1. Write the batch prompt embedding the full taxonomy, instructing that only listed values are permitted and that `unclear` is expected rather than a failure.
2. Implement batching at 10–20 records.
3. Implement **code-level enum validation** — invalid tags are rejected, never mapped to a nearest neighbour.
4. Implement retry-once, then quarantine.
5. Implement content-hash caching keyed on text plus taxonomy version.
6. Write `stage_03_classified.jsonl`.

**Verify before proceeding**
- Run on 30 records first. **Read all 30 classifications by hand against the source text.** Disagreement on more than a few means the prompt or the taxonomy needs work — fix it before spending tokens on the full set.
- Deliberately inject a record designed to elicit an invalid tag. Confirm it is rejected and quarantined, not silently coerced.
- Re-run the same 30. Confirm zero API calls — the cache is working.
- Check the `unclear` rate. Near zero is suspicious: it usually means the model is guessing rather than admitting uncertainty.

---

## Phase 5 — Counting

**Goal:** every number computed in Python, with denominators.

**Tasks**
1. Tag frequencies per dimension, broken down by source.
2. Co-occurrence pairs, particularly `blocker_type` × `blocker_category` and `blocker_type` × `external_action`.
3. Structural versus psychological totals.
4. Write `counts.json` with every count carrying its denominator.

**Verify before proceeding**
- Hand-count one tag across a 50-record sample and compare against the computed figure.
- Confirm every count has a denominator attached.
- Confirm source breakdown is present everywhere — a finding driven by one corpus must be visible as such.

---

## Phase 6 — Scoring

**Goal:** ranked opportunities with three dimensions kept separate.

**Tasks**
1. Compute prevalence per blocker with source breakdown.
2. Compute elasticity **from survey `meta` only** — of respondents citing this blocker, how many would buy straight away or within a few weeks. Report as a fraction with denominator.
3. Set elasticity to `null` for blockers the survey does not cover.
4. Attach ownership from config.
5. Rank by prevalence, then elasticity. Write `opportunities.json`.

**Verify before proceeding**
- Hand-check one elasticity fraction against the raw survey rows.
- Confirm blockers absent from the survey show `null`, not zero. This is the single easiest place to accidentally fabricate a finding.
- Confirm the ranking reproduces the known divergence: quality doubt high prevalence and low elasticity, price blockers high on both. If it does not, the elasticity calculation is wrong.

---

## Phase 7 — Dashboard

**Goal:** deployed, interrogable by someone with no context.

**Tasks**
1. Build the six panels: funnel, ranked opportunities, evidence drill-down, source comparison, co-occurrence, method note.
2. Read the generated JSON directly — no server, no database.
3. Deploy to a free host. Confirm the public URL works from a different device.

**Verify**
- Every opportunity expands to real evidence with its source labelled.
- The funnel is visible without scrolling or hunting.
- The method note states the limitations plainly: corpus under-represents silent non-buyers, Reddit skews to complaints, Hindi coverage effectively absent, elasticity available only where the survey asked.
- Hand the link to someone uninvolved. If they cannot work out what the top opportunity is and why, the ranking panel needs work.

---

## Phase 8 — Findings write-up

**Goal:** convert engine output into the input for interview design.

**Tasks**
1. Record the funnel numbers.
2. Record the top three to four opportunities with prevalence, elasticity, ownership.
3. Note where sources disagree.
4. Note what the engine could not determine — this becomes the interview agenda.

**Verify**
- Every claim traces to a count in `counts.json` or `opportunities.json`.
- No percentages from the survey without n stated alongside.
- No causal language. The engine ranks hypotheses; interviews establish cause.

---

## Out of scope for every phase

No sentiment analysis. No embeddings or emergent clustering. No LLM-generated statistics. No composite score collapsing the three dimensions. No modification of the input corpora.
