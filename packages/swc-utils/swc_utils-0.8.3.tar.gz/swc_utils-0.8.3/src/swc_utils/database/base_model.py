import datetime
import json

from swc_utils.exceptions.package_exceptions import MissingDependencyError

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    raise MissingDependencyError("Flask-SQLAlchemy")

try:
    from sqlalchemy.orm.collections import InstrumentedList
    from werkzeug.datastructures.file_storage import FileStorage
except ImportError:
    raise MissingDependencyError("SQLAlchemy")


def make_base_model(db_engine: SQLAlchemy):
    class BaseModel(db_engine.Model):
        __abstract__ = True

        def add(self):
            db_engine.session.add(self)
            db_engine.session.commit()

        def commit(self):
            db_engine.session.commit()

        def delete(self):
            db_engine.session.delete(self)
            db_engine.session.commit()

        def update(self, **kwargs):
            for key, value in kwargs.items():
                if value is None:
                    continue
                if value == getattr(self, key):
                    continue
                if type(value) is FileStorage:
                    setattr(self, key, value.stream.read())
                else:
                    setattr(self, key, value)

            self.commit()
            return self

        def to_dict(self, show: list = None, to_json=True, parent_type=None):
            columns = self.__table__.columns.keys()
            relationships = self.__mapper__.relationships.keys()

            def is_jsonable(x):
                try:
                    json.dumps(x)
                    return True
                except (TypeError, OverflowError):
                    return False

            ret_data = {}

            for key in columns:
                if key.startswith("_") or key.startswith("__"):
                    continue
                if (not show) or key in show:
                    if type(getattr(self, key)) == datetime.datetime:
                        ret_data[key] = getattr(self, key).timestamp() * 1000
                        continue
                    if to_json and (not is_jsonable(getattr(self, key))):
                        continue
                    ret_data[key] = getattr(self, key)

            for key in relationships:
                if key.startswith("_") or key.startswith("__"):
                    continue
                if (not show) or key in show:
                    if type(getattr(self, key)) is InstrumentedList:
                        ret_data[key] = list(map(
                            lambda x: x.to_dict(show=show, to_json=to_json, parent_type=type(self)),
                            getattr(self, key)
                        ))
                    elif parent_type is not None and type(getattr(self, key)) is not parent_type:
                        ret_data[key] = getattr(self, key).to_dict(show=show, to_json=to_json)

            return ret_data

        def to_json(self, show: list = None):
            return self.to_dict(show=show)

    return BaseModel
