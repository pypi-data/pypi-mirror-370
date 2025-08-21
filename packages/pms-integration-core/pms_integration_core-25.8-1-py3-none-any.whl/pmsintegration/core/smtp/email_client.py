import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from pmsintegration.core.app import AppContext


def send_email(
        subject: str,
        body: str,
        content_type: str = "html",
        attachments: Optional[dict[str, bytes]] = None
):
    try:
        app_ctx = AppContext.global_context()

        email_config = app_ctx.smtp.get_config
        get_emailid = app_ctx.env.get_required("app.smtp_email")
        SMTP_SERVER = email_config.smtp_server
        SMTP_PORT = email_config.smtp_port
        SMTP_USER = email_config.smtp_user
        SMTP_PASSWORD = email_config.smtp_password
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = get_emailid
        # msg["Cc"] = get_emailid
        msg["Subject"] = subject

        msg.attach(MIMEText(body, content_type))

        # Attach files
        if attachments:
            for filename, file_bytes in attachments.items():
                part = MIMEApplication(file_bytes, Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully to {get_emailid}")

    except Exception as e:
        print("Failed to send email:", str(e))
