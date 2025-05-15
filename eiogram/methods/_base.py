from typing import Any, Dict, Optional
import aiohttp
import asyncio
from ..utils._exceptions import (
    TelegramError,
    TelegramAPIError,
    TimeoutError,
    InvalidTokenError,
    NetworkError,
    RateLimitError,
    UnauthorizedError,
)


class MethodBase:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"
        from ..core._bot import Bot

        self.bot = Bot(token=self.token)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Make a request to Telegram API

        Args:
            method: HTTP method (POST/GET)
            endpoint: API endpoint
            params: Request parameters
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response

        Raises:
            NetworkError: For network-related issues
            TimeoutError: When request times out
            TelegramAPIError: For Telegram API errors
            RateLimitError: When rate limited
            InvalidTokenError: For invalid bot token
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    json=params or {},
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    data = await self._parse_response(response)
                    return data

        except asyncio.TimeoutError:
            raise TimeoutError(timeout)
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}")
        except Exception as e:
            raise TelegramError(f"Unexpected error: {str(e)}")

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse and validate Telegram API response"""
        try:
            data: dict = await response.json()
        except ValueError:
            raise TelegramError("Invalid JSON response")

        if response.status == 401:
            raise InvalidTokenError()

        if response.status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        if not data.get("ok", False):
            error_code = data.get("error_code", 400)
            description = data.get("description", "Unknown error")

            if error_code == 401:
                raise UnauthorizedError(description)

            raise TelegramAPIError(description, error_code)

        return data
