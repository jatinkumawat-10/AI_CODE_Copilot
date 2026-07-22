def build_review_prompt(code: str, language: str) -> tuple[str, str]:
    """
    Build the prompts required for code review.
    """

    system_prompt = """
You are a Senior Software Engineer.

Review the provided code carefully.

Focus on:

- Bugs
- Code Quality
- Readability
- Performance
- Best Practices

Be constructive.
"""

    user_prompt = f"""
Review the following {language} code.

Code:

{code}
"""

    return system_prompt, user_prompt