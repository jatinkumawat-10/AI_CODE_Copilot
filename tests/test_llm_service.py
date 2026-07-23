import json

from app.services.llm_service import generate
class FakeResponse:

    model = "test-model"

    class usage:
        prompt_tokens = 10
        completion_tokens = 20
        total_tokens = 30

    class Choice:

        class Message:
            content = json.dumps(
                {
                    "summary": "Good code",
                    "strengths": ["Readable"],
                    "issues": [],
                    "suggestions": [],
                    "verdict": "Looks good"
                }
            )

        message = Message()

    choices = [Choice()]

class FakeClient:

    class Chat:

        class Completions:

            @staticmethod
            def create(*args, **kwargs):
                return FakeResponse()

        completions = Completions()

    chat = Chat()
def test_generate(monkeypatch):

    monkeypatch.setattr(
    "app.services.llm_service.get_client",
    lambda: FakeClient(),
)

    response = generate(
        system_prompt="system",
        user_prompt="user",
    )

    assert response.model == "test-model"

    assert response.content.summary == "Good code"

    assert response.content.verdict == "Looks good"

    assert response.prompt_tokens == 10

    assert response.total_tokens == 30

import pytest

from app.exceptions import LLMServiceError


class FailingClient:

    class Chat:

        class Completions:

            @staticmethod
            def create(*args, **kwargs):
                raise Exception("OpenRouter unavailable")

        completions = Completions()

    chat = Chat()


def test_generate_raises_llm_service_error(monkeypatch):

    monkeypatch.setattr(
    "app.services.llm_service.get_client",
    lambda: FailingClient(),
)

    with pytest.raises(LLMServiceError):

        generate(
            system_prompt="system",
            user_prompt="user",
        )