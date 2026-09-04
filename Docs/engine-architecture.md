# Architecture

Technical design for the discovery engine. Derived from `engine-problem-statement.md` and `engine-context.md`. Read both first.

## Design principles

1. **Staged and auditable.** Every stage writes its output to disk with a count. Nothing is dropped silently.
2. **Counts in code, never from a model.** The LLM assigns labels. Python does all arithmetic.
3. **Source travels with the record.** From ingestion to dashboard, every record knows where it came from.
4. **Idempotent and cheap to re-run.** Classification results are cached by content hash so re-running costs nothing.
5. **Inputs are read-only.** The engine never modifies the collected corpora.

## Pipeline

```
raw corpora
    │
    ├─ 01_ingest      3 sources → 1 schema          → stage_01_ingested.jsonl
    ├─ 02_filter      63k → ~1.6k → ~300            → stage_02_filtered.jsonl
    ├─ 03_classify    LLM + enum validation         → stage_03_classified.jsonl
    ├─ 04_count       frequencies + co-occurrence   → counts.json
    ├─ 05_score       prevalence/elasticity/owner   → opportunities.json
    └─ 06_dashboard   deployed UI
```

Each stage reads the previous stage's file and writes its own. Any stage can be re-run alone. A `funnel.json` accumulates the counts at every step.

## Stage 1 — Ingest

Three loaders, one output schema.

```json
{
  "record_id": "sha256 of source + original id",
  "source": "play_store | reddit | survey",
  "text": "the content to classify",
  "created_at": "ISO 8601 or null",
  "meta": { }
}
```

`meta` holds source-specific fields that must not be lost but do not belong in a shared schema — `rating` and `matched_terms` for Play Store, `thread_id` and `subreddit` for Reddit, the full structured answers for survey rows.

**Play Store** — read JSONL directly.

**Reddit** — parse the DOCX into thread structure. Each post and comment becomes a record; `meta.thread_id` groups them. Thread context is preserved because a two-word comment can be meaningful given its parent.

**Survey** — each response becomes one record. `text` is the concatenation of its free-text and selected options so the classifier sees the same content a human would. The structured answers stay in `meta` because they are needed intact for elasticity scoring.

## Stage 2 — Filter

Applies only to Play Store. Reddit and survey records pass straight through — they are small and already dense.

**Sequential gates, each counted:**

1. Text present and non-empty
2. Word count ≥ 12
3. Contains at least one wishlist-relevant term
4. Matches a deliberation or structural-blocker pattern

The output of gates 1–3 (~1,600 records) is kept as the **broad set**. The output of all four gates (~300 records) is the **narrow set**.

Both are retained. The narrow set is what gets classified; the broad set exists so a claim like "this pattern appears in N of 1,590 filtered reviews" can be checked without re-running collection.

`funnel.json` records the count entering and leaving every gate. These numbers go on a slide, so they must balance exactly.

## Stage 3 — Classify

**Batching.** Records are sent in batches of 10–20. One record per call would be slow and wasteful; larger batches degrade labelling quality as the model loses track.

**Prompt structure.** The taxonomy is stated in full, with the explicit instruction that only listed values may be used and that `unclear` is a valid, expected answer. Each record is classified independently within the batch — no cross-record reasoning.

**Enum validation in code.** The returned tags are checked against the allowed sets. An invalid tag is not silently corrected or mapped to a neighbour. The record is flagged `validation_failed` and retried once; a second failure sends it to a quarantine file for manual review.

This is the difference between claiming enum enforcement and actually having it. A prompt that asks for fixed values still returns invented ones; only code-level rejection makes the guarantee real.

**Caching.** Results are keyed by a hash of the record text plus the taxonomy version. Re-running the pipeline reclassifies nothing unless the taxonomy changed. Changing the taxonomy invalidates the cache wholesale, which is correct.

**Output** adds to each record:

```json
{
  "wishlist_motive": "...",
  "blocker_type": "...",
  "blocker_category": "...",
  "external_action": "...",
  "journey_stage": "...",
  "classifier_version": "v1",
  "validation_status": "ok | failed | quarantined"
}
```

## Stage 4 — Count

Pure Python. No model.

