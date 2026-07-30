import hashlib
import hmac

import pytest

from app.utils.github_signature import verify_github_signature


def _sign(payload_body: bytes, secret: str) -> str:
    """Helper: compute a valid signature the same way GitHub would."""
    return (
        "sha256="
        + hmac.new(
            key=secret.encode("utf-8"),
            msg=payload_body,
            digestmod=hashlib.sha256,
        ).hexdigest()
    )


def test_verify_github_signature_valid(monkeypatch):
    monkeypatch.setattr("app.config.GITHUB_WEBHOOK_SECRET", "test-secret")

    payload = b'{"action": "opened"}'
    valid_signature = _sign(payload, "test-secret")

    assert verify_github_signature(payload, valid_signature) is True


def test_verify_github_signature_invalid(monkeypatch):
    monkeypatch.setattr("app.config.GITHUB_WEBHOOK_SECRET", "test-secret")

    payload = b'{"action": "opened"}'
    wrong_signature = _sign(payload, "wrong-secret")

    assert verify_github_signature(payload, wrong_signature) is False


def test_verify_github_signature_missing_header(monkeypatch):
    monkeypatch.setattr("app.config.GITHUB_WEBHOOK_SECRET", "test-secret")

    payload = b'{"action": "opened"}'

    assert verify_github_signature(payload, None) is False


def test_verify_github_signature_tampered_payload(monkeypatch):
    monkeypatch.setattr("app.config.GITHUB_WEBHOOK_SECRET", "test-secret")

    original_payload = b'{"action": "opened"}'
    signature = _sign(original_payload, "test-secret")

    tampered_payload = b'{"action": "closed"}'

    assert verify_github_signature(tampered_payload, signature) is False


def test_verify_github_signature_raises_if_secret_not_configured(monkeypatch):
    """
    A missing/empty GITHUB_WEBHOOK_SECRET must fail loudly, not silently
    verify against an empty string (which would make verification
    meaningless -- any signature computed with an empty key would be
    trivially reproducible).
    """
    monkeypatch.setattr("app.config.GITHUB_WEBHOOK_SECRET", None)

    with pytest.raises(RuntimeError):
        verify_github_signature(b'{"action": "opened"}', "sha256=anything")
