import os
import io
import json
import sqlite3
import unittest
from contextlib import suppress

from requests import Response
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


with suppress(ImportError):
    import freezegun

    freezegun.configure(extend_ignore_list=["southerncross"])


class TestCase(unittest.TestCase):
    def init_app(self, app, db=None):
        app.config.update(
            TESTING=True,
            SECRET_KEY=os.urandom(24),
            WTF_CSRF_ENABLED=False)

        if db:
            with app.app_context():
                self.dbsession = scoped_session(sessionmaker(bind=db.engine))
            self.addCleanup(self.dbsession.remove)

        self.client = app.test_client()

    def create_http_response(self, content=b"", status_code=200, headers=None):
        res = Response()

        if type(content) is str:
            content = content.encode()
        elif type(content) in (dict, list):
            content = json.dumps(content).encode()

        res._content = content
        res.raw = io.BytesIO(content)
        res.status_code = status_code
        res.headers = headers or {}
        return res

    def assert_no_content(self, res):
        self.assertEqual(204, res.status_code)
        self.assertEqual(b"", res.data)

    def assert_empty_array(self, res):
        self.assertEqual(200, res.status_code)
        self.assertEqual(b"[]", res.data)

    def assert_redirection(self, res, url, status_code=302):
        self.assertEqual(status_code, res.status_code)
        self.assertEqual(url, res.location)

    def assert_flash_message(self, message, category):
        with self.client.session_transaction() as session:
            self.assertEqual((category, message), session["_flashes"].pop(0))
