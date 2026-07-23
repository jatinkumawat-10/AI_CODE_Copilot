def build_review_prompt(code: str, language: str):

    system_prompt = """
You are a senior software engineer performing professional code reviews.

Return ONLY valid JSON.

Never return markdown.

Never explain the JSON.

Never wrap the JSON inside code fences.

If no issues exist, return empty arrays instead of inventing issues.
"""

    user_prompt = f"""
Review the following {language} code.

Return exactly this JSON schema:

{{
    "summary": "string",
    "strengths": [
        "string"
    ],
    "issues": [
        "string"
    ],
    "suggestions": [
        "string"
    ],
    "verdict": "string"
}}

Code:

{code}
"""

    return system_prompt, user_prompt