- Frequency of each tag, **broken down by source**
- Co-occurrence pairs across dimensions, particularly `blocker_type` × `blocker_category` and `blocker_type` × `external_action`
- Structural versus psychological totals
- Distribution of `journey_stage`

Every count is emitted with its denominator. A bare number is not reportable; "34 of 312 classified records" is.

Source breakdown is mandatory, not optional. A finding driven entirely by one corpus must be visibly so.

## Stage 5 — Score

Three dimensions, held separate. **Never collapsed into one number** — a single score hides the reasoning, and the reasoning is the deliverable.

**Prevalence** — count of records carrying this blocker, with source breakdown and denominator.

**Elasticity** — from survey `meta` only. For each blocker, of respondents citing it, how many said they would buy straight away or within a few weeks. Reported as a fraction with its denominator, for example `5/8`.

For blockers the survey did not cover, elasticity is `null`. **Not zero, not estimated.** A null that is honestly displayed is more useful than a fabricated number.

**PM ownership** — a static mapping in config, not inferred:

```yaml
price_wait:        product      # alerts, price history
quality_doubt:     product      # reviews, photos, Q&A
fit_doubt:         product      # size guidance, past-order sizing
decision_paralysis: product     # comparison tools
forgot_wishlist:   product      # reminders, surfacing
no_reviews:        product      # review seeding, alternate trust signals
size_unavailable:  shared       # product can notify; inventory must stock
out_of_stock:      shared
serviceability:    ops
cod_unavailable:   ops
budget_constraint: neither      # outside platform control
```

`shared` matters. Product cannot make an item in stock, but it can notify the moment it returns — which is a real, shippable lever against a structural blocker.

**Ranking** sorts by prevalence, then elasticity, with ownership shown alongside. Sorting is transparent and re-derivable; nothing is hand-adjusted.

## Stage 6 — Dashboard

Single page, static build, deployed free. Reads the generated JSON — no server, no database.

**Panels**

1. **Funnel** — 63,014 → 1,590 → ~300, stage by stage. Shown prominently, not in a footnote. It is the honest framing of how thin the signal is.
2. **Ranked opportunities** — each blocker with prevalence, elasticity, ownership, expandable to evidence.
3. **Evidence drill-down** — actual record text, source-labelled, for any selected opportunity.
4. **Source comparison** — what each corpus contributed per blocker, and where they disagree.
5. **Co-occurrence** — which blockers appear together.
6. **Method note** — taxonomy, limitations, what the engine can and cannot claim.

Panel 6 is not decoration. A reviewer who can see the limitations stated plainly trusts the rest more, not less.

## Directory layout

```
discovery-engine/
  run.py                      orchestrates all stages
  config/
    taxonomy.yaml
    ownership.yaml
    filters.yaml
  src/
    ingest/{play_store,reddit,survey}.py
    filter.py
    classify.py
    count.py
    score.py
  data/
    input/                    read-only copies of corpora
    stages/                   stage_01..03 jsonl
    output/                   counts.json, opportunities.json, funnel.json
    cache/                    classification cache
    quarantine/               records that failed validation twice
  dashboard/
```

## Dependencies

An LLM client, `pyyaml`, `python-docx` for the Reddit file, `openpyxl` for the survey. Standard library for everything else.

No pandas — the data is small enough that plain dicts are clearer and make the counting logic auditable by reading it.

## What is deliberately absent

- **No sentiment analysis.** The brief explicitly rules it out as insufficient.
- **No embeddings or clustering.** A fixed taxonomy is more defensible than emergent clusters, which drift between runs and cannot be validated.
- **No LLM-generated summaries presented as findings.** Narrative text may be generated for the dashboard, but only from computed counts, and always with those counts displayed alongside.
- **No database.** JSON files on disk, inspectable by hand.
- **No single composite score.** Three dimensions stay visible.

## Failure posture

A record that fails classification twice is quarantined, not dropped. Quarantine count appears in the funnel.

An LLM API failure retries with backoff, then halts the stage rather than continuing — a partially classified set that looks complete is worse than an obvious stop.

Missing elasticity is displayed as unknown. It is never imputed, defaulted, or filled from a neighbouring blocker.
