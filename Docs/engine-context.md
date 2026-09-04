# Context

Background for anyone — human or agent — working on the discovery engine. Read `engine-problem-statement.md` first.

## The research question

A fashion e-commerce platform wants more users to buy at least one wishlisted item within 30 days of saving it. The underlying user problem is **not given**. Discovering it is the entire point of this engine.

Solutions cannot involve monetary incentives. That constraint matters here because it rules out the most obvious answer to the most-cited blocker. If people say they are waiting for a price drop, "give them a discount" is off the table — which forces the engine to surface what else is actually blocking them.

## The metric this serves

North star: of users who wishlisted an item, the share who bought at least one within 30 days.

Decomposed into four sequential rates:
1. **Re-engagement** — do they come back to the item at all
2. **Resolution** — does their doubt get resolved
3. **Wishlist-to-cart** — do they cart it
4. **Cart-to-purchase** — do they complete

Every opportunity the engine surfaces should be attributable to at least one of these four stages. A blocker that cannot be located in the funnel is probably not actionable.

## What we already know going in

This is not a blank slate. The collected data has been inspected, and these observations shape the engine's design.

**From the survey (n=39, 35 after screening)**

Stated blockers cluster into roughly equal groups — price waiting, quality doubt, budget, decision paralysis — with none dominating.

The most requested fix is reviews and photos from real buyers, slightly ahead of price-drop alerts.

Crucially, **prevalence and elasticity diverge**. Quality doubt is among the most-cited blockers but among the least likely to convert if resolved. Price blockers are both common and highly elastic. Fit uncertainty, in this sample, showed no conversion at all when respondents were asked what they would do if it were resolved.

Two time-decay signals: the most common reason for going off an item was finding something better, followed by the moment passing. Both suggest that speed of re-engagement matters independently of which blocker is being resolved.

**From Reddit**

Myntra caps wishlists at 1,000 items. Users hit the cap and delete items to make room — those deleted items can never convert, which silently shrinks the denominator of the north star metric.

A recurring pattern: users wait for a sale, return when it starts, and find the item repriced, out of stock, or newly undeliverable to their pincode. Several report buying elsewhere at a higher price out of frustration. That is demand redirected, not demand lost.

**From Play Store**

Structural blockers appear repeatedly and plainly: pincode serviceability failures, items going out of stock, size unavailability, slow restocking. One review states directly that prices increase on wishlisted items. Another reports the wishlist being cleared without warning.

Psychological deliberation is almost absent — as expected. People do not write app reviews about hesitating.

## The central open question

Is non-conversion mainly **structural** (the platform blocked the purchase) or **psychological** (the user held back)?

Current read: both, and they compound. Users wait for a price drop, and the waiting itself exposes them to stock, serviceability, and repricing failures. The two categories are not independent.

The engine should be able to test this rather than assume it — which is why `blocker_category` is a classification dimension and why co-occurrence counting matters.

## Source asymmetries the engine must respect

Each corpus is strong where the others are weak, and the engine must not average them into a single undifferentiated pile.

**Play Store** — 63,014 records, but median length 5 words and roughly 0.3–0.5% relevant. Ratings are bimodal. The Hindi locale returned 124 records out of 63,014, so any claim about non-English-speaking users is unsupported. Six months of coverage, not eighteen.

**Reddit** — 7 threads, five from a complaint-focused subreddit. Excellent for surfacing blocker *types* nobody would have invented. Useless for frequency. A count of "how many Reddit threads mentioned X" is not a meaningful statistic and should not be presented as one.

**Survey** — the only source that can speak to elasticity, because it is the only one that asked what people would do if the blocker were removed. Also the only source where respondents were reporting on a real item currently sitting in their wishlist. Small, but directly on-question.

Because of this, **findings must always carry their source**. "Serviceability is a blocker" is supported by Play Store and Reddit. "Resolving serviceability would convert X% of blocked users" can only come from the survey, and only if the survey covered it.

## The honesty requirement

The corpus systematically under-represents the exact behaviour being studied. Silent non-buyers do not write app reviews and rarely post on Reddit. This is a known, accepted limitation, not a bug to engineer around.

The engine's role is to **generate and rank hypotheses**. User interviews establish cause. Any output that reads as though the engine settled a causal question is overclaiming.

Concretely, this means:
- Report counts, never invented percentages
- Show the filter funnel rather than only the surviving records
- Label every finding with which source produced it
- Where sources disagree, show the disagreement instead of resolving it silently

## How this fits the wider project

```
scrapers  →  DISCOVERY ENGINE  →  user interviews  →  problem definition  →  MVP
 (done)          (this)             (next)
```

The engine's output feeds interview design directly. Its ranked opportunities become the hypotheses the interviews test, and the interviews are what determine which problem is actually pursued.

That downstream use is why ranking matters more than summarising. A list of themes gives interviewers nothing to prioritise. A ranked list with prevalence, elasticity, and ownership tells them exactly which two or three things to probe hardest.
