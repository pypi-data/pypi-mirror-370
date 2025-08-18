import os
import uuid
import smtplib
import threading
from email.mime.base import MIMEBase

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64


class SMTPClient:
    """
    SMTP Client for sending emails
    """
    def __init__(self, host: str, port: int, system_email: str = None, system_name: str = None, system_user: str = None,
                 system_password: str = None, ssl: bool = True, threaded: bool = True):
        """
        prepare a smtp client for sending emails using the given host and port with the given system mail and password
        :param host:
        :param port:
        :param system_email:
        :param system_name:
        :param system_user:
        :param system_password:
        :param ssl:
        :param threaded:
        """
        self._host = host
        self._port = port
        self._ssl = ssl
        self._system_email = system_email
        self._system_name = system_name
        self._system_user = system_user
        self._system_password = system_password
        self._threaded = threaded

    def _send(self, receivers: list[str], content: MIMEMultipart, sender_email):
        smtp_server = (self._host, self._port)
        smtp_credentials = (self._system_user, self._system_password)

        client = smtplib.SMTP_SSL if self._ssl else smtplib.SMTP

        with client(*smtp_server) as server_conn:
            server_conn.login(*smtp_credentials)
            server_conn.sendmail(
                sender_email, receivers, content.as_string()
            )

    @staticmethod
    def _attach(email_content, attachments):
        for attachment in attachments:
            if isinstance(attachment, str):
                mime = attachment.split(".").pop()
                filename = os.path.basename(attachment)
                with open(attachment, "rb") as fp:
                    data = fp.read()
            else:
                mime = "octet-stream"
                filename = str(uuid.uuid4())
                data = attachment

            attachment_part = MIMEBase("application", mime)
            attachment_part.set_payload(data)
            encode_base64(attachment_part)
            attachment_part.add_header("Content-Transfer-Encoding", "base64")
            attachment_part.add_header("Content-Disposition", "attachment", filename=filename)
            email_content.attach(attachment_part)

    def send(self, recipients: str or list[str], content: str or MIMEMultipart, subject: str = None,
             attachments: list[str or bytes] = None, as_html: bool = True, sender_email: str = None,
             sender_name: str = None):
        """
        email the given recipient with the given content and subject
        :param recipients: Recipient email address
        :param content: Email content
        :param subject: Email subject
        :param attachments: List of attachments (file paths or bytes)
        :param as_html: Send email as html
        :param sender_email: optional email address as sender
        :param sender_name: optional name of the sender
        :return:
        """
        if type(content) is str:
            email_content = MIMEMultipart("alternative")
            email_content.attach(MIMEText(content, "html" if as_html else "plain"))
        else:
            email_content = content

        recipients = recipients if isinstance(recipients, list) else [recipients]
        email = sender_email or self._system_email

        if email_content.get("Subject") is None and subject is not None:
            email_content["Subject"] = subject
        if email_content.get("From") is None:
            sender_name = sender_name or self._system_name
            email_content["From"] = f"{sender_name} <{email}>" if sender_name else email

        if attachments is not None:
            self._attach(email_content, attachments)

        if self._threaded:
            threading.Thread(target=self._send, args=(recipients, email_content, email,)).start()
        else:
            self._send(recipients, email_content, email)
