import os
import json
from collections import defaultdict

from flask import current_app

from .default_dictionary import default_dictionary


class _TranslatorState:
    def __init__(self, dictionary, default_locale="en"):
        self._dictionary = {lang: {k.lower(): v for k, v in value.items()}
                            for lang, value in dictionary.items()}
        self._default_locale = default_locale

    def get_languages(self):
        return self._dictionary.keys()

    def gettext(self, message, **kwargs):
        ret = self._dictionary.get(
            self.locale_selector() or self._default_locale, {"i18n": "English"}).get(
            message.lower().strip(), message)
        return ret if len(kwargs) == 0 else ret % kwargs

    def ngettext(self, singular, plural, num, **kwargs):
        if num > 1:
            return self.gettext(plural, **kwargs)
        return self.gettext(singular, **kwargs)

    def merge(self, dictionary):
        for k, v in dictionary.items():
            if k in self._dictionary:
                dictionary = self._dictionary[k]
                for source, destination in v.items():
                    if (current := dictionary.get(source)) and current != destination:
                        current_app.logger.warning(
                            "Dictionary data for '%s' is changed from '%s' to '%s'." % (
                                source, current, destination))
                    dictionary[source] = destination
            else:
                self._dictionary[k] = v


class Translator:
    def __init__(self, app=None):
        self.app = app
        self._locale_selector = self._state = None
        if app is not None:
            self._state = self.init_app(app)

    def init_app(self, app):
        dictionary = defaultdict(dict)

        app.config.setdefault("SOUTHERNCROSS_I18N_DEFAULT_LOCALE", "en")

        if app.config.setdefault("SOUTHERNCROSS_I18N_ENABLE_DEFAULT", True):
            dictionary.update(default_dictionary)

        if loc_dir := app.config.get("SOUTHERNCROSS_I18N_DICTIONARY_DIR"):
            for i in os.listdir(loc_dir):
                if i.endswith(".json"):
                    with open(os.path.join(loc_dir, i)) as fp:
                        dictionary[i[:-5]] |= json.loads(fp.read())

        else:
            app.config.setdefault("SOUTHERNCROSS_I18N_DICTIONARY_FILE",
                                  os.path.join(app.root_path, "dictionary.json"))

            with open(app.config["SOUTHERNCROSS_I18N_DICTIONARY_FILE"]) as fp:
                for lang, data in json.loads(fp.read()).items():
                    dictionary[lang] |= data

        state = _TranslatorState(dictionary, app.config["SOUTHERNCROSS_I18N_DEFAULT_LOCALE"])

        if self._locale_selector is not None:
            state.locale_selector = self._locale_selector

        app.extensions["translator"] = self._state = state

        app.jinja_env.add_extension("jinja2.ext.i18n")
        app.jinja_env.install_gettext_callables(
            state.gettext, state.ngettext, newstyle=True)

        return state

    def locale_selector(self, func):
        self._locale_selector = func
        if self._state is not None:
            self._state.locale_selector = func
        return func

    def get_languages(self):
        return self._state.get_languages()

    def __getattr__(self, name):
        return getattr(self._state, name, None)


def _get_state():
    if translator := current_app.extensions.get("translator"):
        return translator
    raise RuntimeError("The translator extension was not registered to the "
                       "current application.")


def gettext(message, **kwargs):
    return _get_state().gettext(message, **kwargs)


def ngettext(singular, plural, num, **kwargs):
    return _get_state().ngettext(singular, plural, num, **kwargs)


def get_languages():
    return _get_state().get_languages()
