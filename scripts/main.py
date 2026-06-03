import logging, pathlib, sys

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from monitor import config, checks, report, emailer

subject = "Platform Status Alert"

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    named_urls = config.get_named_urls()
    if not named_urls:
        logging.error("No URL_* environment variables configured")
        sys.exit(1)

    results = checks.check_named_urls(named_urls)
    failures = [r for r in results if not r["status"].startswith("Success")]

    if not failures:
        logging.info("✅ All %d URL(s) OK – no e-mail", len(named_urls))
        return

    out_pdf = pathlib.Path("platform_status_report.pdf")
    report.generate_pdf_report(failures, outfile=str(out_pdf))

    body = f"{len(failures)} site(s) failed. See attached report."
    try:
        smtp = config.get_smtp_config()
    except config.ConfigError as exc:
        logging.error("Email configuration error: %s", exc)
        sys.exit(1)

    emailer.send_email(subject, body, [str(out_pdf)], smtp)

if __name__ == "__main__":
    main()
