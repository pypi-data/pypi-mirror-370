import json
from datetime import datetime

import wtforms
from wtforms.validators import ValidationError


READONLY = {"readonly": True}
DISABLED = {"disabled": True}
AUTOFOCUS = {"autofocus": True}
AUTOCOMPLETE_NEW_PASSWORD = {"autocomplete": "new-password"}


# Followings are for compatibility.
StringField = wtforms.StringField
TextAreaField = wtforms.TextAreaField
IntegerField = wtforms.IntegerField


class HiddenJsonField(wtforms.HiddenField):
    def _value(self):
        return self.data and json.dumps(self.data)

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = json.loads(valuelist[0])


class HiddenIntegerField(wtforms.IntegerField):
    widget = wtforms.widgets.HiddenInput()

    def _value(self):
        if self.data is not None:
            return str(self.data)
        return ""


class DatePickerField(wtforms.StringField):
    date_format = "%Y-%m-%d"

    def __init__(self, *args, date_format=None, **kwargs):
        super().__init__(*args, **kwargs)

        if date_format:
            self.date_format = date_format

    def _value(self):
        return self.data and self.data.strftime(self.date_format) or ""

    def process_formdata(self, valuelist):
        self.data = None
        if valuelist:
            try:
                if valuelist[0]:
                    self.data = datetime.strptime(valuelist[0], self.date_format).date()
            except Exception:
                raise ValueError("Not a valid date format.")


class DateTimePickerField(wtforms.StringField):
    datetime_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, *args, datetime_format=None, **kwargs):
        super().__init__(*args, **kwargs)

        if datetime_format:
            self.datetime_format = datetime_format

    def _value(self):
        return self.data and self.data.strftime(self.datetime_format) or ""

    def process_formdata(self, valuelist):
        self.data = None
        if valuelist:
            try:
                if valuelist[0]:
                    self.data = datetime.strptime(valuelist[0], self.datetime_format)
            except Exception:
                raise ValidationError("Not a valid datetime format.")


class AjaxSelectField(wtforms.SelectField):
    def __init__(self, *args, data_url=None, data_params=None, **kwargs):
        self.data_url = data_url
        self.data_params = data_params
        kwargs.setdefault("choices", [])
        super().__init__(*args, **kwargs)

    def pre_validate(self, form):
        if not self.flags.required and self.data:
            super().pre_validate(form)


class AjaxSelectMultipleField(wtforms.SelectMultipleField):
    def __init__(self, *args, data_url=None, data_params=None, **kwargs):
        self.data_url = data_url
        self.data_params = data_params
        kwargs.setdefault("choices", [])
        super().__init__(*args, **kwargs)

    def pre_validate(self, form):
        if not self.flags.required and self.data:
            super().pre_validate(form)


class CommaSeparatedField(StringField):
    def __init__(self, *args, separated_validators=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.separated_validators = separated_validators or []

    def _value(self):
        if isinstance(self.data, str):
            return self.data
        return ", ".join(self.data) if self.data else ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [i.strip() for i in valuelist[0].split(",")]
        else:
            self.data = []

    def post_validate(self, form, validation_stopped):
        if not validation_stopped:
            data = self.data
            try:
                for validator in self.separated_validators:
                    for i in data:
                        self.data = i
                        validator(None, self)

            finally:
                self.data = data
