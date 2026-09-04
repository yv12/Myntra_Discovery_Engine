# Discovery Engine — Project Spec

## What this project is

An AI-powered discovery engine that takes three collected corpora, filters and normalises them into a single evidence set, classifies each record against a fixed taxonomy, and produces a **ranked, comparable list of opportunity areas** with the underlying evidence attached to each.

It is deployed and publicly testable.

## What it must not be

The brief is explicit that the workflow must go beyond summarising reviews or performing sentiment analysis. A theme summariser fails this bar.

The output is not "here are five themes we found." It is "here are the opportunity areas, ranked by how much they could move wishlist-to-purchase conversion, each with its evidence, its prevalence, and its estimated elasticity."

## The inputs

| Source | Volume | What it is good for | What it cannot tell us |
|---|---|---|---|
| Play Store JSONL | 63,014 records | Structural blockers, breadth of user base | Pre-purchase deliberation. Median review is 5 words. |
| Reddit threads | 7 threads | Deliberation, sale-window failure patterns, the wishlist cap | Base rates. Sourced largely from a complaint subreddit. |
| Survey responses | 39 responses (35 after screening) | Direct self-report on real stalled items. **The only source with elasticity data.** | Anything at scale. |

These three have genuinely different strengths. The engine's job is to combine them without pretending they are interchangeable.

## The filtering problem

63,014 Play Store records cannot go into an LLM classifier. Most of them are five words long and about delivery.

Measured funnel from the collected corpus:

- 63,014 raw records
- ~1,590 records matching a wishlist-relevant term **and** at least 15 words
- ~196–325 records containing genuine deliberation or structural-blocker language

That final set is roughly **0.3–0.5% of the corpus**. This is expected for this source and is not a failure. The funnel counts themselves are a finding worth reporting — they quantify how rarely this behaviour surfaces in app reviews, which is the empirical justification for why primary research carries the causal weight.

Filtering must be **staged and auditable**. Every record dropped is counted, and the count at each stage is reported. No silent losses.

## The classification taxonomy

Closed enums. The LLM selects from fixed lists. Any tag outside the list is rejected in code, not merely discouraged in the prompt.

**wishlist_motive**
`price_watch` · `fit_uncertainty` · `budget_timing` · `occasion` · `aspirational` · `comparison_shortlist` · `gifting` · `unclear`

**blocker_type**
`price_wait` · `budget_constraint` · `quality_doubt` · `fit_doubt` · `decision_paralysis` · `size_unavailable` · `out_of_stock` · `serviceability` · `cod_unavailable` · `no_reviews` · `forgot_wishlist` · `none`

**blocker_category**
`structural` · `psychological` · `both` · `none`

**external_action**
`checked_other_platform` · `bought_elsewhere` · `asked_someone` · `none` · `unclear`

**journey_stage**
`pre_save` · `saved_waiting` · `returned_blocked` · `abandoned` · `purchased` · `unclear`

`unclear` and `none` are deliberate options. Without them the model is forced to guess, and forced guesses are how a classifier quietly manufactures findings.

## Counting happens in code

Tag frequencies and tag co-occurrence pairs are computed with plain Python. No LLM involved in producing any number.

Co-occurrence is where the real insight sits. `price_wait` appearing alongside `out_of_stock` is a materially different claim from either tag alone — it is the observed pattern of users waiting for a sale and finding the item gone when they return.

## Opportunity scoring

Each blocker type is scored on three dimensions:

**Prevalence** — how often it appears across the evidence set, reported per source so a Play-Store-heavy signal is visible as such.

**Elasticity** — of the people blocked by this, what share would actually buy if it were resolved. Derived from the survey's "if that were sorted out tomorrow" question. **This is available only from survey data.** Play Store and Reddit cannot supply it, and the engine must not fabricate it for blockers the survey does not cover.

**PM ownership** — can a product team ship something that moves this, or does it belong to inventory, payments, or logistics.

Ranked output, with each dimension shown separately rather than collapsed into a single opaque score. A reader must be able to see *why* something ranks where it does.

## Why prevalence alone is misleading

The survey already shows prevalence and elasticity diverging. Quality doubt is among the most-cited blockers and among the least elastic: eight respondents named it, two would act if it were resolved. Price blockers show the opposite pattern.

An engine that ranks by frequency alone would point at the wrong problem. That is the specific failure this scoring design exists to prevent.

## Output

A deployed, publicly accessible dashboard containing:

1. **Ranked opportunities** — blocker types ordered by the scoring above, each dimension visible
2. **Evidence drill-down** — click any opportunity to see the actual records behind it, with source labelled
3. **Funnel transparency** — the filtering counts at every stage, shown not buried
4. **Source comparison** — what each corpus contributed, and where they disagree
5. **Co-occurrence view** — which blockers appear together

## Constraints

- Free stack only.
- No LLM-generated statistics. Every number traceable to a count over records.
- Every claim links to its evidence.
- Source is preserved on every record end to end. A finding must always be attributable.
- Raw corpora are read-only. The engine never mutates its inputs.

## Definition of done

- All three sources ingest into one normalised schema.
- Filter funnel runs with counts reported at each stage, and the arithmetic balances.
- Every classified record carries valid enum tags and its source.
- Opportunity ranking is reproducible from the data with no manual adjustment.
- Dashboard is deployed at a public URL and someone else can interrogate it without explanation.
