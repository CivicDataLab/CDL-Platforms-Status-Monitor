import os
import tempfile
import logging
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

# Paths (adjust if your layout differs)
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
SAMPLE_REPORT_PDF = os.path.join(ASSETS_DIR, "sample_report.pdf")
OUTPUT_PDF = "platform_status_report.pdf"

# Define IST timezone
IST = ZoneInfo("Asia/Kolkata")


def _build_body_pdf(results: List[dict], body_pdf_path: str) -> None:
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

    for rec in results:
        display_name = rec.get("name", "Unknown")
        story.append(Paragraph(f"<b>Platform:</b> {display_name}", styles["Normal"]))
        story.append(Paragraph(f"<b>URL:</b> {rec['url']}", styles["Normal"]))
        story.append(Paragraph(f"<b>Status:</b> {rec['status']}", styles["Normal"]))
        if rec.get("error"):
            story.append(Paragraph("<b>Error:</b>", styles["Normal"]))
            story.append(Paragraph(rec["error"], styles["ErrorText"]))
        story.append(Spacer(1, 18))

    doc.build(story)
    filename = os.path.basename(body_pdf_path)
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
        # Stamp sample_report background first
        merged_page.merge_page(sample_report_page)
        # Overlay body content on top
        merged_page.merge_page(body_page)

        writer.add_page(merged_page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)


def generate_pdf_report(results: List[dict], outfile: str = OUTPUT_PDF) -> None:
    """
    Generates the platform status report PDF by composing body content and
    merging it onto the sample_report template.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        body_pdf_path = os.path.join(tmpdir, "body.pdf")
        _build_body_pdf(results, body_pdf_path)
        _merge_with_sample_report(body_pdf_path, outfile)
