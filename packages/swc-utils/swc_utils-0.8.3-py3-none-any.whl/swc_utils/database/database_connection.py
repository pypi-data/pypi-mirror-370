from ..exceptions.package_exceptions import MissingDependencyError

try:
    from flask import Flask
except ImportError:
    raise MissingDependencyError("Flask")

from .connection_profile import ConnectionProfile


def connect_to_database(app: Flask, conn: ConnectionProfile, extra_db: dict[str, ConnectionProfile] = None):
    """
    Connect to the database using the connection profile
    :param app: Flask app instance
    :param conn: ConnectionProfile instance
    :param extra_db: Extra database connection profiles
    :return:
    """
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = conn.connection_uri

    if extra_db is not None:
        for key, value in extra_db.items():
            extra_db[key] = value.connection_uri

        app.config['SQLALCHEMY_BINDS'] = extra_db
