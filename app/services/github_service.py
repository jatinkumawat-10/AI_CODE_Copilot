import httpx

from app.config import GITHUB_PAT

GITHUB_API_BASE = "https://api.github.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_pr_files(owner: str, repo: str, pr_number: int) -> list[dict]:
    """
    Fetch the list of changed files for a PR, each with its filename and
    unified diff patch. Uses the /files endpoint (structured, per-file)
    rather than the raw .diff endpoint, since we need each file's language
    individually for generate_review() -- a single combined diff string
    would need to be re-split by file anyway.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files"

    response = httpx.get(url, headers=_headers())
    response.raise_for_status()

    return response.json()


def post_pr_comment(owner: str, repo: str, pr_number: int, body: str) -> None:
    """
    Post a comment on a PR. Note: PRs are a special case of GitHub
    "issues" under the hood, so comments use the /issues/ endpoint even
    though this is a pull request, not a literal issue -- this is a real
    GitHub API quirk, not a mistake in this code.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments"

    response = httpx.post(url, headers=_headers(), json={"body": body})
    response.raise_for_status()