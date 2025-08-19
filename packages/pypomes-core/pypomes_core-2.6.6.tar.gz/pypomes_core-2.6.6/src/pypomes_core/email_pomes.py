import sys
from email.message import EmailMessage
from enum import StrEnum
from logging import Logger
from smtplib import SMTP

from .file_pomes import Mimetype
from .env_pomes import APP_PREFIX, env_get_str


class EmailConfig(StrEnum):
    """
    Parameters for email.
    """
    HOST = env_get_str(key=f"{APP_PREFIX}_EMAIL_HOST",
                       def_value="")
    PORT = env_get_str(key=f"{APP_PREFIX}_EMAIL_PORT",
                       def_value="")
    ACCOUNT = env_get_str(key=f"{APP_PREFIX}_EMAIL_ACCOUNT",
                          def_value="")
    PWD = env_get_str(key=f"{APP_PREFIX}_EMAIL_PWD",
                      def_value="")
    SECURITY = env_get_str(key=f"{APP_PREFIX}_EMAIL_SECURITY",
                           def_value="")


def email_send(errors: list[str] | None,
               user_email: str,
               subject: str,
               content: str,
               content_type: Mimetype = Mimetype.TEXT,
               logger: Logger = None) -> None:
    """
    Send email to *user_email*, with *subject* as the email subject, and *content* as the email message.

    :param errors: incidental error messages
    :param user_email: the address to send the email to
    :param subject: the email subject
    :param content: the email message
    :param content_type: the mimetype of the content (defaults to *text/plain*)
    :param logger: optional logger
    """
    # import needed function
    from .obj_pomes import exc_format

    # build the email object
    email_msg = EmailMessage()
    email_msg["From"] = EmailConfig.ACCOUNT
    email_msg["To"] = user_email
    email_msg["Subject"] = subject
    if content_type == Mimetype.HTML:
        email_msg.set_content("Your browser does not support HTML.")
        email_msg.add_alternative(content,
                                  subtype="html")
    else:
        email_msg.set_content(content)

    # send the message
    try:
        # instantiate the email server, login and send the email
        with SMTP(host=EmailConfig.HOST,
                  port=int(EmailConfig.PORT)) as server:
            if EmailConfig.SECURITY == "tls":
                server.starttls()
            server.login(user=EmailConfig.ACCOUNT,
                         password=EmailConfig.PWD)
            server.send_message(msg=email_msg)
            if logger:
                logger.debug(msg=f"Sent email '{subject}' to '{user_email}'")
    except Exception as e:
        # the operatin raised an exception
        exc_err: str = exc_format(exc=e,
                                  exc_info=sys.exc_info())
        err_msg: str = f"Error sending the email: {exc_err}"
        if logger:
            logger.error(msg=err_msg)
        if isinstance(errors, list):
            errors.append(err_msg)


def email_codify(email: str) -> str:
    """
    Codify *email* so as to provide a hint at its content, whilst preventing its usage.

    The codification process changes my_mail@my_server.com into m*****l@m********.com.

    :param email: the email to codify
    :return: the codified email
    """
    # initialize the return variable
    result: str = email

    pos1: int = email.rfind("@")
    pos2: int = email.rfind(".")
    if pos2 > pos1 > 0:
        result = email[0] + "*" * (pos1 - 2) + \
                 email[pos1 - 1:pos1 + 2] + "*" * (pos2 - pos1 - 2) + email[pos2:]

    return result
