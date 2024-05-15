# Author: Sakthi Santhosh
# Created on: 15/05/2024
from csv import DictReader
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from requests import get
from smtplib import SMTP
from os import getenv

from dotenv import load_dotenv

ENDPOINT_DNS_NAME = "vpn.sakthisanthosh.in"
CONFIG_TEMPLATE = None
DATE_TODAY = str(date.today())


class Recipient:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs["name"]
        self.email = kwargs["email"]
        self.priv_key = kwargs["priv_key"]
        self.client_ipv4 = kwargs["client_ipv4"]

        self.config = self._generate_client_conf()

    def _generate_client_conf(self) -> BytesIO:
        recipient_config = CONFIG_TEMPLATE%(
           self.priv_key,
           self.client_ipv4,
           ENDPOINT_DNS_NAME
        )

        return BytesIO(recipient_config.encode("utf-8"))


def load_config_template() -> str:
    try:
        with open("./assets/config_template.conf", 'r') as conf_file_handle:
            return conf_file_handle.read()
    except FileNotFoundError:
        print("Fatal: Unable to load config template, terminating application.")
        exit(1)


def load_recipients() -> list[Recipient]:
    recipients = []

    with open("./assets/recipients.csv", newline='') as csvfile:
        reader = DictReader(csvfile)

        for row in reader:
            priv_key = getenv("PYTHONWGES_PRIVKEY_" + row["email"].split('@')[0])

            if priv_key is None:
                raise TypeError(f"Private key is not set for the peer '{row['email']}'.")

            recipient = Recipient(
                **row,
                priv_key=priv_key,
            )
            recipients.append(recipient)

    return recipients


def send_email(sender_email: str, recipients: list[Recipient], subject: str) -> None:
    try:
        with open("./assets/body.txt", 'r') as file:
            body = file.read()
    except FileNotFoundError:
        print("Error: Body file not found. Defaulting to standard body.")
        body = ''

    msg = MIMEMultipart()
    msg["From"] = f"Sakthi Santhosh <{sender_email}>"
    msg["To"] = ','.join([f"{recipient.name} <{recipient.email}>" for recipient in recipients])
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    for recipient in recipients:
        attachment_filename = f"{recipient.email.split('@')[0]}.conf"
        attachment_part = MIMEApplication(
            recipient.config.getvalue(),
            Name=attachment_filename
        )

        attachment_part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_filename}"'
        )

        msg.attach(attachment_part)

    msg_as_string = msg.as_string()
    server = SMTP("smtp.gmail.com", 587)

    server.starttls()
    server.login(sender_email, getenv("PYTHONWGES_SMTP_PASSWORD"))
    server.sendmail(sender_email, [recipient.email for recipient in recipients], msg_as_string)
    print(msg_as_string)
    server.quit()


if __name__ == "__main__":
    load_dotenv("./assets/.env")

    CONFIG_TEMPLATE = load_config_template()

    send_email(
        "sakthisanthosh010303@gmail.com",
        load_recipients(),
        "VPN Configuration for " + DATE_TODAY
    )
