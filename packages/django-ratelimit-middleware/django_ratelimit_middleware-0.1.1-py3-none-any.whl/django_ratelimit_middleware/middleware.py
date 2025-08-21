"""src/django_ratelimit_middleware/middleware.py.

This module provides a Django middleware class for simple IP- or user-based
rate limiting. It is designed to prevent abuse by limiting the number of
requests a client can make in a given time window.

The middleware uses Django's cache framework to store request timestamps and
enforces limits based on configurable settings:

    - RATE_LIMIT_REQUESTS: Maximum number of requests allowed per window (default 100)
    - RATE_LIMIT_WINDOW: Time window in seconds (default 60)

Example usage in settings.py:

    MIDDLEWARE = [
        # ...
        "django_ratelimit_middleware.middleware.RateLimitMiddleware",
    ]

    RATE_LIMIT_REQUESTS = 60
    RATE_LIMIT_WINDOW = 60

Classes:
    RateLimitMiddleware: Middleware for enforcing request rate limits.

"""

import time
from typing import Callable
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.conf import settings


class RateLimitMiddleware:
    """Django middleware for simple IP/user-based rate limiting.

    This middleware tracks request timestamps per client (IP address or
    authenticated user) and limits the number of requests within a time window.

    Configuration via Django settings:
        RATE_LIMIT_REQUESTS: int
            Maximum number of requests allowed per time window (default: 100)
        RATE_LIMIT_WINDOW: int
            Time window in seconds for rate limiting (default: 60)

    Attributes:
        get_response (Callable[[HttpRequest], HttpResponse]):
            The next middleware or view.
        rate_limit (int):
            Maximum requests allowed.
        time_window (int):
            Time window in seconds.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the RateLimitMiddleware.

        Args:
            get_response (Callable[[HttpRequest], HttpResponse]):
                The next middleware or view function in the request/response chain.
        """
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.rate_limit: int = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        self.time_window: int = getattr(settings, "RATE_LIMIT_WINDOW", 60)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process an incoming HTTP request and enforce rate limits.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse:
                Either the normal response from the next middleware/view or a 429 Too
                Many Requests response if the limit is exceeded.
        """
        identifier: str = self._get_identifier(request)
        cache_key: str = f"rl:{identifier}"
        history: list[float] = cache.get(cache_key, [])

        now: float = time.time()
        history = [ts for ts in history if now - ts < self.time_window]
        history.append(now)

        if len(history) > self.rate_limit:
            retry_after: int = int(self.time_window - (now - history[0]))
            return JsonResponse(
                {
                    "detail": "Too Many Requests",
                    "retry_after_seconds": retry_after,
                },
                status=429,
                headers={"Retry-After": str(retry_after)},
            )

        cache.set(cache_key, history, timeout=self.time_window)
        return self.get_response(request)

    def _get_identifier(self, request: HttpRequest) -> str:
        """Determine a unique identifier for the client making the request.

        Uses the authenticated user's ID if available, otherwise the remote IP.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            str: A string identifier for rate limiting.
        """
        if request.user.is_authenticated:
            return f"user:{request.user.pk}"
        return request.META.get("REMOTE_ADDR", "unknown")
