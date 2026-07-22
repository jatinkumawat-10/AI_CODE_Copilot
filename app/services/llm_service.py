from app.config import MODEL_NAME
from app.llm.openrouter import client


def generate(system_prompt: str, user_prompt: str) -> str:
    """
    Generate a response from the configured LLM.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content