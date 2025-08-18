import time

from authlib.jose import JsonWebSignature
from authlib.jose.errors import BadSignatureError, ExpiredTokenError
from flask import current_app


TOKEN_ALGORITHM = "HS512"
try:
    from authlib.jose import JWS_ALGORITHMS
except ImportError:
    JWS_ALGORITHMS = [TOKEN_ALGORITHM]


class _SerializerState:
    def __init__(self, key, expires_in):
        self._key = key
        self._expires_in = expires_in
        self._serializer = JsonWebSignature(JWS_ALGORITHMS)
        self._serializer.REGISTERED_HEADER_PARAMETER_NAMES = frozenset(list(
            self._serializer.REGISTERED_HEADER_PARAMETER_NAMES) + ["iat", "exp"])

    def loads(self, token):
        jws = self._serializer.deserialize_compact(token, self._key)

        try:
            if (exp := int(jws["header"].get("exp"))) < 0:
                raise ValueError

        except Exception:
            raise BadSignatureError("Invalid expiry date.")

        if exp < self.now():
            raise ExpiredTokenError

        return jws["payload"].decode()

    def dumps(self, raw):
        now = self.now()
        return self._serializer.serialize_compact(dict(
            alg=TOKEN_ALGORITHM, iat=now, exp=now + self._expires_in), raw, self._key).decode()

    def now(self):
        return int(time.time())


class JWTSerializer:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        state = _SerializerState(
            app.config["SECRET_KEY"],
            app.config.setdefault("SOUTHERNCROSS_JWT_TOKEN_EXPIRES", 86400))

        app.extensions["jwt_serializer"] = state

        return state


def _get_serializer():
    if serializer := current_app.extensions.get("jwt_serializer"):
        return serializer

    raise RuntimeError(
        "The JWT Serializer extension was not registered to the current application.")


def loads(token):
    return _get_serializer().loads(token)


def dumps(raw):
    return _get_serializer().dumps(raw)
