from wtforms.validators import ValidationError

from ..validators import CrontabValidator


class Crontab:
    def __init__(self, message=None):
        self.message = message or CrontabValidator.error_message

    def __call__(self, form, field):
        if not field.data:
            return

        try:
            CrontabValidator().validate(field.data)
        except Exception:
            raise ValidationError(self.message)
