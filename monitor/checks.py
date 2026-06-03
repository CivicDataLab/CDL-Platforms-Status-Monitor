import os
import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

ALLOW_403_FOR = {
    d.strip().lower()
    for d in os.getenv("ALLOW_403_FOR", "").split(",")
    if d.strip()
}

def _domain_allowed(url: str, allowlist: set) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in allowlist)


def _classify_response(url: str, status_code: int) -> tuple[str, str | None]:
    if status_code == 200:
        return "Success", None

    if status_code == 403 and _domain_allowed(url, ALLOW_403_FOR):
        return "Success (403 allowed)", None

    return f"HTTP {status_code}", None


def _result(
    url: str,
    status: str,
    status_code: int | None,
    error: str | None,
    response_time_ms: int | None,
    attempts: int,
) -> dict:
    return {
        "url": url,
        "status": status,
        "status_code": status_code,
        "error": error,
        "response_time_ms": response_time_ms,
        "attempts": attempts,
    }


def check_url(url: str, timeout: int = 10, retries: int = 2, retry_delay: float = 1.0) -> dict:
    """Return dict with url, status, status_code, error, response time, and attempts."""
    max_attempts = retries + 1
    last_error = None

    for attempt in range(1, max_attempts + 1):
        started = time.perf_counter()
        response_time_ms = None

        try:
            response = requests.get(url, timeout=timeout, headers=HEADERS)
            response_time_ms = round((time.perf_counter() - started) * 1000)
            status, error = _classify_response(url, response.status_code)

            if status.startswith("Success") or attempt == max_attempts:
                return _result(
                    url,
                    status,
                    response.status_code,
                    error,
                    response_time_ms,
                    attempt,
                )

        except Exception as exc:
            response_time_ms = round((time.perf_counter() - started) * 1000)
            last_error = str(exc)

            if attempt == max_attempts:
                logging.error("Error checking %s after %d attempt(s) -> %s", url, attempt, exc)
                return _result(url, "Failed", None, last_error, response_time_ms, attempt)

        if retry_delay:
            time.sleep(retry_delay)

    return _result(url, "Failed", None, last_error, None, max_attempts)

def _check_named_url(item, timeout: int, retries: int, retry_delay: float):
    name, url = item
    result = check_url(url, timeout=timeout, retries=retries, retry_delay=retry_delay)
    result["name"] = name
    return result


def check_named_urls(
    named_urls: dict,
    max_workers: int = 8,
    timeout: int = 10,
    retries: int = 2,
    retry_delay: float = 1.0,
):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(
            executor.map(
                lambda item: _check_named_url(item, timeout, retries, retry_delay),
                named_urls.items(),
            )
        )
    return results
