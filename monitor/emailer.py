import os, smtplib, logging
from email.message import EmailMessage
from typing import List


def send_email(subject: str, body: str, attachments: List[str], smtp: dict):
    msg = EmailMessage()
    msg["From"] = smtp["user"]
    msg["To"] = ", ".join(smtp["to"])
    msg["Subject"] = subject
    msg.set_content(body)

    for path in attachments:
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application",
                               subtype="pdf", filename=os.path.basename(path))

    with smtplib.SMTP(smtp["host"], smtp["port"]) as server:
        server.starttls()
        server.login(smtp["user"], smtp["password"])
        server.send_message(msg)
    logging.info("Alert e-mail sent to %s", ", ".join(smtp["to"]))
