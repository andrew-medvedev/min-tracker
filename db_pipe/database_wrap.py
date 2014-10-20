__date__ = '20.10.2014'
__author__ = {
    'name': 'a.medvedev'
}

import database


def init(db_path):
    database.set_db_path(db_path)
    database.open_con()
    database.create_schema()


class User:
    def __init__(self, _id):
        self._id = _id
        self.login = None
        self.password = None
        self.salt = None
        self.name = None
        self.data = None


class KVData:
    def __init__(self, _id):
        self._id = _id
        self.key = None
        self.value = None
        self.link = None


class Project:
    def __init__(self, _id):
        self._id = _id
        self.name = None
        self.description = None
        self.status = None
        self.parent = None
        self.data = None


class UserRole:
    def __init__(self, _id):
        self._id = _id
        self.user = None
        self.project = None
        self.name = None
        self.type = None


class Task:
    def __init__(self, _id):
        self._id = _id
        self.type = None
        self.name = None
        self.description = None
        self.status = None
        self.author_role = None
        self.performer_role = None
        self.created_ts = None
        self.last_updated_ts = None
        self.closed_ts = None
        self.time = None
        self.ready = None
        self.project = None
        self.parent = None