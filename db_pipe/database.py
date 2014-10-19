__author__ = 'a.medvedev'

import sqlite3 as sqlite
import logging as log


db_path = 'data.db'
con = None


def open_con():
    global con, db_path
    try:
        con = sqlite.connect(db_path)
    except:
        pass


def set_db_path(database_path):
    global db_path
    db_path = database_path


def create_schema():
    try:
        open(db_path)
    except FileNotFoundError:
        if con is not None:
            add_users = """
                    CREATE TABLE users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        login VARCHAR(100) NOT NULL,
                        password BLOB NOT NULL,
                        salt BLOB NOT NULL,
                        name VARCHAR(50) NOT NULL
                    );
                    """
            add_users_kv_data = """
                    CREATE TABLE users_kv_data(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        key VARCHAR(50) NOT NULL,
                        value VARCHAR(255) NOT NULL,
                        link INTEGER NOT NULL,
                        FOREIGN KEY(link) REFERENCES users(id)
                    );
                    """
            add_projects = """
                    CREATE TABLE projects(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description VARCHAR(255) NOT NULL,
                        status VARCHAR(6) NOT NULL DEFAULT 'open',
                        parent_id INTEGER DEFAULT NULL,
                        FOREIGN KEY(parent_id) REFERENCES projects(id)
                    );
                    """
            add_projects_kv_data = """
                    CREATE TABLE projects_kv_data(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        key VARCHAR(50) NOT NULL,
                        value VARCHAR(255) NOT NULL,
                        link INTEGER NOT NULL,
                        FOREIGN KEY(link) REFERENCES projects(id)
                    );
                    """
            add_user_roles = """
                    CREATE TABLE user_roles(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER NOT NULL,
                        project_id INTEGER NOT NULL,
                        role_name VARCHAR(100) NOT NULL,
                        role_type VARCHAR(4) NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(project_id) REFERENCES projects(id)
                    );
                    """
            add_tasks = """
                    CREATE TABLE tasks(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        task_type VARCHAR(6) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description VARCHAR(255) NOT NULL,
                        task_status VARCHAR(6) NOT NULL DEFAULT 'new',
                        author_role_id INTEGER NOT NULL,
                        performer_role_id INTEGER NOT NULL,
                        created_ts INTEGER NOT NULL,
                        last_updated_ts INTEGER NOT NULL,
                        closed_ts INTEGER NOT NULL,
                        time INTEGER NOT NULL,
                        ready INTEGER NOT NULL,
                        project_id INTEGER NOT NULL,
                        parent_id INTEGER DEFAULT NULL,
                        FOREIGN KEY(author_role_id) REFERENCES user_roles(id),
                        FOREIGN KEY(performer_role_id) REFERENCES user_roles(id),
                        FOREIGN KEY(project_id) REFERENCES projects(id),
                        FOREIGN KEY(parent_id) REFERENCES tasks(id)
                    );
                    """
            con.execute(add_users + add_users_kv_data + add_projects + add_projects_kv_data + add_user_roles + add_tasks)


def add_user(login, password, salt, name):
    cursor = con.cursor()
    try:
        cursor.execute('INSERT INTO users(login, password, salt, name) VALUES(?, ?, ?, ?)',
                      (login, password, salt, name))
    except sqlite.Error as e:
        log.error('add_user : {}'.format(e))
        return None
    return cursor.lastrowid


def add_users_kv_data(keys_ar, values_ar, links_ar):
    out = []
    cursor = con.cursor()
    i = 0
    while i < len(keys_ar):
        i += 1
        try:
            cursor.execute('INSERT INTO users_kv_data(key, value, link) VALUES(?, ?, ?)',
                           (keys_ar[i], values_ar[i], links_ar[i]))
        except sqlite.Error as e:
            log.error('add_users_kv_data : {}'.format(e))
            return None
        out.append(cursor.lastrowid)
    return out


def add_project(name, description, status, parent_id):
    cursor = con.cursor()
    try:
        cursor.execute('INSERT INTO projects(name, description, status, parent_id) VALUES(?, ?, ?, ?)',
                      (name, description, status, parent_id))
    except sqlite.Error as e:
        log.error('add_project : {}'.format(e))
        return None
    return cursor.lastrowid


def add_projects_kv_data(keys_ar, values_ar, links_ar):
    out = []
    cursor = con.cursor()
    i = 0
    while i < len(keys_ar):
        i += 1
        try:
            cursor.execute('INSERT INTO projects_kv_data(key, value, link) VALUES(?, ?, ?)',
                           (keys_ar[i], values_ar[i], links_ar[i]))
        except sqlite.Error as e:
            log.error('add_projects_kv_data : {}'.format(e))
            return None
        out.append(cursor.lastrowid)
    return out


def add_user_role(user_id, project_id, role_name, role_type):
    cursor = con.cursor()
    try:
        cursor.execute('INSERT INTO user_roles(user_id, project_id, role_name, role_type) VALUES(?, ?, ?, ?)',
                      (user_id, project_id, role_name, role_type))
    except sqlite.Error as e:
        log.error('add_user_role : {}'.format(e))
        return None
    return cursor.lastrowid


def add_task(task_type, name, description, task_status, author_role_id, performer_role_id, created_ts, last_updated_ts,
             closed_ts, time, ready, project_id, parent_id):
    cursor = con.cursor()
    stmt = """
    INSERT INTO tasks(
        task_type,
        name,
        description,
        task_status,
        author_role_id,
        performer_role_id,
        created_ts,
        last_updated_ts,
        closed_ts,
        time,
        ready,
        project_id,
        parent_id
    ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.execute(stmt, (
                       task_type,
                       name,
                       description,
                       task_status,
                       author_role_id,
                       performer_role_id,
                       created_ts,
                       last_updated_ts,
                       closed_ts,
                       time,
                       ready,
                       project_id,
                       parent_id))
    except sqlite.Error as e:
        log.error('add_task : {}'.format(e))
        return None
    return cursor.lastrowid


if __name__ == '__main__':
    open_con()
    create_schema()