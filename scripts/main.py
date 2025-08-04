import logging, sys, pathlib
from monitor import config, checks, report, emailer

subject = f"Platform Status Alert "

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    named_urls = config.get_named_urls()
    if not named_urls:
        logging.error("URLS env var empty"); sys.exit(1)

    results = checks.check_named_urls(named_urls)
    failures = [r for r in results if r["status"] != "Success"]

    if not failures:
        logging.info("✅ All %d URL(s) OK – no e-mail", len(named_urls))
        return

    out_pdf = pathlib.Path("platform_status_report.pdf")
    report.generate_pdf_report(failures, outfile=str(out_pdf))

    body = f"{len(failures)} site(s) failed. See attached report."
    emailer.send_email(subject, body, [str(out_pdf)])

if __name__ == "__main__":
    main()
