import json
from datetime import datetime, date, time
from uuid import UUID

from flask import current_app, Flask as _Flask, jsonify
from flask.json.provider import JSONProvider as _JSONProvider


def created(response, location):
    return jsonify(response), 201, {"Location": location}


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is date:
            return obj.strftime(current_app.config["SOUTHERNCROSS_JSON_DATE_FORMAT"])
        elif type(obj) is datetime:
            return obj.strftime(current_app.config["SOUTHERNCROSS_JSON_DATETIME_FORMAT"])
        elif type(obj) is time:
            return obj.strftime(current_app.config["SOUTHERNCROSS_JSON_TIME_FORMAT"])
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode()
        return list(obj)


class JSONProvider(_JSONProvider):
    def dumps(self, obj, **kwargs):
        kwargs["separators"] = (",", ":")
        return JSONEncoder(**kwargs).encode(obj)

    def loads(self, s, **kwargs):
        if type(s) is bytes:
            s = s.decode()
        return json.loads(s.replace("\\u0000", ""), **kwargs)


class Flask(_Flask):
    json_provider_class = JSONProvider
