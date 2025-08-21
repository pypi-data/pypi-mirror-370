import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

from pydantic import Field
from tools_vars import EMAIL_TOOL

# Import the Rich logger instead of configuring a basic logger
from codemie.logging import logger
from codemie.toolkit import RemoteInput, RemoteTool


class EmailToolInput(RemoteInput):
    recipient_emails: list[str] = Field(None, description="A list of recipient email addresses")
    subject: str = Field(None, description="The email subject")
    body: str = Field(None, description="The body of the email")

class EmailTool(RemoteTool):
    name: str = EMAIL_TOOL.name
    args_schema: Type[RemoteInput] = EmailToolInput
    description: str = EMAIL_TOOL.description
    smtp_port: int = int(os.getenv('SMTP_PORT', 587))
    smtp_server: str = str(os.getenv('SMTP_SERVER', 'smtp.office365.com'))
    smtp_user: str = str(os.getenv('SMTP_USER'))
    smtp_password: str = str(os.getenv('SMTP_PASSWORD'))

    def _run(self, recipient_emails: str, subject: str, body: str, *args, **kwargs) -> str:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = ", ".join(recipient_emails)

            part = MIMEText(body, 'html')
            msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, recipient_emails, msg.as_string())
                server.quit()

            logger.info(f"Email sent to {recipient_emails}")
            return "Email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_emails}: {e}")
            return f"Failed to send email: {e}"
