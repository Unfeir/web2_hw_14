from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import AuthToken
from src.conf.config import settings

auth = AuthToken()
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="NoteBook",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
    The function takes in three arguments:
    -email: The user's email address, which is used as the recipient of the message.
    -username: The username of the user, which is used in constructing a personalized greeting for them.
    -host: The hostname that will be included in the confirmation link sent to them.

    :param email: EmailStr: Specify the type of email address that is expected
    :param username: str: Display the username in the email
    :param host: str: Pass the hostname of the server to be used in the email
    :return: A coroutine
    :doc-author: Trelent
    """
    try:
        token_verification = await auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def pass_reset_email(email: EmailStr, username: str, host: str):
    """
    The pass_reset_email function sends an email to the user with a link to reset their password.
    The function takes in three arguments:
    - email: the user's email address, which is used as a unique identifier for that user.
    - username: the username of the account associated with this email address. This is used in
    conjunction with host (see below) to create a URL that will be sent via an HTML template
    (reset_password_template.html). This URL will direct users back to our website where they can reset their password.

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Personalize the email
    :param host: str: Pass the host of the website
    :return: A value of type nonetype
    :doc-author: Trelent
    """
    try:
        token_verification = await auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_template.html")
    except ConnectionErrors as err:
        print(err)
