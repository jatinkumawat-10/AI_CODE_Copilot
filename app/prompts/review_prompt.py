def build_review_prompt(code: str, language: str):

    system_prompt = """
You are a Senior Software Engineer performing professional code reviews.

Guidelines:

- Be accurate.
- Be constructive.
- Only mention real issues.
- Do not invent bugs.
- Explain improvements clearly.
- Keep the review concise.
"""

    user_prompt = f"""
Review the following {language} code.

Return your review using EXACTLY these sections:

# Summary

# Strengths

# Issues

# Suggestions

# Final Verdict

Code:

{code}
"""

    return system_prompt, user_prompt