import logging
from logging import INFO, DEBUG

from swc_utils.exceptions.package_exceptions import MissingDependencyError

try:
    from flask_sqlalchemy.model import Model
except ImportError:
    raise MissingDependencyError("Flask-SQLAlchemy")

try:
    from sqlalchemy import Engine, text, MetaData
    from sqlalchemy.ext.declarative import declarative_base as _declarative_base
    from sqlalchemy.orm import sessionmaker
except ImportError:
    raise MissingDependencyError("SQLAlchemy")


class DBCareEngine:
    """
    Class responsible for handling database tables and columns.
    Can be used to check for missing columns, extra columns, and run custom tasks.
    """
    def __init__(self, db_engine: Engine, declarative_base: Model = None, flask_app=None):
        """
        :param db_engine: SQLAlchemy engine
        :param declarative_base: SQLAlchemy declarative base
        :param flask_app: Flask app instance
        """
        self.base = declarative_base or _declarative_base()
        self.engine = db_engine
        self.__flask_app = flask_app

    def __enter__(self):
        self.session = sessionmaker(bind=self.engine)()
        self.connection = self.engine.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        self.session.close()
        return False

    def _log(self, message, level=INFO):
        if self.__flask_app:
            self.__flask_app.logger.log(level, message)
        else:
            logging.log(level, message)

    def find_models(self) -> list:
        """
        Find all models that are subclasses of the base model.
        :return: List of models
        """
        models = list()

        def find_subclasses(cls):
            for subclass in cls.__subclasses__():
                find_subclasses(subclass)
                models.append(subclass)

        find_subclasses(self.base)
        return models

    def find_tables(self) -> dict:
        """
        Find all tables in the database.
        :return: Dictionary of tables
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return metadata.tables

    def _check_table_column_exists(self, table_name, column_name):
        sql = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{column_name}'"
        return self.connection.execute(text(sql)).scalar() > 0

    def _fix_missing_columns(self, model, missing_columns):
        for column in missing_columns:
            if self._check_table_column_exists(model.__tablename__, column):
                self._log(f"Column '{column}' already exists in '{model.__tablename__}'. Skipping...", DEBUG)
                continue

            column = model.__table__.columns.get(column)

            column_definition = f'{column.name} {column.type.compile(dialect=self.engine.dialect)}'
            alter_table_sql = f'ALTER TABLE {model.__tablename__} ADD COLUMN {column_definition}'
            self.connection.execute(text(alter_table_sql))

            self._log(f"Column '{column.name}' added to '{model.__tablename__}'")

    def _fix_extra_columns(self, model, extra_columns):
        for column in extra_columns:
            result = self._check_table_column_exists(model.__tablename__, column) and self.connection.execute(text(
                f"SELECT COUNT(*) FROM {model.__tablename__} WHERE {column} IS NOT NULL"
            )).scalar()

            if result > 0:
                self._log(f"Column '{column}' in '{model.__tablename__}' contains data and will not be dropped", DEBUG)
                continue

            self.connection.execute(text(
                f"ALTER TABLE {model.__tablename__} DROP COLUMN {column}"
            ))

            self._log(f"Column '{column}' dropped from '{model.__tablename__}'")

    def treat_tables(self):
        """
        Check for missing columns and extra columns in the database tables.
        :return: None
        """
        all_models = self.find_models()
        all_tables = self.find_tables()

        for model in all_models:
            if not hasattr(model, "__tablename__"):
                self._log(f"Table '{model.__name__}' has no name. Might be abstract. Skipping...", DEBUG)
                continue
            elif model.__tablename__ not in all_tables:
                self._log(f"Table '{model.__tablename__}' not found in database. Skipping...", DEBUG)
                continue

            table = all_tables.get(model.__tablename__)
            model_columns = model.__table__.columns.keys()
            existing_columns = table.columns.keys()

            missing_columns = set(model_columns) - set(existing_columns)
            extra_columns = set(existing_columns) - set(model_columns)

            self._log(f"Missing columns for '{model.__tablename__}': {missing_columns}", DEBUG)
            self._log(f"Extra columns for '{model.__tablename__}': {extra_columns}", DEBUG)

            if missing_columns:
                self._fix_missing_columns(model, missing_columns)

            if extra_columns:
                self._fix_extra_columns(model, extra_columns)

    def run_custom_task(self, task: callable):
        self._log(f"Running custom task '{task.__name__}'...")
        task(self)

