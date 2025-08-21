__version__ = "0.8.4"


try:
    import urllib3

    # Show following warning only once.
    urllib3.warnings.simplefilter("default", urllib3.exceptions.SecurityWarning)

except ImportError:
    pass


try:
    import wtforms

    def _patched_process_string_formdata(self, valuelist):
        if valuelist and (self.flags.required or valuelist[0]):
            self.data = valuelist[0].strip() or None

    wtforms.StringField.process_formdata = _patched_process_string_formdata

    def _patched_process_textarea_formdata(self, valuelist):
        if valuelist and (self.flags.required or valuelist[0]):
            self.data = valuelist[0]

    wtforms.TextAreaField.process_formdata = _patched_process_string_formdata

    _original_process_integer_formdata = wtforms.IntegerField.process_formdata

    def _patched_process_integer_formdata(self, valuelist):
        if valuelist and (self.flags.required or valuelist[0]):
            _original_process_integer_formdata(self, valuelist)

    wtforms.IntegerField.process_formdata = _patched_process_integer_formdata


except ImportError:
    pass
