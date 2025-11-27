from typing import Any, Dict, Optional, TYPE_CHECKING
import httpx
from ...utils.exceptions import (
    TelegramError,
    TelegramAPIError,
    TimeoutError,
    InvalidTokenError,
    NetworkError,
    RateLimitError,
    UnauthorizedError,
)

if TYPE_CHECKING:
    from .._bot import Bot


class MethodBase:
    _shared_client: Optional[httpx.AsyncClient] = None

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.token = bot.token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._shared_client is None or cls._shared_client.is_closed:
            cls._shared_client = httpx.AsyncClient()
        return cls._shared_client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 3.0,
    ) -> Dict[str, Any]:
        request_json = params or {}

        telegram_wait = float(request_json.get("timeout", 0))
        total_timeout = max(timeout, telegram_wait + 5)

        client = self._get_client()
        try:
            response = await client.request(
                method.upper(),
                f"{self.base_url}{endpoint}",
                json=request_json,
                timeout=total_timeout,
            )
        except httpx.TimeoutException:
            raise TimeoutError(total_timeout)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")
        except Exception as e:
            raise TelegramError(f"Unexpected error: {e}")

        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse and validate Telegram API response."""
        try:
            data: dict = response.json()
        except ValueError:
            raise TelegramError("Invalid JSON response")

        status = response.status_code
        if status == 401:
            raise InvalidTokenError()
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        if not data.get("ok", False):
            error_code = data.get("error_code", status)
            description = data.get("description", "Unknown error")
            if error_code == 401:
                raise UnauthorizedError(description)
            raise TelegramAPIError(description, error_code)

        return data
