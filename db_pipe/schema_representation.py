__author__ = 'a.medvedev'


_users = [
    {
        'column': 'id',
        'type': 'long',
        'is_pk': True
    }, {
        'column': 'login',
        'type': 'string',
        'length': 100
    }, {
       'column': 'password',
       'type': 'bytearray'
    }, {
        'column': 'salt',
        'type': 'bytearray'
    }, {
        'column': 'name',
        'type': 'string',
        'length': 50
    }
]


_kv_data = [
    {
        'column': 'id',
        'type': 'long',
        'is_pk': True
    }, {
        'column': 'key',
        'type': 'string',
        'length': 50
    }, {
        'column': 'value',
        'type': 'string',
        'length': 255
    }, {
        'column': 'link',
        'type': 'long',
        'is_fk': True
    }
]


_projects = [
    {
        'column': 'id',
        'type': 'long',
        'is_pk': True
    }, {
        'column': 'name',
        'type': 'string',
        'length': 100
    }, {
        'column': 'description',
        'type': 'string',
        'length': 255
    }, {
        'column': 'status',
        'type': 'enum',
        'enum_ref': 'project_status',
    }, {
        'column': 'parent_id',
        'type': 'long',
        'is_fk': True
    }
]


_user_roles = [
    {
        'column': 'id',
        'type': 'long',
        'is_pk': True
    }, {
        'column': 'user_id',
        'type': 'long',
        'is_fk': True
    }, {
        'column': 'project_id',
        'type': 'long',
        'is_fk': True
    }, {
        'column': 'role_name',
        'type': 'string',
        'length': 100
    }, {
        'column': 'role_type',
        'type': 'enum',
        'enum_ref': 'user_role_type'
    }
]


_tasks = [
    {
        'column': 'id',
        'type': 'long',
        'is_pk': True
    }, {
        'column': 'type',
        'type': 'enum',
        'enum_ref': 'task_type'
    }, {
        'column': 'name',
        'type': 'string',
        'length': 100
    }, {
        'column': 'description',
        'type': 'string',
        'length': 255
    }, {
        'column': 'status',
        'type': 'enum',
        'enum_ref': 'task_status'
    }, {
        'column': 'author_id',
        'type': 'long',
        'is_fk': True
    }, {
        'column': 'performer_id',
        'type': 'long',
        'is_fk': True
    }, {
        'column': 'created_ts',
        'type': 'timestamp'
    }, {
        'column': 'last_updated_ts',
        'type': 'timestamp'
    }, {
        'column': 'closed_ts',
        'type': 'timestamp'
    }, {
        'column': 'time',
        'type': 'int'
    }, {
        'column': 'ready',
        'type': 'byte'
    }, {
        'column': 'project_id',
        'type': 'long',
        'is_fk': True
    }, {
        'column': 'parent_id',
        'type': 'long',
        'if_fk': True
    }
]


def get_schema():
    return {
        'table': 'users',
        'columns': _users
    }, {
        'table': 'kv_data',
        'columns': _kv_data
    }, {
        'table': 'projects',
        'columns': _projects
    }, {
        'table': 'user_roles',
        'columns': _user_roles
    }, {
        'table': 'tasks',
        'columns': _tasks
    }