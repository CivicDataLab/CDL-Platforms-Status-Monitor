import os
import tempfile
import logging
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from pypdf import PdfReader, PdfWriter
from pypdf._page import PageObject

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
SAMPLE_REPORT_PDF = os.path.join(ASSETS_DIR, "sample_report.pdf")
OUTPUT_PDF = "platform_status_report.pdf"

IST = ZoneInfo("Asia/Kolkata")


def _plain_text(value) -> str:
    return escape(str(value), quote=False)


def _format_ms(value) -> str:
    if value is None:
        return "N/A"
    return f"{value} ms"


def _build_body_pdf(
    results: List[dict],
    body_pdf_path: str,
    total_checked: int | None = None,
    failure_count: int | None = None,
) -> None:
    """
    Build a simple content-only PDF with appropriate margins to avoid footer/header.
    """
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ErrorText",
        parent=styles["Code"],
        fontSize=8,
        leading=10,
        textColor=colors.red,
    ))

    doc = SimpleDocTemplate(
        body_pdf_path,
        pagesize=LETTER,
        leftMargin=inch * 0.75,
        rightMargin=inch * 0.75,
        topMargin=inch * 1.5,
        bottomMargin=inch * 1.2
    )
    now_ist = datetime.now(IST)
    story = [
        Paragraph(
            f"Platform Status Report – {now_ist:%Y-%m-%d %H:%M:%S} IST",
            styles["Title"]
        ),
        Spacer(1, 12),
    ]

    if total_checked is not None:
        failures = failure_count if failure_count is not None else len(results)
        healthy = total_checked - failures
        story.extend([
            Paragraph(f"<b>Total checked:</b> {total_checked}", styles["Normal"]),
            Paragraph(f"<b>Healthy:</b> {healthy}", styles["Normal"]),
            Paragraph(f"<b>Failed:</b> {failures}", styles["Normal"]),
            Spacer(1, 12),
        ])

    for rec in results:
        display_name = _plain_text(rec.get("name", "Unknown"))
        url = _plain_text(rec["url"])
        status = _plain_text(rec["status"])
        status_code = rec.get("status_code")
        status_code_text = "N/A" if status_code is None else str(status_code)
        response_time = _plain_text(_format_ms(rec.get("response_time_ms")))
        attempts = _plain_text(rec.get("attempts", "N/A"))
        story.append(Paragraph(f"<b>Platform:</b> {display_name}", styles["Normal"]))
        story.append(Paragraph(f"<b>URL:</b> {url}", styles["Normal"]))
        story.append(Paragraph(f"<b>Status:</b> {status}", styles["Normal"]))
        story.append(Paragraph(f"<b>Status code:</b> {status_code_text}", styles["Normal"]))
        story.append(Paragraph(f"<b>Response time:</b> {response_time}", styles["Normal"]))
        story.append(Paragraph(f"<b>Attempts:</b> {attempts}", styles["Normal"]))
        if rec.get("error"):
            story.append(Paragraph("<b>Error:</b>", styles["Normal"]))
            story.append(Paragraph(_plain_text(rec["error"]), styles["ErrorText"]))
        story.append(Spacer(1, 18))

    doc.build(story)
    logging.info("Report PDF created.")


def _merge_with_sample_report(body_pdf_path: str, output_pdf_path: str) -> None:
    sample_report_pdf = PdfReader(SAMPLE_REPORT_PDF)
    body_pdf = PdfReader(body_pdf_path)
    writer = PdfWriter()

    sample_report_page = sample_report_pdf.pages[0]

    for body_page in body_pdf.pages:
        merged_page = PageObject.create_blank_page(
            width=sample_report_page.mediabox.width,
            height=sample_report_page.mediabox.height,
        )
        merged_page.merge_page(sample_report_page)
        merged_page.merge_page(body_page)

        writer.add_page(merged_page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)


def generate_pdf_report(
    results: List[dict],
    outfile: str = OUTPUT_PDF,
    total_checked: int | None = None,
    failure_count: int | None = None,
) -> None:
    """
    Generates the platform status report PDF by composing body content and
    merging it onto the sample_report template.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        body_pdf_path = os.path.join(tmpdir, "body.pdf")
        _build_body_pdf(
            results,
            body_pdf_path,
            total_checked=total_checked,
            failure_count=failure_count,
        )
        _merge_with_sample_report(body_pdf_path, outfile)
