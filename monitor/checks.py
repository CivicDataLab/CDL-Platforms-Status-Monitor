import os
import requests
import logging
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

def check_url(url: str, timeout: int = 10) -> dict:
    """Return dict with url, status, status_code, error."""
    try:
        r = requests.get(url, timeout=timeout, headers=HEADERS)

        if r.status_code == 200:
            return {"url": url, "status": "Success", "status_code": 200, "error": None}

        if r.status_code == 403 and _domain_allowed(url, ALLOW_403_FOR):
            return {"url": url, "status": "Success (403 allowed)", "status_code": 403, "error": None}

        return {"url": url, "status": f"HTTP {r.status_code}", "status_code": r.status_code, "error": None}

    except Exception as exc:
        logging.error("Error checking %s -> %s", url, exc)
        return {"url": url, "status": "Failed", "status_code": None, "error": str(exc)}

def _check_named_url(item):
    name, url = item
    result = check_url(url)
    result["name"] = name
    return result


def check_named_urls(named_urls: dict, max_workers: int = 8):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_check_named_url, named_urls.items()))
    return results
