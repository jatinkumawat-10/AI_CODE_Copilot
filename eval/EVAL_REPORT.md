# Eval Report — Run 1

**Date:** 2026-07-24
**Model:** `poolside/laguna-xs-2.1:free` (see ADR 0001)
**Methodology:** 5 trials per case, keyword-first cascade scoring (see
`SCORING_STRATEGY.md`), errors excluded from denominator (0 errors this run).

## Results

| Case | Category | Hit Rate | Keyword Hits | LLM-Judge Hits |
|---|---|---|---|---|
| 001_sql_injection | security | 5/5 (100%) | 5 | 0 |
| 002_missing_null_check | correctness | 5/5 (100%) | 4 | 1 |
| 003_race_condition | correctness (concurrency) | 1/5 (20%) | 1 | 0 |

**Overall recall: 73.3% (11/15 valid trials)**

## Analysis

SQL injection and missing null checks are caught reliably and consistently.
Race conditions are not: 4 of 5 trials fell through to the LLM-judge
fallback (meaning the keyword check found none of `["race condition",
"thread safety", "concurrent", "lock", "check-then-act", "TOCTOU"]` in the
model's output), and the judge itself — asked directly whether the issues
list described a race condition — answered **no in all 4 of those trials**.
This is not an ambiguous or borderline signal; it's a consistent failure to
recognize a bug that requires reasoning about concurrent execution rather
than pattern-matching a named, well-documented vulnerability class.

**Working hypothesis:** the model performs well on bug classes with strong,
recognizable training signal (SQL injection is one of the most commonly
labeled vulnerabilities in public code/security datasets) and performs
poorly on bugs that require reasoning about *behavior over time* (what
happens if two calls interleave) rather than *pattern recognition* (this
specific string-concatenation shape is dangerous).

## Run 2 (same day, later)

Extended to 5 cases (added 004_toctou_file_check, 005_shared_counter_race).

| Case | Hit Rate | Notes |
|---|---|---|
| 001_sql_injection | 5/5 (100%) | consistent with Run 1 |
| 002_missing_null_check | 5/5 (100%) | consistent with Run 1 |
| 003_race_condition | **4/5 (80%)** | **Run 1 was 1/5 (20%) — same unchanged case, opposite result** |
| 004_toctou_file_check | 2/4 (50%), 1 errored | incomplete — hit daily quota mid-case |
| 005_shared_counter_race | 1/1 (100%), 4 errored | incomplete — only 1 of 5 trials completed |

**Overall recall: 85.0% (17/20 valid trials, 5 errored/excluded)**

### Critical operational finding: OpenRouter's free tier has a hard daily cap

The 429 errors mid-run were not transient throttling — the response body reads
`"Rate limit exceeded: free-models-per-day"` with `X-RateLimit-Limit: 50,
X-RateLimit-Remaining: 0`. This is a **50-requests-per-day hard ceiling** on
`poolside/laguna-xs-2.1:free`, not a per-minute limit our existing 2-second
inter-call delay can work around. Once exhausted, every subsequent call
fails immediately regardless of retry/backoff logic, until the daily reset.

This is a materially stronger version of the tradeoff ADR 0001 already
flagged in the abstract ("free-tier model, cost/access reasons") — now we
have the exact number, and it directly limits how much eval iteration is
even possible per day on this model.

### Honest methodological limitation: case 003's result is not yet trustworthy

A 1/5 → 4/5 swing on an unchanged test case across two independent runs
means **5 trials is not enough to produce a stable estimate for this bug
class**, and we cannot currently rule out that rate-limit-induced retry
pressure (responses generated under a degraded/retrying client state)
affected output quality differently between runs. This is a real,
documented uncertainty — not resolved by this report, and not resolvable
today given the exhausted quota.

### Conclusion and decision

Given (a) the hard 50/day cap makes further same-day iteration impossible,
and (b) case 003's instability means more free-tier trials wouldn't
currently produce a trustworthy answer anyway, this is the natural point to
invoke ADR 0001's revisit trigger for real: **compare against a paid model**
is now motivated by two independent reasons, not one. This is logged as a
planned follow-up, not executed in this session — eval work is paused here
by design, not abandoned, and the project moves on to Stage 3 (persistence).