import traceback

from flask import current_app
from flask_mail import Message


def send_mail(cc=None, **kwargs):
    current_app.extensions["mail"].send(Message(
        cc=cc or current_app.config.get("MAIL_DEFAULT_CC"), **kwargs))


def send_exception_mail(**kwargs):
    try:
        send_mail(body=traceback.format_exc(), **kwargs)
    except Exception:
        current_app.logger.exception("Failed to send exception mail.")
