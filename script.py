import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
import csv
from dotenv import load_dotenv

load_dotenv()

SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]
SERVER_PORT = os.environ["SERVER_PORT"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


def get_recipient_email(path):
    email_number_map = {}
    with open(path) as csvfile:
        email_reader = csv.reader(csvfile)
        for row in email_reader:
            email_s = row[2].split()
            for email in email_s:
                email_number_map[email] = row[0]
    return email_number_map


    # return "marcin.lobaczewski@gmail.com"
email_number_map = get_recipient_email(path="22032022.csv")
print(email_number_map)

def prepare_message(email, attachment_filepath):
    msg = EmailMessage()
    msg["Subject"] = "Zdjecia do dokumentow"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    filepath = "doggles.jpg"

    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)

    with open(attachment_filepath, "rb") as fp:
        msg.add_attachment(
            fp.read(), maintype=maintype, subtype=subtype, filename=attachment_filepath
        )
    return msg

def send_message(message):
    context = ssl.create_default_context()
    with smtplib.SMTP(SERVER_ADDRESS, SERVER_PORT) as smtp:
        smtp.ehlo()  # Say EHLO to server
        smtp.starttls(context=context)  # Puts the connection in TLS mode.
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
