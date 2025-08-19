import os
import requests
import logging
from urllib.parse import urlparse

ALLOW_403_FOR = {
    d.strip().lower()
    for d in os.getenv("ALLOW_403_FOR", "").split(",")
    if d.strip()
}

def check_url(url: str, timeout: int = 10) -> dict:
    """Return dict with url, status, status_code, error."""
    try:
        r = requests.get(url, timeout=timeout)
        host = urlparse(url).hostname or ""
        host = host.lower()

        print(f"URL: {url}, host: {host}, ALLOW_403_FOR: {ALLOW_403_FOR}")

        if r.status_code == 200:
            return {"url": url, "status": "Success", "status_code": 200, "error": None}

        if r.status_code == 403:
            if host.endswith("substack.com") or host == "substack.com":
                return {
                    "url": url,
                    "status": "Success (403 allowed)",
                    "status_code": 403,
                    "error": None
                }

        return {
            "url": url,
            "status": f"HTTP {r.status_code}",
            "status_code": r.status_code,
            "error": None
        }

    except Exception as exc:
        logging.error("Error checking %s -> %s", url, exc)
        return {
            "url": url,
            "status": "Failed",
            "status_code": None,
            "error": str(exc)
        }

def check_named_urls(named_urls: dict):
    results = []
    for name, url in named_urls.items():
        result = check_url(url)  # existing function
        result["name"] = name    # add the name
        results.append(result)
    return results