import os, smtplib, logging
from email.message import EmailMessage
from typing import List
from .config import SMTP

def send_email(subject: str, body: str, attachments: List[str]):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = SMTP["user"], SMTP["to"], subject
    msg.set_content(body)

    for path in attachments:
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application",
                               subtype="pdf", filename=os.path.basename(path))

    with smtplib.SMTP(SMTP["host"], SMTP["port"]) as server:
        server.starttls()
        server.login(SMTP["user"], SMTP["password"])
        server.send_message(msg)
    logging.info("Alert e-mail sent to %s", SMTP["to"])
