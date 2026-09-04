# Edge Cases

Failure modes and correct behaviour. Consult alongside `engine-implementation-plan.md` while building each phase.

The dangerous failures here are not crashes. They are the ones that produce confident, plausible, wrong findings — because nothing downstream will catch them.

---

## Classification

**The model invents a tag**
Rejected in code, not mapped to a nearest neighbour. Retry once, then quarantine. Mapping an invented tag to a real one is how a fabricated category silently enters the counts.

**The model refuses to say `unclear`**
Most likely failure in practice. Models pattern-match to a plausible label rather than admitting uncertainty. Watch the `unclear` rate — near zero on genuinely ambiguous text means the model is guessing, and every guess becomes a count.

**Batch contamination**
Records in a batch influence each other's labels. Symptom: long runs of identical tags within a batch. Guard: check whether tag distribution differs by position in batch. If it does, shrink the batch.

**The model returns the wrong number of results**
A batch of 15 comes back with 14 labels. Never assume positional alignment — match on an id echoed in the response. Misalignment silently attaches every label to the wrong record, and the output looks entirely normal.

**Malformed JSON from the model**
Common. Retry once, quarantine on second failure. Never regex-repair a partial response into valid JSON.

**Taxonomy changed but cache not invalidated**
Cache key must include taxonomy version. Otherwise a re-run after a taxonomy edit returns stale labels for old records and new labels for new ones, producing a silently mixed dataset.

**Same text classified differently across runs**
Expected with a non-zero temperature. Set temperature to zero. If it still varies, note it — reproducibility is part of the deliverable.

---

## Filtering

**The narrow gate drops relevant records**
The main risk in Phase 3. Pattern lists never catch every phrasing. Mitigation: read 20 dropped records by hand. Also keep the broad set, so nothing filtered is lost forever.

**The gate is too loose**
Opposite failure — irrelevant records dilute counts and make every blocker look equally common. Read 20 kept records.

**Keyword appears in an irrelevant sense**
"Fit" means physical fit and also "fits my budget" and "fit for purpose". "Sale" appears in every promotional complaint. Keyword matching cannot disambiguate; this is what the classifier is for. Do not attempt to fix it in the filter.

**Counts stop balancing**
Entering must equal surviving plus dropped, at every gate. If not, records are vanishing. Stop and find it — a leak here invalidates every number that follows.

**Filter tuned until the answer looks good**
The most insidious failure in the project. Adjusting the pattern list after seeing which findings emerge is fitting the filter to a preferred conclusion. Fix the filter in Phase 3, verify it once, then leave it alone. If it must change later, re-run everything downstream and say so.

---

## Elasticity

**Blockers with no survey coverage**
Must be `null`, never zero. Zero reads as "resolving this converts nobody," which is a strong claim from no data. A visible null is honest.

**Tiny denominators**
Some blockers have three or four survey respondents. `0/3` is not evidence that resolving fit uncertainty converts nobody. Always display the denominator, and flag anything under five as too small to rank on.

**Survey blocker labels do not match classifier enums**
The survey uses its own phrasing. The mapping between survey options and `blocker_type` enums must be explicit in config, not inferred at runtime. An implicit mismatch silently zeroes out elasticity for a whole category.

**Screening failures counted**
Four respondents said they had no unbought wishlist item but answered the follow-ups anyway. Decide once: exclude them and report n=35, or include and report n=39. Either is defensible; switching between them depending on which produces a better number is not. Record the decision in the method note.

**Elasticity treated as ground truth**
It is self-reported intent about a hypothetical. People overstate what they would do. Directionally useful for ranking, not a conversion forecast. Never present it as one.

---

## Source handling

**Sources averaged together**
The three corpora are not interchangeable. A blocker appearing in 200 Play Store records and 1 survey response is not "201 mentions." Every count carries its source breakdown.

**Reddit counted as frequency data**
Seven threads from a complaint subreddit. "Mentioned in 5 of 7 threads" is not a statistic. Reddit is for surfacing blocker types, not measuring their prevalence.

**Play Store volume swamps everything**
63,014 records versus 39 survey responses. Even after filtering, Play Store dominates raw counts — which will make structural blockers look more prevalent than psychological ones purely because of where the data came from. This is a sampling artefact, and the dashboard must make it visible rather than let it read as a finding.

**Hindi coverage claimed**
124 records out of 63,014. Any statement about non-English-speaking users is unsupported. Say so in the method note.

**Date coverage overstated**
The Play Store corpus runs January to June 2026 — six months, not the eighteen originally scoped. Seasonal patterns outside that window are invisible.

---

## Counting

**Counts without denominators**
"34 records mentioned serviceability" is meaningless without knowing whether that is out of 300 or 63,000. Every count carries its base.

**Co-occurrence misread as causation**
`price_wait` co-occurring with `out_of_stock` shows they appear together. It does not establish that waiting causes the stock-out. Present as co-occurrence, describe as a pattern, and let the interviews test the mechanism.

**Double counting across dimensions**
A record can carry a motive and a blocker and a journey stage. Summing across dimensions produces nonsense totals. Count within a dimension only.

---

## Dashboard

**Limitations buried**
The method note is a panel, not a footnote. A reviewer who sees limitations stated plainly trusts the rest more.

**Funnel hidden**
63,014 → ~300 is the honest framing of signal density. Showing only the surviving records implies a far stronger evidence base than exists.

**Generated narrative drifts from the counts**
If the dashboard renders LLM-written summary text, the underlying numbers must sit beside it. A summary that is not directly checkable against a displayed count should not be shown at all.

**Evidence links break**
Every opportunity must expand to real records. An opportunity with no viewable evidence is an assertion.

---

## Overall interpretation

**Engine output presented as causal**
It ranks hypotheses. Interviews establish cause. Language matters: "appears most frequently" and "was most cited" are supportable; "drives non-conversion" is not.

**Absence read as evidence of absence**
Psychological hesitation barely appears in Play Store data. That is a property of app reviews, not evidence that hesitation is rare. Stating this explicitly is the difference between a careful reading and a wrong one.

**The prevalence trap**
Ranking by frequency alone points at the wrong problem — the survey already shows quality doubt is highly cited and poorly elastic. Prevalence and elasticity stay separate and both stay visible. This is the entire reason the scoring design exists.
