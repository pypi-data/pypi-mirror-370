from __future__ import annotations
from typing import Dict, Optional
import httpx


class PromptevClient:
    """
    Minimal Python client for Promptev's compile endpoint.
    - POST /api/sdk/v1/prompt/client/{project_key}/{prompt_key}
    - Body: { "variables": { ... } }
    - Success: { "prompt": "..." }
    - Error (400): { "detail": "Missing required variables: ..." }  -> raises ValueError
    """

    def __init__(
        self,
        project_key: str,
        base_url: str = "https://api.promptev.ai",
        headers: Optional[Dict[str, str]] = None,  # e.g. {"X-PTV-API-Key": "..."}
        timeout: float = 30.0,
    ) -> None:
        self.project_key = project_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Create dedicated clients for connection reuse
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", **(headers or {})},
            timeout=self.timeout,
        )
        self._aclient = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", **(headers or {})},
            timeout=self.timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP clients (sync)."""
        try:
            self._client.close()
        finally:
            # Async client has a sync close too (since httpx 0.28+ keepers).
            # If you're on older httpx, use asyncio.run(self._aclient.aclose()).
            try:
                self._aclient.close()  # type: ignore[attr-defined]
            except Exception:
                pass

    # Optional context-manager support
    def __enter__(self) -> "PromptevClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    async def aclose(self) -> None:
        """Close the async client explicitly (optional if using context managers)."""
        await self._aclient.aclose()
        self._client.close()

    async def __aenter__(self) -> "PromptevClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # --------------------------
    # Sync API
    # --------------------------
    def get_prompt(
        self,
        prompt_key: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Synchronous compile call.
        """
        url = f"/api/sdk/v1/prompt/client/{self.project_key}/{prompt_key}"
        payload = {"variables": variables or {}}

        try:
            resp = self._client.post(url, json=payload)
        except httpx.HTTPError as e:
            raise RuntimeError(f"Network error: {e}") from e

        # Raise for non-2xx so we can parse detail for 400
        if resp.status_code == 400:
            # FastAPI commonly returns {"detail": "..."}
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = resp.text or "Bad Request"
            raise ValueError(detail if isinstance(detail, str) else "Bad Request")

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            # surface the body text to help debugging
            raise RuntimeError(f"Request failed ({resp.status_code}): {resp.text}") from e

        data = resp.json()
        compiled = data.get("prompt")
        if not isinstance(compiled, str):
            raise RuntimeError("Unexpected response: missing 'prompt' field")
        return compiled

    # --------------------------
    # Async API
    # --------------------------
    async def aget_prompt(
        self,
        prompt_key: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Asynchronous compile call.
        """
        url = f"/api/sdk/v1/prompt/client/{self.project_key}/{prompt_key}"
        payload = {"variables": variables or {}}

        try:
            resp = await self._aclient.post(url, json=payload)
        except httpx.HTTPError as e:
            raise RuntimeError(f"Network error: {e}") from e

        if resp.status_code == 400:
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = resp.text or "Bad Request"
            raise ValueError(detail if isinstance(detail, str) else "Bad Request")

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Request failed ({resp.status_code}): {resp.text}") from e

        data = resp.json()
        compiled = data.get("prompt")
        if not isinstance(compiled, str):
            raise RuntimeError("Unexpected response: missing 'prompt' field")
        return compiled
