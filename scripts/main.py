import argparse
import logging
import pathlib
import sys

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from monitor import config, checks

subject = "Platform Status Alert"

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Check platform URLs and email failure reports.")
    parser.add_argument("--dry-run", action="store_true", help="Run checks and generate reports without sending email.")
    parser.add_argument("--report-only", action="store_true", help="Generate the PDF report without sending email.")
    parser.add_argument("--include-successes", action="store_true", help="Include successful checks in generated reports.")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout per attempt in seconds.")
    parser.add_argument("--retries", type=int, default=2, help="Number of retries after the first failed attempt.")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Delay between retries in seconds.")
    parser.add_argument("--workers", type=int, default=8, help="Maximum number of concurrent URL checks.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    named_urls = config.get_named_urls()
    if not named_urls:
        logging.error("No URL_* environment variables configured")
        sys.exit(1)

    results = checks.check_named_urls(
        named_urls,
        max_workers=args.workers,
        timeout=args.timeout,
        retries=args.retries,
        retry_delay=args.retry_delay,
    )
    failures = [r for r in results if not r["status"].startswith("Success")]
    report_results = results if args.include_successes else failures

    if not failures:
        logging.info("✅ All %d URL(s) OK – no e-mail", len(named_urls))
        if args.report_only and args.include_successes:
            from monitor import report

            out_pdf = pathlib.Path("platform_status_report.pdf")
            report.generate_pdf_report(
                report_results,
                outfile=str(out_pdf),
                total_checked=len(results),
                failure_count=0,
            )
            logging.info("Report-only mode wrote %s", out_pdf)
        return

    from monitor import report

    out_pdf = pathlib.Path("platform_status_report.pdf")
    report.generate_pdf_report(
        report_results,
        outfile=str(out_pdf),
        total_checked=len(results),
        failure_count=len(failures),
    )

    body = f"{len(failures)} site(s) failed. See attached report."
    if args.dry_run or args.report_only:
        logging.info("Email skipped because dry-run/report-only mode is enabled")
        return

    try:
        smtp = config.get_smtp_config()
    except config.ConfigError as exc:
        logging.error("Email configuration error: %s", exc)
        sys.exit(1)

    from monitor import emailer

    emailer.send_email(subject, body, [str(out_pdf)], smtp)

if __name__ == "__main__":
    main()
