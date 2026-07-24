# Spec: AI Code Review Platform

**Status:** Living document — updated as scope evolves across stages
**Last updated:** 2026-07-23
**Owner:** [your name]

---

## 1. Problem Statement

Manual code review is slow, inconsistent, and dependent on reviewer availability and
attention. Common defect classes (missing input validation, insecure data handling,
off-by-one errors, unhandled exceptions) get missed under time pressure even by
experienced reviewers. This project automates a first-pass review layer that flags
likely issues with structured, machine-readable output, so a human reviewer's time is
spent judging flagged issues rather than searching for them from scratch.

This is a first-pass assistant, not a replacement for human review. Every finding is
a suggestion; nothing is auto-applied without explicit human approval (see Non-Goals
and the approval workflow in later stages).

---

## 2. Non-Goals (this iteration)

Explicitly out of scope right now — listed so scope creep is a conscious decision,
not an accident:

- **No automatic fix application.** The system proposes findings; it does not modify
  code. Auto-fix-and-apply is a future capability (Stage 6+), gated behind an
  explicit approval state machine.
- **No language-specific static analysis (AST parsing, linter integration per
  language).** The service supports a fixed whitelist of file extensions
  (`.py`, `.js`, `.ts`, `.java`, `.cpp` — see `EXTENSION_LANGUAGE_MAP` in
  `file_handler.py`), sent as raw text to the LLM rather than parsed into a
  syntax tree. This is a whitelist for input validation, not full
  language-agnosticism — an unlisted extension is rejected with a 400 rather
  than accepted and best-effort reviewed. Revisit only if eval scores (Stage 2)
  show a specific listed language needs AST-level precision the LLM misses.
- **No IDE plugin / real-time-as-you-type review.** This is a batch/webhook-triggered
  review, not an inline editor assistant.
- **No fine-tuned model.** We rely on prompting an existing hosted model (via
  OpenRouter) rather than training/fine-tuning our own. Revisit only if prompting
  provably plateaus below target accuracy.
- **No authentication/multi-tenant access control yet.** Single-user/single-repo
  assumption for now; explicitly flagged as a gap before any real deployment.

---

## 3. Success Metrics

Success is defined numerically, against a labeled benchmark (see Stage 2 below),
not by "the review looks reasonable":

- **Recall ≥ 80%** on a labeled set of 30-50 code snippets with planted defects
  (the system must actually flag most planted issues).
- **Precision ≥ 70%** on the same set (it shouldn't drown real issues in noise).
- **p95 review latency < 10s** per file/diff at typical PR size. **Status as of
  first real measurement (Stage 2, case 001):** 29.19s for a ~4-line file —
  roughly 3x over target. Likely attributable to the free-tier model
  (`poolside/laguna-xs-2.1:free`, see ADR 0001) rather than the service code
  itself. This is a known, measured gap, not yet resolved — flagged here
  rather than left as an unverified claim. Needs more samples before drawing
  a firm conclusion (one data point is not a p95).
- Metrics are computed by an automated eval script and stored per run in
  `eval_results` (Stage 3), so accuracy is trackable over time, not a one-off claim.

---

## 4. Interface Contract

### Current (manual upload)
```
POST /review
Content-Type: multipart/form-data
Body: file (source code file, extension in .py/.js/.ts/.java/.cpp)

Response 200 — matches app/schemas/review.py:ReviewResult:
{
  "summary": "string — one-paragraph overview of the code",
  "strengths": ["string", ...],
  "issues": ["string", ...],
  "suggestions": ["string", ...],
  "verdict": "string"
}

Note: this is a holistic review, not a per-line finding list. There is no
line number, severity, or category field per issue — "issues" is a flat list
of free-text strings. This matters directly for Stage 2 (the eval set): a
benchmark that checks "was the planted bug on line 42 flagged" cannot be
built against this schema as-is. Either (a) the eval instead checks whether
a planted bug's description is semantically present anywhere in the "issues"
list, or (b) the schema evolves in Stage 3 to add per-issue line numbers.
This decision is deferred to Stage 2 and should become its own ADR.

Response 422: validation error (bad file type, empty file, oversized file
  over MAX_FILE_SIZE = 1MB — enforced in file_handler.py)

Note: `llm_service.py` already logs per-request latency and token usage
(prompt/completion/total) on every call. This is real, working observability
— it just isn't persisted anywhere yet (Stage 3 moves it from log lines into
a queryable `review_runs` table).
Response 500: generic failure (current) — LLM/provider errors are not yet
  distinguished from other internal errors. Planned: split into 502 (upstream
  provider failure) vs 500 (genuine internal bug) once llm_service.py catches
  provider-specific exceptions instead of a bare `except Exception`.
```

### Planned (Stage 5 — webhook-triggered)
```
POST /webhooks/github
Headers: X-Hub-Signature-256 (HMAC verification, required)
Body: GitHub pull_request event payload

Behavior: fetch PR diff via GitHub API, run review per changed file,
persist results, post summary as a PR comment.
```

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM hallucinates a finding that isn't real (false positive erodes trust) | Labeled eval set tracks precision explicitly; findings include line numbers so they're independently verifiable |
| Upstream provider (OpenRouter) outage or rate limit | Currently: caught via a generic `except Exception` in `llm_service.py`, logged, and surfaced as a failure — no retry-with-backoff yet. **Gap:** a transient failure currently fails the whole request immediately rather than retrying once before giving up. Flagged as a Stage 3 improvement, not yet implemented. |
| Malformed/invalid JSON returned by the model | **No retry logic exists yet.** A bad response is currently caught by the same generic exception handler as any other failure — the caller gets a 500-style error with no distinction between "the model returned garbage" and "the network died." This is a known gap: Stage 3 should add a specific `JSONDecodeError`/`ValidationError` catch that retries once with a corrective prompt before failing. |
| Large diffs exceed context window | Chunk by file, cap per-file size, explicitly reject/flag oversized files rather than silently truncating |
| Duplicate webhook delivery (GitHub retries on timeout) | Idempotency check on `review_runs` keyed by PR + commit SHA (Stage 5) |
| Prompt injection via malicious code comments instructing the model to ignore instructions | Documented as a known risk; system prompt explicitly instructs the model to treat file content as data, not instructions; not yet adversarially tested — flagged as future hardening work |

---

## 6. Stages (cross-reference)

1. This spec + ADRs
2. Labeled eval set + scoring script
3. PostgreSQL persistence (`review_runs`, `findings`, `eval_results`)
4. React demo UI (upload form + results table)
5. GitHub webhook + PR-diff review
6. Approval state machine (`proposed → approved → applied`)