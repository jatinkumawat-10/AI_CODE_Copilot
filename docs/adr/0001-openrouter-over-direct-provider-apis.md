# ADR 0001: Use OpenRouter Instead of a Direct Provider API

**Status:** Accepted
**Date:** 2026-07-23

## Context

The review service needs to call an LLM to analyze code and return a
structured review. `config.py` currently hardcodes
`BASE_URL = "https://openrouter.ai/api/v1"` and
`MODEL_NAME = "poolside/laguna-xs-2.1:free"`, and `openrouter.py` wraps the
OpenAI SDK client pointed at that base URL. The two realistic alternatives
were integrating directly against a single provider's native SDK, or
integrating against OpenRouter as a provider-agnostic proxy.

## Decision

Use OpenRouter as the LLM client layer, currently configured against a
free-tier model (`poolside/laguna-xs-2.1:free`) for cost and access reasons
during early development.

## Alternatives Considered

- **Direct Anthropic or OpenAI native SDK.** Rejected as the sole integration
  because it locks the service to one provider — an outage, rate limit, or
  pricing change on that provider takes the whole service down with no
  fallback path. OpenRouter's proxy layer means swapping models or providers
  is a one-line config change in `config.py`, not a code change.
- **Building a custom multi-provider abstraction in-house.** Rejected as
  strictly more work than OpenRouter for the same benefit during an
  early-stage project — OpenRouter already implements that abstraction and is
  maintained externally. Revisit only if OpenRouter's own reliability or fee
  structure becomes the bottleneck.
- **Using a paid model instead of the free tier from the start.** Rejected for
  now on cost/access grounds while the project is in early development and
  request volume is low. This is a conscious, revisitable tradeoff, not an
  oversight — see Consequences below for what it costs us.

## Consequences

- **Positive:** provider-agnostic — swapping models or providers is a config
  change in `config.py`, not a code change. Easy to A/B different models
  against the eval set (Stage 2) once it exists, without touching
  `review_service.py` or `llm_service.py`.
- **Negative (OpenRouter layer):** an added layer of indirection and latency
  versus calling a provider directly; OpenRouter itself becomes a dependency
  and a single point of failure in its own right. The current bare
  `except Exception` in `llm_service.py` means an OpenRouter-layer failure is
  indistinguishable from any other failure — flagged already in spec.md's
  risk table as a Stage 3 gap.
- **Negative (free-tier model) — confirmed concretely in Stage 2:** the
  free tier is capped at **50 requests/day** (`X-RateLimit-Limit: 50`),
  confirmed by a real `429` during eval Run 2. This isn't just weaker
  instruction-following (the original concern) — it's a hard operational
  ceiling on how much testing/evaluation is even possible per day, which
  directly limited Stage 2's ability to gather enough trials to resolve an
  observed instability in one bug category (see `eval/EVAL_REPORT.md`, Run 2).
- **Revisit trigger:** if Stage 2's eval scores come in low, the first
  diagnostic step should be re-running the same eval set against a paid model
  to isolate whether the gap is prompt quality or model capability, before
  assuming the prompt needs rework.