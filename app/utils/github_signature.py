import hashlib
import hmac


def verify_github_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """
    Verify that a webhook payload actually came from GitHub, by recomputing
    the HMAC-SHA256 signature using our shared secret and comparing it
    against the one GitHub sent in the X-Hub-Signature-256 header.

    Without this check, anyone who discovers the webhook URL could send
    fake payloads pretending to be GitHub.
    """
    from app.config import GITHUB_WEBHOOK_SECRET

    if signature_header is None:
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            key=GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            msg=payload_body,
            digestmod=hashlib.sha256,
        ).hexdigest()
    )

    # hmac.compare_digest, not ==, to avoid a timing attack: a naive string
    # comparison exits early on the first mismatched character, and an
    # attacker could exploit those tiny timing differences to guess the
    # correct signature one character at a time. compare_digest always
    # takes the same amount of time regardless of where a mismatch occurs.
    return hmac.compare_digest(expected_signature, signature_header)