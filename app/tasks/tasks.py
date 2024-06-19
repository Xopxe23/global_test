import smtplib

from app.config import settings
from app.tasks.celery_app import celery
from app.tasks.email_templates import create_email_verification_template


@celery.task
def sent_verification_email(
        email_to: str,
        code: str,
        action: str
):
    email_to = email_to
    msg_content = create_email_verification_template(email_to, code, action)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    return f'Code {code} has been sent successfully on {email_to}'
