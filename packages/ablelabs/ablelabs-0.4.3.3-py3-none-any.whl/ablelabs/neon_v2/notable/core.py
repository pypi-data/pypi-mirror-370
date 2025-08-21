import httpx
from .decorators import extract_data_async

class Base:
    def __init__(self, base_url: str):
        self._timeout = 300
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            headers={"Content-Type": "application/json"},
            timeout=httpx.Timeout(self._timeout),
            limits=httpx.Limits(
                max_keepalive_connections=9999,
                max_connections=10,
            ),
        )

    @extract_data_async
    async def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self._base_url}{path}"

        response = await self._client.get(url, params=params, timeout=self._timeout)

        # Check status code
        if response.status_code != 200:
            raise Exception(
                f"API returned error status {response.status_code}: {response.reason_phrase}"
            )

        return response.json() if response.text else {}

    @extract_data_async
    async def _post(
        self, path: str, body: dict = None, params: dict = None
    ):
        url = f"{self._base_url}{path}"

        response = await self._client.post(
            url, json=body, params=params, timeout=self._timeout
        )

        # Check status code
        if response.status_code != 200:
            raise Exception(
                f"API returned error status {response.status_code}: {response.reason_phrase}"
            )

        return response.json() if response.text else {}
