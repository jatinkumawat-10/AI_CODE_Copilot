# ADR 0002: Structured JSON Schema for Review Output (Enforced via Pydantic)

**Status:** Accepted
**Date:** 2026-07-23

## Context

The LLM's raw output is unstructured text. The service needs a reliable, parseable
format so that findings can be stored, scored against the eval set, and rendered
in a UI without brittle string-parsing of free text.

## Decision

Constrain the LLM's response to a fixed JSON schema (line, severity, category,
message, suggestion per finding), validated on the way in with Pydantic models,
and reject/retry if the model returns malformed output.

## Alternatives Considered

- **Free-text review, formatted for human reading only.** Rejected: this cannot be
  scored automatically against the eval set (Stage 2), cannot be stored in
  structured DB columns (Stage 3), and cannot be reliably rendered as a table in
  the UI (Stage 4). It optimizes for looking finished in a demo while making every
  later stage harder.
- **Markdown output, parsed with regex.** Rejected: regex-parsing LLM output is
  fragile — small phrasing shifts break the parser silently. A JSON schema with
  Pydantic validation fails loudly (a validation error) instead of silently
  returning wrong data, which is the more dangerous failure mode for a system
  whose whole value proposition is trustworthy, measurable output.
- **Free-form JSON with no fixed schema (model decides field names).** Rejected:
  without a fixed contract, the eval script and DB schema would need to handle
  arbitrary shapes, defeating the purpose of structuring the output at all.

## Consequences

- **Positive:** every finding is directly scorable against the labeled eval set
  (does line X, category Y appear in both expected and actual output), directly
  storable in Postgres columns, and directly renderable in a table without custom
  parsing logic.
- **Negative:** constraining the model's output format can occasionally cause it
  to omit nuance it might have expressed in free text, and malformed responses
  (rare but real) need explicit handling — currently: one retry with an
  explicit "your last response was invalid JSON" correction message, then a 502
  if it still fails.
- **Revisit trigger:** if retry-on-malformed-output rate exceeds ~5% of requests
  in practice, worth investigating whether the schema is too rigid or the prompt
  needs stronger formatting instructions.