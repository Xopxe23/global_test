from email.message import EmailMessage

from app.config import settings


def create_email_verification_template(
        email_to: str,
        code: str,
        action: str
) -> EmailMessage:
    email_message = EmailMessage()
    email_message["Subject"] = "Email Verification"
    email_message["From"] = settings.SMTP_USER
    email_message["To"] = email_to
    email_message.set_content(
        f'''
            <h1>Code for {action}</h1>
            <p>Please ENTER your CODE:</p>
            <h1>{code}</h1>
        ''',
        subtype="html"
    )
    return email_message
