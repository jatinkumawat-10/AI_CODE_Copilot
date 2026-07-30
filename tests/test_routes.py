from app.schemas.llm import LLMResponse
from app.schemas.review import ReviewResult


def fake_generate_review(code: str, language: str):
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


def test_review_route_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.review.generate_review",
        fake_generate_review,
    )

    response = client.post(
        "/api/v1/review",
        json={
            "code": "print('Hello')",
            "language": "python",
        },
    )
    # test123
    assert response.status_code == 200

    data = response.json()

    assert data["summary"] == "Good code"
    assert data["strengths"] == ["Readable"]
    assert data["issues"] == []
    assert data["suggestions"] == []
    assert data["verdict"] == "Looks good"
