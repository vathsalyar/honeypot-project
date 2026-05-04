import os
import smtplib
import requests
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALERT_EMAIL      = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD   = os.getenv("EMAIL_PASSWORD")

def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ALERT] Telegram not configured, skipping.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }, timeout=5)
        print("[ALERT] Telegram message sent.")
    except Exception as e:
        print(f"[ALERT] Telegram failed: {e}")

def send_email(message: str):
    if not ALERT_EMAIL or not EMAIL_PASSWORD:
        print("[ALERT] Email not configured, skipping.")
        return
    try:
        msg = MIMEText(message)
        msg["Subject"] = "🚨 Honeypot Attack Detected"
        msg["From"]    = ALERT_EMAIL
        msg["To"]      = ALERT_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(ALERT_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("[ALERT] Email sent.")
    except Exception as e:
        print(f"[ALERT] Email failed: {e}")

def send_alert(message: str):
    print(f"[ALERT] {message}")
    send_telegram(message)
    send_email(message)
