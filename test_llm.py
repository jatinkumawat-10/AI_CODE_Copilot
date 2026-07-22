from app.llm.openrouter import client
from app.config import MODEL_NAME

response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Say hello in exactly one sentence."
        }
    ]
)
print("=" * 50)
print(f"Model: {response.model}")
print("=" * 50)

print("\nAnswer:")
print(response.choices[0].message.content)

print("\nUsage:")
print(f"Prompt Tokens: {response.usage.prompt_tokens}")
print(f"Completion Tokens: {response.usage.completion_tokens}")
print(f"Total Tokens: {response.usage.total_tokens}")

details = response.usage.completion_tokens_details
if details and details.reasoning_tokens is not None:
    print(f"Reasoning Tokens: {details.reasoning_tokens}")