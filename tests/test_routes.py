from app.schemas.review import ReviewResult


def fake_review_code(code: str, language: str):
    return ReviewResult(
        summary="Good code",
        strengths=["Readable"],
        issues=[],
        suggestions=[],
        verdict="Looks good",
    )


def test_review_route_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.review.review_code",
        fake_review_code,
    )

    response = client.post(
        "/api/v1/review",
        json={
            "code": "print('Hello')",
            "language": "python",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["summary"] == "Good code"
    assert data["strengths"] == ["Readable"]
    assert data["issues"] == []
    assert data["suggestions"] == []
    assert data["verdict"] == "Looks good"
