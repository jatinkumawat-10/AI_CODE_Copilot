from app.prompts.review_prompt import build_review_prompt


# TEST 1
def test_build_review_prompt_returns_two_strings():
    # Arrange & Act
    system_prompt, user_prompt = build_review_prompt(
        code="print('Hello')",
        language="python",
    )

    # Assert
    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)


# Test 2
def test_system_prompt_contains_role():
    system_prompt, _ = build_review_prompt(
        code="print('Hello')",
        language="python",
    )

    assert "software engineer" in system_prompt.lower()


# TEST 3
def test_user_prompt_contains_language():
    _, user_prompt = build_review_prompt(
        code="print('Hello')",
        language="python",
    )

    assert "python" in user_prompt


# TEST 4
def test_user_prompt_contains_code():
    code = "print('Hello')"

    _, user_prompt = build_review_prompt(
        code=code,
        language="python",
    )

    assert code in user_prompt


# TEST 5
def test_user_prompt_requires_json():
    _, user_prompt = build_review_prompt(
        code="print('Hello')",
        language="python",
    )

    assert "summary" in user_prompt
    assert "strengths" in user_prompt
    assert "issues" in user_prompt
    assert "suggestions" in user_prompt
    assert "verdict" in user_prompt
