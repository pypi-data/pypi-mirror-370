import os
import json
from functools import wraps
from collections import defaultdict

from flask import current_app, request
from jsonschema import Draft4Validator, FormatChecker
from jsonschema import ValidationError      # noqa


class _JSONSchemaState:
    def __init__(self, schema):
        self._format_checker = FormatChecker()
        self._schema = defaultdict(dict)
        [setattr(self, i, {}) for i in ["_definitions", "_schema_source"]]
        self.merge(schema)

    @property
    def format_checker(self):
        return self._format_checker

    def get_validator(self, target):
        return self._schema[target][request.method.lower()]

    def _gen_validator(self, schema):
        schema["definitions"] = self._definitions
        return Draft4Validator(schema, format_checker=self._format_checker)

    def merge(self, schema):
        self._definitions.update(schema.get("definitions", {}))
        self._schema_source.update(schema)

        [self._schema[key].update({i: self._gen_validator(j) for i, j in target.items()})
         for key, target in self._schema_source.items() if key != "definitions"]


class JSONSchema:
    def __init__(self, app=None):
        self.app = app
        self._state = None if app is None else self.init_app(app)

    def _merge(self, app, filename, state):
        with open(filename) as fp:
            data = fp.read()
            if jsi := app.config.get("SOUTHERNCROSS_JSON_SCHEMA_INTERPOLATION"):
                data = data % jsi
            state.merge(json.loads(data))

    def init_app(self, app):
        state = _JSONSchemaState({})
        if js_dir := app.config.get("SOUTHERNCROSS_JSON_SCHEMA_DIR"):
            [self._merge(app, os.path.join(js_dir, i), state)
             for i in os.listdir(js_dir) if i.endswith(".json")]

        else:
            app.config.setdefault("SOUTHERNCROSS_JSON_SCHEMA_FILE", os.path.join(
                app.root_path, "jsonschema.json"))
            self._merge(app, app.config["SOUTHERNCROSS_JSON_SCHEMA_FILE"], state)

        self._state = app.extensions["jsonschema"] = state
        return state

    def checks(self, format, exception):
        if self._state is None:
            raise RuntimeError("The JsonSchema extension is not initialized yet.")

        def _wrapper(func):
            func = self._state.format_checker.checks(format, exception)(func)
        return _wrapper

    def set_definitions(self, definitions):
        if self._state is None:
            raise RuntimeError("The JsonSchema extension is not initialized yet.")

        self._state._definitions.update(definitions)
        self._state.merge({})


def validate(target):
    def _wrapper(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            if not (js := current_app.extensions.get("jsonschema")):
                raise RuntimeError("The JSON schema extension was not registered to the "
                                   "current application.")
            js.get_validator(target).validate(request.get_json())

            return func(*args, **kwargs)
        return _inner
    return _wrapper
