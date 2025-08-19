import os
import requests
import logging

def check_url(url: str, timeout: int = 10) -> dict:
    """Return dict with url, status, status_code, error."""
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return {"url": url, "status": "Success", "status_code": 200, "error": None}
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