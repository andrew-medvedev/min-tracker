__date__ = '20.10.2014'
__author__ = {
    'name': 'a.medvedev',
}

import random
import hashlib
import binascii
import utils
import constants


tokens_l = {}  # Словарь токенов логин->обертка токена
tokens_t = {}  # Словарь токенов токен->обертка токена
token_seed = 0  # Некоторая фигня, которая будет гарантировать, что при генерации токена на вход хеш функции не попадут
                # одинаковые значения


class TokenWrapper:
    def __init__(self, login, token):
        self.login = login
        self.token = token
        self.last_act_ts = utils.timestamp()


def insert_new_token(login, new_token):
    """
    Функция отвечает за заведение нового объекта токена в словаре tokens.
    Пока будет использоваться питонская хеш-таблица, но потом планируется вставить дерево
    и протестировать быстродействие.
    """
    global tokens_l, tokens_t

    if login in tokens_l:
        wrapper = tokens_l[login]
        wrapper.token = new_token
        wrapper.last_act_ts = utils.timestamp()
    else:
        wrapper = TokenWrapper(login, new_token)
        tokens_l[login] = wrapper
        tokens_t[new_token] = wrapper


def return_token(token):
    """
    Ищем и удаляем токен
    :return True - если токен найден и удален, False - в противном случае
    """
    global tokens_l, tokens_t

    if token in tokens_t:
        login = tokens_t[token].login
        del tokens_t[token]
        del tokens_l[login]
        return True
    else:
        return False


def step_tokens():
    """
    Служебный метод, который пробегается по всем токенам, ищет устаревшие и удаляет
    """
    global tokens_l

    for k in tokens_l:
        wrapper = tokens_l[k]
        if utils.timestamp() - wrapper.last_act_ts > constants.TOKEN_MAX_TIME_IDLE:
            tok = wrapper.token
            del tokens_l[k]
            del tokens_t[tok]


def generate_token():
    global token_seed

    timestamp = str(utils.timestamp()).encode('utf-8')
    tseed = str(token_seed).encode('utf-8')
    token_seed += 1

    hasher = get_hasher()
    hasher.update(timestamp)
    hasher.update(tseed)

    return str(binascii.hexlify(bytearray(hasher.digest())), 'ascii')


def generate_r_salt():
    out = bytearray()
    for i in range(constants.SALT_LENGTH):
        out.append(random.randint(0, 255))
    return out


def compare_password(password, pass_hash, salt):
    hasher = get_hasher()
    hasher.update(password.encode('utf-8'))
    hasher.update(salt)
    pass_check = hasher.digest()

    # Быстрое сравнение байтовых массивов(меньше питона)
    return pass_check in pass_hash and len(pass_check) == len(pass_hash)


def hash_password(password, salt):
    hasher = get_hasher()
    hasher.update(password.encode('utf-8'))
    hasher.update(salt)

    return hasher.digest()


def get_hasher():
    """
    Геттер для хеш-функции - пока используется алгоритм ша-1
    :return: SHA-1 Algorithm OpenSSL implementation
    """
    return hashlib.sha1()