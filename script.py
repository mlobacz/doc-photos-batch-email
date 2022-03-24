import csv
import logging
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]
SERVER_PORT = os.environ["SERVER_PORT"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


def get_email_number_map(csv_path) -> dict:
    logging.info(f"Creating email_number_map from {csv_path} file.")
    email_number_map = {}
    with open(file=csv_path, encoding="utf-8") as csvfile:
        email_reader = csv.reader(csvfile)
        for row in email_reader:
            email_s = row[2].split()
            email_number_map.update({email: row[0] for email in email_s})
    return email_number_map


def find_photos_paths(number: str, basepath: str) -> list:
    logging.info(f"Finding photos for number: {number}, in {basepath} directory.")
    return [
        filename for filename in os.listdir(basepath) if filename.startswith(number)
    ]


def prepare_message(recipient_email: str, attachment_filepaths: str) -> EmailMessage:
    logger.info(f"Preparing message from: {EMAIL_ADDRESS} to {recipient_email}.")
    msg = EmailMessage()
    msg["Subject"] = "Zdjecia do dokumentow"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    for attachment_filepath in attachment_filepaths:
        ctype, encoding = mimetypes.guess_type(attachment_filepath)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(attachment_filepath, "rb") as fp:
            logger.info(f"Adding attachment: {attachment_filepath} to the message.")
            msg.add_attachment(
                fp.read(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment_filepath,
            )
    return msg


def send_message(message):
    logging.info(f"Sending message to {message['To']}.")
    context = ssl.create_default_context()
    with smtplib.SMTP(SERVER_ADDRESS, SERVER_PORT) as smtp:
        smtp.ehlo()  # Say EHLO to server
        smtp.starttls(context=context)  # Puts the connection in TLS mode.
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)


def main():
    email_number_map = get_email_number_map(csv_path="22032022.csv")
    for email, number in email_number_map.items():
        photos_paths = find_photos_paths(number=number, basepath=".")
        email_message = prepare_message(
            recipient_email=email, attachment_filepaths=photos_paths
        )
        send_message(message=email_message)
