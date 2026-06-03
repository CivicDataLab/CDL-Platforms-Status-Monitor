import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


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


def parse_email_recipients(raw: str):
    normalized = raw.replace(";", ",")
    return [email.strip() for email in normalized.split(",") if email.strip()]


def get_smtp_config():
    port_raw = os.getenv("EMAIL_PORT", "587")
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ConfigError("EMAIL_PORT must be an integer") from exc

    smtp = {
        "host": os.getenv("EMAIL_HOST", "").strip(),
        "port": port,
        "user": os.getenv("EMAIL_USER", "").strip(),
        "password": os.getenv("EMAIL_PASS", ""),
        "to": parse_email_recipients(os.getenv("EMAIL_TO", "")),
    }

    missing = [
        key
        for key in ("host", "user", "password")
        if not smtp[key]
    ]
    if missing:
        env_var_names = {
            "host": "EMAIL_HOST",
            "user": "EMAIL_USER",
            "password": "EMAIL_PASS",
        }
        env_names = ", ".join(env_var_names[key] for key in missing)
        raise ConfigError(f"Missing required email configuration: {env_names}")

    if not smtp["to"]:
        raise ConfigError("EMAIL_TO must contain at least one recipient")

    return smtp
