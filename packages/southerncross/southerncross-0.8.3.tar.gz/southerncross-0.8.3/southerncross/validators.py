import re


_minute_re = re.compile(
    "(?P<all>\\*)|"
    "(?P<specific>[0-5]?\\d)|"
    "(?P<range>[0-5]?\\d-[0-5]?\\d)|"
    "(?P<list>[0-5]?\\d(,[0-5]?\\d)+)|"
    "(?P<step>(\\*|[0-5]?\\d)/(([0-5]?[1-9])|([1-5]0)))"
)

_hour_re = re.compile(
    "(?P<all>\\*)|"
    "(?P<specific>[01]?\\d|2[0-3])|"
    "(?P<range>([01]?\\d|2[0-3])-([01]?\\d|2[0-3]))|"
    "(?P<list>([01]?\\d|2[0-3])(,([01]?\\d|2[0-3]))+)|"
    "(?P<step>(\\*|[01]?\\d|2[0-3])/([01]?[1-9]|2[0-3]|10))"
)

_day_of_month_re = re.compile(
    "(?P<all>\\*)|"
    "(?P<specific>[1-2]?[1-9]|[1-3]0|31)|"
    "(?P<range>([1-2]?[1-9]|[1-3]0|31)-([1-2]?[1-9]|[1-3]0|31))|"
    "(?P<list>([1-2]?[1-9]|[1-3]0|31)(,([1-2]?[1-9]|[1-3]0|31))+)|"
    "(?P<step>(\\*|[1-2]?[1-9]|[1-3]0|31)/([1-2]?[1-9]|[1-3]0|31))"
)

_month_re = re.compile(
    "(?P<all>\\*)|"
    "(?P<specific>[1-9]|1[0-2])|"
    "(?P<range>([1-9]|1[0-2])-([1-9]|1[0-2]))|"
    "(?P<list>([1-9]|1[0-2])(,([1-9]|1[0-2]))+)|"
    "(?P<step>(\\*|[1-9]|1[0-2])/([1-9]|1[0-2]))"
)

_day_of_week_re = re.compile(
    "(?P<all>\\*)|"
    "(?P<specific>[0-6])|"
    "(?P<range>[0-6]-[0-6])|"
    "(?P<list>[0-6](,[0-6])+)|"
    "(?P<step>(\\*|[0-6])/[1-6])"
)

_regex_list = [_minute_re, _hour_re, _day_of_month_re, _month_re, _day_of_week_re]


_month_names = [
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
_month_names_re = re.compile(
    rf"(?<![\d\/])({'|'.join(_month_names)})(?!\d)", re.IGNORECASE)

_day_of_week_names = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
_day_of_week_names_re = re.compile(
    rf"(?<![\d\/])({'|'.join(_day_of_week_names)})(?!\d)", re.IGNORECASE)


class CrontabValidator:
    error_message = "Invalid crontab expression."

    def _replace_names(self, value):
        parts = value.split()
        if len(parts) > 3:
            parts[3] = re.sub(
                _month_names_re,
                lambda m: str(_month_names.index(m.group().lower()) + 1),
                parts[3])
        if len(parts) > 4:
            parts[4] = re.sub(
                _day_of_week_names_re,
                lambda m: str(_day_of_week_names.index(m.group().lower())),
                parts[4])
        return " ".join(parts)

    def validate(self, value):
        parts = self._replace_names(value).split()
        if len(parts) != 5:
            raise ValueError(self.error_message)

        for ind, pattern in enumerate(_regex_list):
            if not (match := pattern.fullmatch(parts[ind])):
                raise ValueError(self.error_message)

            if matched_range := match.groupdict()["range"]:
                min_value, max_value = matched_range.split("-")
                if int(min_value) > int(max_value):
                    raise ValueError(self.error_message)
