from contextlib import suppress

import sqlalchemy
from sqlalchemy.exc import DatabaseError
from flask import g, request
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy


_original_escaped_like_impl = sqlalchemy.sql.operators._escaped_like_impl


def _sa_url_set(url, **kwargs):
    try:
        url = url.set(**kwargs)
    except AttributeError:
        for key, value in kwargs.items():
            setattr(url, key, value)

    return url


class SQLAlchemy(_SQLAlchemy):
    def apply_driver_hacks(self, app, sa_url, options):
        # This is only for flask_sqlalchemy < 3.
        # This function name is changed to _apply_driver_defaults,
        # and charset is set to utf8mb4 as default in flask_sqlalchemy >= 3.
        if sa_url.drivername.startswith("mysql"):
            query = dict(sa_url.query)
            query.setdefault("charset", "utf8mb4")
            sa_url = _sa_url_set(sa_url, query=query)

        return super().apply_driver_hacks(app, sa_url, options)

    def init_app(self, app):
        # Add some default values to silence warnings.
        app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
        app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///")
        app.config.setdefault("SQLALCHEMY_RECORD_QUERIES", False)
        app.config.setdefault("SQLALCHEMY_PREPING", True)
        app.config.setdefault("SQLALCHEMY_AUTOESCAPE", True)

        super().init_app(app)

        # Add before_request to send ping against database.
        @app.before_request
        def _preset_database_ping():
            g.db = self

            if app.config["SQLALCHEMY_PREPING"] and (
                    request.endpoint and request.endpoint != "static"):
                with suppress(DatabaseError):
                    # Use engine directly to avoid auto begin.
                    self.engine.execute(sqlalchemy.select(1))

        if not app.config["SQLALCHEMY_AUTOESCAPE"]:
            sqlalchemy.sql.operators._escaped_like_impl = _original_escaped_like_impl

        elif sqlalchemy.sql.operators._escaped_like_impl == _original_escaped_like_impl:
            def _escaped_like_impl(fn, other, escape, autoescape):
                if escape is None:
                    escape = "/"
                    other = other.replace(escape, escape + escape).replace(
                        "%", escape + "%").replace("_", escape + "_")

                return fn(other, escape=escape)

            sqlalchemy.sql.operators._escaped_like_impl = _escaped_like_impl
