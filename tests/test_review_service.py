from app.schemas.llm import LLMResponse
from app.schemas.review import ReviewResult
from app.services.review_service import review_code

captured = {}


def fake_generate(system_prompt: str, user_prompt: str):
    captured["system_prompt"] = system_prompt
    captured["user_prompt"] = user_prompt

    return LLMResponse(
        content=ReviewResult(
            summary="Good code",
            strengths=["Readable"],
            issues=[],
            suggestions=[],
            verdict="Looks good",
        ),
        model="test-model",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        latency=0.01,
    )


def test_review_code_returns_review(monkeypatch):
    """
    review_code should return the validated ReviewResult
    produced by the LLM service.
    """

    # Replace generate() with our fake version
    monkeypatch.setattr(
        "app.services.review_service.generate",
        fake_generate,
    )

    result = review_code(
        code="print('Hello')",
        language="python",
    )

    assert isinstance(result, ReviewResult)
    assert result.summary == "Good code"
    assert result.verdict == "Looks good"
    assert "software engineer" in captured["system_prompt"].lower()
    assert "python" in captured["user_prompt"].lower()
    assert "print('Hello')" in captured["user_prompt"]
