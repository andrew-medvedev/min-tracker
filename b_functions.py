__author__ = 'a.medvedev'

import database
import auth
import utils


def register_new_user(login, password, name, data):
    # 1 - Проверить, нет ли пользователя с таким же логином
    # 2 - Родить рандомную соль (10 байт)
    # 3 - Захешировать пароль с применением рандомной соли
    # 4 - Начать транзакцию
    # 5 - Сохранить запись пользователя и получить ID
    # 6 - Сохранить записи users_kv_data из массива data
    # 7 - Закоммитить транзакцию
    # 8 - Вернуть (True, None)

    if database.count_users_by_login(login) > 0:
        return False, 'Login already exists'
    else:
        salt = auth.generate_r_salt()
        pass_h = auth.hash_password(password, salt)
        if database.add_user_with_data(login, pass_h, salt, name, data):
            return True, None
        else:
            return False, 'Internal error'


def login(login, password):
    # 1 - Проверить, есть ли пользователь с таким логином
    # 2 - Выполнить подтверждение пароля
    # 3 - Если не ок, то возвращаем (False, 'Invalid login and/or password')
    # 4 - Генерируем новый токен
    # 5 - Ищем по дереву(словарю) токенов имеющийся токен по данному логину
    # 6 - Заменяем или создаем новый токен и помещаем в дерево(словарь)
    # 7 - Возвращаем пользователю рожденный токен
    # TODO Надо получить доступ над циклом исполнения в Торнадо, что бы направить этот поток на служебные цели:
    # Проверка времени жизни токенов: если токены долго бездействуют - удаляем

    user = database.find_user_by_login(login)
    if user is None:
        return False, 'Invalid login and/or password'
    else:
        if auth.compare_password(password, user.password, user.salt):
            new_token = auth.generate_token()
            auth.insert_new_token(login, new_token)
            return True, new_token
        else:
            return False, 'Invalid login and/or password'


def logout(user_token):
    # 1 - Проверяем, есть ли в дереве(словаре) такой токен
    # 2 - Если есть - удаляем и возвращаем (True, None)
    # 3 - Если нет - возвращаем (False, 'Didn't find such token')

    if auth.return_token(user_token):
        return True, None
    else:
        return False, 'Didn\'t find such token'


def get_user_info(user_token, name):
    # 1 - Проверяем, есть ли такой user_token в дереве(словаре) токенов
    # 2 - Если нет, то возвращаем (False, 'No permissions')
    # 3 - Если есть, то обнавляем timestamp последней активности токена
    # 4 - Делаем выборку из базы данных на данный name
    # 5 - Если ничего нет - возвращаем (False, 'No such user')
    # 6 - Если есть - делаем выборку соответствующих users_kv_data
    # 7 - Если запрос прошел без ошибок - возвращаем все данные
    # 8 - Если нет - возвращаем (False, Internal Error)

    if user_token in auth.tokens_t:
        token_wrapper = auth.tokens_t[user_token]
        token_wrapper.last_act_ts = utils.timestamp()
    else:
        return False, 'No permissions'


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