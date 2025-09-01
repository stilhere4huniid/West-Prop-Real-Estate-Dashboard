from dotenv import load_dotenv
import os
import csv
import smtplib
from email.message import EmailMessage

load_dotenv()

# --- CONFIGURE THESE ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")           # Your Gmail address
APP_PASSWORD = os.getenv("APP_PASSWORD")              # Gmail App Password (not your normal password)
SUBJECT = "WestProp: New Project Alert!"
BODY = """Hello,

Exciting news from WestProp! We have a new project launching soon. Stay tuned for details.

Best regards,
WestProp Team
"""

# --- READ SUBSCRIBERS ---
with open("email_alert_subscribers.csv", newline="") as f:
    reader = csv.reader(f)
    subscribers = [row[0] for row in reader if "@" in row[0]]

# --- SEND EMAIL TO EACH SUBSCRIBER ---
msg = EmailMessage()
msg["Subject"] = SUBJECT
msg["From"] = SENDER_EMAIL
msg.set_content(BODY)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(SENDER_EMAIL, APP_PASSWORD)
    for email in subscribers:
        msg["To"] = email
        smtp.send_message(msg)
        del msg["To"]  # Remove for next loop

print(f"Sent alert to {len(subscribers)} subscribers.")