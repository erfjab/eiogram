class TelegramError(Exception):
    """Base class for all Telegram API errors"""

    def __init__(self, message: str = "Telegram API Error"):
        super().__init__(message)


class TelegramAPIError(TelegramError):
    """Error returned by Telegram API (ok: false)"""

    def __init__(self, description: str, error_code: int):
        self.error_code = error_code
        self.description = description
        super().__init__(f"API Error {error_code}: {description}")


class NetworkError(TelegramError):
    """Network-related errors"""

    pass


class TimeoutError(NetworkError):
    """Request timeout error"""

    def __init__(self, timeout: float):
        super().__init__(f"Request timed out after {timeout} seconds")
        self.timeout = timeout


class RateLimitError(TelegramError):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")


class InvalidTokenError(TelegramError):
    """Invalid bot token"""

    def __init__(self):
        super().__init__("Invalid bot token provided")


class UnauthorizedError(TelegramError):
    """Unauthorized access"""

    def __init__(self, description: str):
        super().__init__(f"Unauthorized: {description}")
