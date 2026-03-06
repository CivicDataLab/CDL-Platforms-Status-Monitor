import os
from dotenv import load_dotenv

load_dotenv()

def get_named_urls():
    disabled_raw = os.getenv("DISABLED_GROUPS", "")
    disabled_groups = [g.strip().upper() for g in disabled_raw.split(",") if g.strip()]

    urls = {}
    for k, v in os.environ.items():
        if k.startswith("URL_") and v.strip():
            name = k[4:]  # strip "URL_" prefix
            if any(name.upper() == group or name.upper().startswith(group + "_") for group in disabled_groups):
                continue
            urls[name] = v.strip()
    return urls

SMTP = {
    "host": os.getenv("EMAIL_HOST", ""),
    "port": int(os.getenv("EMAIL_PORT", 587)),
    "user": os.getenv("EMAIL_USER", ""),
    "password": os.getenv("EMAIL_PASS", ""),
    "to": os.getenv("EMAIL_TO", ""),
}
