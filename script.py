import csv
import logging
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

logging.basicConfig(
    format="%(levelname)s:%(asctime)s:%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]
SERVER_PORT = os.environ["SERVER_PORT"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


def get_email_number_map(csv_path) -> dict:
    logger.info(f"Creating email_number_map from {csv_path} file.")
    email_number_map = {}
    with open(file=csv_path, encoding="utf-8") as csvfile:
        email_reader = csv.reader(csvfile)
        for row in email_reader:
            email_s = row[2].split()
            email_number_map.update({email: row[0] for email in email_s})
    return email_number_map


def find_photos_paths(number: str, basepath: str) -> list:
    logger.info(f"Finding photos for number: {number}, in {basepath} directory.")
    delimiter_position = len(number)
    delimiters = [".", "_"]
    return [
        filename
        for filename in os.listdir(basepath)
        if filename.startswith(number) and filename[delimiter_position] in delimiters
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
        filename = attachment_filepath.split("/")[-1]
        with open(attachment_filepath, "rb") as fp:
            logger.info(f"Adding attachment: {filename} to the message.")
            msg.add_attachment(
                fp.read(),
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )
    return msg


def send_message(message):
    logger.info(f"Sending message to {message['To']}.")
    context = ssl.create_default_context()
    with smtplib.SMTP(SERVER_ADDRESS, SERVER_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
    logger.info(f"Message to {message['To']} sent!")


def main(csv_path: str, basepath: str):
    email_number_map = get_email_number_map(csv_path=csv_path)
    for email, number in email_number_map.items():
        full_paths = [
            os.path.join(basepath, photo_path)
            for photo_path in find_photos_paths(number=number, basepath=basepath)
        ]
        if not full_paths:  # in case there is no file for the number
            continue
        email_message = prepare_message(
            recipient_email=email, attachment_filepaths=full_paths
        )
        send_message(message=email_message)


if __name__ == "__main__":
    main(
        csv_path="22032022.csv",
        basepath="/mnt/d/Marcin/Pictures/zdjecia-do-dokumentow/20220322",
    )
