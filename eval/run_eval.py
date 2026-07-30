"""
Eval runner for the AI Code Review Platform.
Stage 2 of the project journey: measures the review service's accuracy
against a labeled benchmark of planted bugs.
"""

import json
import time
from pathlib import Path

from app.config import MODEL_NAME
from app.exceptions import LLMServiceError
from app.llm.openrouter import get_client
from app.services.review_service import review_code

CASES_DIR = Path(__file__).parent / "cases"
DELAY_BETWEEN_CALLS_SECONDS = 2


def load_cases() -> list[dict]:
    """Load every *.json test case from eval/cases/ into a list of dicts."""
    cases = []
    for case_file in sorted(CASES_DIR.glob("*.json")):
        with open(case_file) as f:
            cases.append(json.load(f))
    return cases


def keyword_match(issues: list[str], key_concepts: list[str]) -> bool:
    """
    Return True if any key_concept appears as a case-insensitive substring
    in any issue string. This is the cheap, fast first pass of the cascade.
    """
    issues_text = " ".join(issues).lower()
    return any(concept.lower() in issues_text for concept in key_concepts)


def llm_judge(issues: list[str], bug_description: str) -> bool:
    """
    Fallback for the ~20% of cases keyword_match doesn't catch. Asks the
    model directly whether the issues list semantically describes the
    planted bug. Only called when keyword_match already returned False,
    per the cascade documented in SCORING_STRATEGY.md.
    """
    client = get_client()

    issues_text = "\n".join(f"- {issue}" for issue in issues)
    prompt = f"""A code review flagged the following issues:
{issues_text}

Does any of the above issue describe this specific problem: "{bug_description}"?
Answer with exactly one word: yes or no."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content.strip().lower()
    return answer.startswith("yes")


N_TRIALS = 5


def run_single_trial(case: dict) -> dict:
    """
    One call to the real review service for one case, scored via the
    keyword-first cascade. Resilient to upstream failures (e.g. 429 rate
    limits) — a failed trial is recorded as an error, not raised, so one
    bad call doesn't discard every other result already computed in this
    run. This directly addresses the crash observed hitting OpenRouter's
    free-tier rate limit mid-run.
    """
    time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

    try:
        result = review_code(code=case["code"], language=case["language"])
    except LLMServiceError as e:
        return {"flagged": None, "method": "error", "raw_issues": None, "error": str(e)}

    bug = case["planted_bug"]
    hit_via_keyword = keyword_match(result.issues, bug["key_concepts"])

    if hit_via_keyword:
        flagged, method = True, "keyword"
    else:
        flagged = llm_judge(result.issues, bug["description"])
        method = "llm_judge"

    return {
        "flagged": flagged,
        "method": method,
        "raw_issues": result.issues,
        "error": None,
    }


def score_case(case: dict, n_trials: int = N_TRIALS) -> dict:
    """
    Run one case n_trials times (default 5) and report a hit rate instead
    of a single boolean. Non-determinism means one run can flip HIT/MISS
    on identical input (observed directly on case 002) — a hit rate is a
    meaningfully more trustworthy signal than one lucky or unlucky call.

    Error trials (upstream failures) are excluded from the hit-rate
    denominator — an error means "we never got a real answer," which is a
    different fact than "the model tried and missed." Conflating the two
    would silently make the model look worse than it actually performed.
    """
    trials = [run_single_trial(case) for _ in range(n_trials)]
    valid_trials = [t for t in trials if t["error"] is None]
    error_trials = [t for t in trials if t["error"] is not None]
    hits = sum(1 for t in valid_trials if t["flagged"])

    return {
        "case_id": case["case_id"],
        "expected_to_flag": case["expected_to_flag"],
        "hits": hits,
        "n_valid_trials": len(valid_trials),
        "n_errors": len(error_trials),
        "hit_rate": hits / len(valid_trials) if valid_trials else None,
        "trials": trials,
    }


def run_all() -> list[dict]:
    """Run every case in eval/cases/ and return per-case aggregated results."""
    cases = load_cases()
    return [score_case(case) for case in cases]


if __name__ == "__main__":
    results = run_all()

    true_positive_cases = [r for r in results if r["expected_to_flag"]]
    total_hits = sum(r["hits"] for r in true_positive_cases)
    total_valid = sum(r["n_valid_trials"] for r in true_positive_cases)
    total_errors = sum(r["n_errors"] for r in true_positive_cases)
    recall = total_hits / total_valid if total_valid else 0.0

    for r in results:
        methods = [t["method"] for t in r["trials"] if t["error"] is None]
        method_summary = (
            f"keyword={methods.count('keyword')}, "
            f"llm_judge={methods.count('llm_judge')}"
        )
        hit_rate_str = (
            f"{r['hits']}/{r['n_valid_trials']}"
            if r["n_valid_trials"]
            else "no valid trials"
        )
        error_note = f", {r['n_errors']} errored" if r["n_errors"] else ""
        print(f"{r['case_id']}: {hit_rate_str} hit rate ({method_summary}){error_note}")

    print(
        f"\nOverall recall across {len(true_positive_cases)} cases: "
        f"{recall:.1%} ({total_hits}/{total_valid} valid trials, "
        f"{total_errors} errored and excluded)"
    )
