__date__ = '20.10.2014'
__author__ = {
    'name': 'a.medvedev'
}

import database


def init(db_path):
    database.set_db_path(db_path)
    database.open_con()
    database.create_schema()


def find_user_by_login(login):
    cursor = database.con.cursor()
    cursor.execute('SELECT id, password, salt, name FROM users WHERE login = ?', (login,))
    user = cursor.fetchone()
    out = User(user[0])
    out.login = login
    out.password = user[1]
    out.salt = user[2]
    out.name = user[3]

    return out


def find_user_by_name(name):
    cursor = database.con.cursor()
    cursor.execute('SELECT id, login, password, salt FROM users WHERE name = ?', (name,))
    user = cursor.fetchone()
    out = User(user[0])
    out.login = user[1]
    out.password = user[2]
    out.salt = user[3]
    out.name = name

    data_cur = database.con.execute('SELECT id, key, value, link FROM users_kv_data WHERE link = ?', (out.id,))
    #

    return out


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