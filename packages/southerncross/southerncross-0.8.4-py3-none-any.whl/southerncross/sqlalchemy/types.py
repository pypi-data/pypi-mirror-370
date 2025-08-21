import re
import json
import sqlite3

from sqlalchemy import String as _String, event, TypeDecorator, Text, Integer
from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import BinaryExpression, literal
from sqlalchemy.dialects.mysql import LONGTEXT


class JSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXT)
        return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        return None if value is None else json.dumps(value, separators=[",", ":"])

    def process_result_value(self, value, dialect):
        return None if value is None else json.loads(value)


class EnumType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        return None if value is None else self.enum_class[value].value

    def process_result_value(self, value, dialect):
        return None if value is None else self.enum_class(value).name


try:
    from bfx_aes_cipher import encrypt, decrypt

    class EncryptedText(TypeDecorator):
        impl = Text
        cache_ok = True

        def load_dialect_impl(self, dialect):
            if dialect.name == "mysql":
                return dialect.type_descriptor(LONGTEXT)
            return dialect.type_descriptor(Text)

        def process_bind_param(self, value, dialect):
            return encrypt(value)

        def process_result_value(self, value, dialect):
            return decrypt(value)

    class EncryptedJSON(TypeDecorator):
        impl = EncryptedText
        cache_ok = True

        def process_bind_param(self, value, dialect):
            return None if value is None else json.dumps(value)

        def process_result_value(self, value, dialect):
            return None if value is None else json.loads(value)

except ImportError:
    pass


class RegexpBinaryExpression(BinaryExpression):
    inherit_cache = True


class String(_String):
    class comparator_factory(_String.comparator_factory):
        def regexp(self, other):
            return RegexpBinaryExpression(self.expr, literal(other), "regexp")


@compiles(RegexpBinaryExpression, "sqlite")
@compiles(RegexpBinaryExpression, "mysql")
def mysql_regex_match(element, compiler, **kw):
    return " ".join([
        compiler.process(element.left), "REGEXP", compiler.process(element.right)])


@compiles(RegexpBinaryExpression, "postgresql")
def postgres_regex_match(element, compiler, **kw):
    return " ".join([
        compiler.process(element.left), "~", compiler.process(element.right)])


@event.listens_for(Engine, "connect")
def sqlite_engine_connect(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_function(
            "REGEXP", 2, lambda regex, value: bool(re.search(regex, value)))
