# syntaxmatrix/emailer.py
import os
import smtplib
from email.message import EmailMessage

def send_email(to: str, subject: str, body: str):
    backend = os.getenv("EMAIL_BACKEND", "console").lower()
    if backend == "smtp":
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER")
        passwd = os.getenv("SMTP_PASS")
        sender = os.getenv("SMTP_FROM")
        if not all([host, port, sender]):
            raise RuntimeError("SMTP_HOST/PORT/FROM must be set for SMTP")
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        msg.set_content(body)
        with smtplib.SMTP(host, port) as smtp:
            if user and passwd:
                smtp.login(user, passwd)
            smtp.send_message(msg)
    else:
        print(f"\n--- EMAIL to {to} ({subject}) ---\n{body}\n")
