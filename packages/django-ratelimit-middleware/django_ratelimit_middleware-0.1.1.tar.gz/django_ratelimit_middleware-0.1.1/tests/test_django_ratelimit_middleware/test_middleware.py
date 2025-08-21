"""tests/test_django_ratelimit_middleware/test_middleware.py.

Unit tests for the django_ratelimit_middleware.middleware module.

This module contains pytest-based tests for the RateLimitMiddleware class,
which enforces simple IP/user-based rate limiting in Django.

Tests include:
    - Anonymous user request limiting
    - Authenticated user request limiting
    - Rate limit reset after the time window expires

Fixtures:
    rf: Provides a Django RequestFactory instance for creating test requests.
    clear_cache: Clears the Django cache before and after each test to avoid
                 cross-test contamination.

Test tools used:
    - pytest
    - pytest-django
    - Django RequestFactory
    - Django override_settings
    - Django caching framework
"""

import time
from typing import Generator, Any

import pytest
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, override_settings
from django.contrib.auth.models import AnonymousUser

from src.django_ratelimit_middleware.middleware import RateLimitMiddleware


@pytest.fixture
def rf() -> RequestFactory:
    """Fixture providing a Django RequestFactory for creating test requests.

    Returns:
        RequestFactory: An instance of Django's RequestFactory.
    """
    return RequestFactory()


@pytest.fixture(autouse=True)
def clear_cache() -> Generator[Any, None, None]:
    """Fixture to clear the Django cache before and after each test.

    Ensures that rate limit state does not leak between tests.
    """
    cache.clear()
    yield
    cache.clear()


def dummy_view(request: HttpRequest) -> HttpResponse:
    """Simple test view that returns an HTTP 200 response.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        HttpResponse: A simple 200 OK response.
    """
    return HttpResponse("OK")


@pytest.mark.django_db
@override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_WINDOW=1)
def test_rate_limit_anonymous(rf: RequestFactory) -> None:
    """Test rate limiting for an anonymous user.

    Verifies that requests exceeding the limit return HTTP 429.
    """
    middleware = RateLimitMiddleware(dummy_view)
    request: HttpRequest = rf.get("/")
    request.user = AnonymousUser()

    response1: HttpResponse = middleware(request)
    assert response1.status_code == 200

    response2: HttpResponse = middleware(request)
    assert response2.status_code == 200

    response3: HttpResponse = middleware(request)
    assert response3.status_code == 429
    assert "Retry-After" in response3.headers


@pytest.mark.django_db
@override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_WINDOW=1)
def test_rate_limit_authenticated(rf: RequestFactory, django_user_model) -> None:
    """Test rate limiting for an authenticated user.

    Verifies that the middleware tracks requests per user ID and enforces limits.
    """
    user = django_user_model.objects.create_user(username="testuser", password="123")
    middleware = RateLimitMiddleware(dummy_view)
    request: HttpRequest = rf.get("/")
    request.user = user

    response1: HttpResponse = middleware(request)
    assert response1.status_code == 200

    response2: HttpResponse = middleware(request)
    assert response2.status_code == 200

    response3: HttpResponse = middleware(request)
    assert response3.status_code == 429
    assert "Retry-After" in response3.headers


@pytest.mark.django_db
@override_settings(RATE_LIMIT_REQUESTS=1, RATE_LIMIT_WINDOW=1)
def test_rate_limit_reset(rf: RequestFactory, django_user_model) -> None:
    """Test that the rate limit resets after the time window expires.

    Simulates a user exceeding the limit and then waiting for the window to reset.
    """
    user = django_user_model.objects.create_user(username="resetuser", password="123")
    middleware = RateLimitMiddleware(dummy_view)
    request: HttpRequest = rf.get("/")
    request.user = user

    response1: HttpResponse = middleware(request)
    assert response1.status_code == 200

    # Exceed limit
    response2: HttpResponse = middleware(request)
    assert response2.status_code == 429

    # Wait for time window to expire
    time.sleep(1.1)
    response3: HttpResponse = middleware(request)
    assert response3.status_code == 200
