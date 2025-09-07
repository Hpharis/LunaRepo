import os
from typing import Dict
import requests


def post_to_wordpress(url: str, username: str, password: str, content: str) -> None:
    data = {
        "title": "Automated Post",
        "content": content,
        "status": "publish",
    }
    response = requests.post(url, json=data, auth=(username, password))
    response.raise_for_status()
    print("Posted to WordPress")


def send_email(host: str, user: str, password: str, to_addr: str, subject: str, body: str) -> None:
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP_SSL(host) as server:
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())
    print("Email sent")
