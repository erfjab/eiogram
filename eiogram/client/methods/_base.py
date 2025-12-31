from typing import Any, Dict, Optional, TYPE_CHECKING
import aiohttp
import ujson
import asyncio
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
    _shared_session: Optional[aiohttp.ClientSession] = None

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.token = bot.token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    @classmethod
    def _get_session(cls) -> aiohttp.ClientSession:
        if cls._shared_session is None or cls._shared_session.closed:
            connector = aiohttp.TCPConnector(
                limit=0,
                ttl_dns_cache=300,
                use_dns_cache=True,
                enable_cleanup_closed=True,
                keepalive_timeout=30,
            )
            cls._shared_session = aiohttp.ClientSession(connector=connector, json_serialize=ujson.dumps)
        return cls._shared_session

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

        session = self._get_session()
        try:
            async with session.request(
                method.upper(),
                f"{self.base_url}{endpoint}",
                json=request_json,
                timeout=aiohttp.ClientTimeout(total=total_timeout),
            ) as response:
                return await self._parse_response(response)
        except asyncio.TimeoutError:
            raise TimeoutError(total_timeout)
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")
        except Exception as e:
            raise TelegramError(f"Unexpected error: {e}")

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse and validate Telegram API response."""
        try:
            data = await response.json(loads=ujson.loads)
        except ValueError:
            raise TelegramError("Invalid JSON response")

        status = response.status
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
