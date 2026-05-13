"""Canvas API health diagnostic — distinguish auth failure / outage / network.

Used by `canvas ping` and by clients that want to give a friendly error
instead of a JSONDecodeError when Canvas returns an HTML status page.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import httpx

from .config import load_config, mask_token


@dataclass
class APIStatus:
    base_url: str
    masked_token: str
    reachable: bool             # True if /api/v1/users/self returned 200 with JSON
    auth_ok: bool | None        # True if 200, False if 401/403, None otherwise
    status_code: int | None
    final_url: str | None       # after redirects
    content_type: str | None
    user_name: str | None
    user_id: int | None
    error: str | None           # short human-readable diagnosis

    def to_dict(self) -> dict:
        return asdict(self)


def check_api(timeout: float = 8.0) -> APIStatus:
    """Hit /api/v1/users/self and classify the response."""
    config = load_config()
    base = config["base_url"].rstrip("/")
    token = config["api_token"]
    url = f"{base}/api/v1/users/self"
    headers = {"Authorization": f"Bearer {token}"}

    status = APIStatus(
        base_url=base, masked_token=mask_token(token),
        reachable=False, auth_ok=None,
        status_code=None, final_url=None, content_type=None,
        user_name=None, user_id=None, error=None,
    )

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        status.error = f"network error: {exc}"
        return status

    status.status_code = resp.status_code
    status.final_url = str(resp.url)
    status.content_type = resp.headers.get("content-type", "")

    # Redirected off canvas.eee.uci.edu → almost certainly an outage redirect
    if "canvas" not in status.final_url.lower():
        status.error = (
            "Canvas API was redirected off-domain — likely outage. "
            f"Landed on {status.final_url}"
        )
        return status

    if resp.status_code in (401, 403):
        status.auth_ok = False
        status.error = (
            f"HTTP {resp.status_code} — token rejected. "
            "Token may be revoked or expired."
        )
        return status

    if resp.status_code >= 500:
        status.error = f"Canvas server error (HTTP {resp.status_code})"
        return status

    if "json" not in (status.content_type or "").lower():
        status.error = (
            f"Canvas returned non-JSON (content-type: {status.content_type}). "
            "Likely an outage or maintenance page."
        )
        return status

    try:
        body = resp.json()
    except ValueError as exc:
        status.error = f"Response was 200 but not parseable JSON: {exc}"
        return status

    status.reachable = True
    status.auth_ok = True
    status.user_name = body.get("name")
    status.user_id = body.get("id")
    return status
