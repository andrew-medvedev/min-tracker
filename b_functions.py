__author__ = 'a.medvedev'


def register_new_user(login, password, name, data):
    pass


def login(login, password):
    pass


def logout(user_token):
    pass


def count_projects(user_token):
    pass


def projects_listing(user_token, only_mine, with_status):
    pass


def find_project(user_token, by_id):
    pass


def add_member(user_token, member_id, project_id, role, description):
    pass


def remove_member(user_token, member_id, project_id, description):
    pass


def change_member_role(user_token, member_id, project_id, new_role, description):
    pass


def add_project(user_token, project_name, data):
    pass


def add_project_hierarchy(user_token, parent_project_id, child_project_id):
    pass


def remove_project_hierarchy(user_token, parent_project_id, child_project_id):
    pass


def edit_project(user_token, project_id, status, data):
    pass


def count_project_tasks(user_token, project_id):
    pass


def list_project_tasks(user_token, project_id, from_, count):
    pass


def find_task(user_token, task_id):
    pass


def edit_task(user_token, task_id, name, description, time, ready, parent_id):
    pass


def change_task_status(user_token, task_id, status, description):
    pass