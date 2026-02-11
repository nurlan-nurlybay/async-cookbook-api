import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from app.core.config import settings


class MailService:
    def __init__(self):
        self.server: Optional[smtplib.SMTP] = None

    def __enter__(self):
        # We cast to str/int because config validation guarantees existence
        self.server = smtplib.SMTP(str(settings.SMTP_HOST), int(settings.SMTP_PORT))
        self.server.starttls()
        self.server.login(str(settings.SMTP_USER), str(settings.SMTP_PASSWORD))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.server.quit()

    def _prepare_message(self, receiver: str, subject: str, body: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = str(settings.SMTP_USER)
        msg["To"] = receiver
        msg.attach(MIMEText(body, "plain"))
        return msg

    def send_single(self, receiver: str, subject: str, body: str):
        with self as mailer:
            msg = self._prepare_message(receiver, subject, body)
            # self.server is guaranteed not None by __enter__ logic, but linter is dumb
            if mailer.server:
                mailer.server.send_message(msg)

    def send_bulk(self, receivers: list[str], subject: str, body: str):
        if not self.server:
            raise RuntimeError("MailService must be used as a context manager.")

        for receiver in receivers:
            msg = self._prepare_message(receiver, subject, body)
            self.server.send_message(msg)
