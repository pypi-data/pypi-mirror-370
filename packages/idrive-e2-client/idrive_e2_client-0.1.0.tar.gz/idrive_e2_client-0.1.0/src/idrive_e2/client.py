from __future__ import annotations

from urllib.parse import urlparse
import aiohttp

from .errors import InvalidAuth, CannotConnect

GET_REGION_ENDPOINT_URL = "https://api.idrivee2.com/api/service/get_region_end_point"


class IDriveE2Client:
    """Async client for the IDrive e2 Get Region Endpoint API."""

    def __init__(self, session: aiohttp.ClientSession, *, request_timeout: int = 20) -> None:
        self._session = session
        self._timeout = request_timeout

    async def get_region_endpoint(self, access_key_id: str) -> str:
        """
        Resolve the endpoint URL for the provided access key.

        Returns:
            str: Normalized endpoint URL with scheme (e.g., "https://s3.eu-central-1.idrivee2-32.com")

        Raises:
            InvalidAuth: If credentials are invalid (resp_code < 0).
            CannotConnect: On network errors, bad status codes, or malformed response.
        """
        try:
            async with self._session.post(
                GET_REGION_ENDPOINT_URL,
                json={"access_key": access_key_id},
                timeout=self._timeout,
            ) as resp:
                if resp.status == 401:
                    raise InvalidAuth("Unauthorized")
                if resp.status >= 400:
                    raise CannotConnect(f"HTTP {resp.status}")
                payload = await resp.json()
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                raise InvalidAuth("Unauthorized") from err
            raise CannotConnect(f"Bad response: {err}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Transport error: {err}") from err

        # Validate and check API fields
        resp_code = payload.get("resp_code")
        resp_msg = payload.get("resp_msg", "Unknown error")

        if resp_code is None:
            raise CannotConnect("Missing resp_code in response")
        if not isinstance(resp_code, int):
            raise CannotConnect(f"Unexpected resp_code type: {resp_code}")
        if resp_code < 0:
            raise InvalidAuth(f"API error {resp_code}: {resp_msg}")
        if resp_code != 0:
            raise CannotConnect(f"Unexpected resp_code value: {resp_code}")

        # Extract domain
        domain_name = payload.get("domain_name")
        if not isinstance(domain_name, str) or not domain_name.strip():
            raise CannotConnect("Missing domain_name in response")
        endpoint_to_parse = (
            f"//{domain_name}" if "://" not in domain_name else domain_name
        )
        # Prepend '//' if no scheme so urlparse recognizes the host
        return urlparse(endpoint_to_parse, scheme="https").geturl()
