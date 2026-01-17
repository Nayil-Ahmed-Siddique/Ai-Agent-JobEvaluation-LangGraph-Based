import os
import smtplib
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_report(
    evaluated_jobs: List[Dict[str, Any]],
    user_profile: Dict[str, Any]
):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = user_profile["email"]

    if not sender_email or not sender_password:
        print("Missing email credentials in .env")
        return

    if not evaluated_jobs:
        body = (
            "Hi,\n\n"
            "Your AI Job Agent ran successfully today.\n"
            "No suitable jobs were found based on your profile.\n\n"
            "— Your AI Job Agent"
        )
    else:
        lines = [
            "Hi,\n\nHere are the jobs your AI Job Agent recommends:\n\n"
        ]
        for job in evaluated_jobs:
            lines.append(
                f"- {job['title']} at {job['company']}\n"
                f"  Decision: {job['decision']}\n"
                f"  Reason: {job['reason']}\n"
                f"  Focus keywords: {', '.join(job.get('focus_keywords', []))}\n\n"
            )
        body = "".join(lines)

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Daily AI Job Agent Report"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print("Email sending failed:", e)
