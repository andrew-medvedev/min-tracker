__date__ = '09.10.2014'
__author__ = {
    'name': 'a.medvedev',
}

LOGIN_MIN_LEN, LOGIN_MAX_LEN = 4, 30
PASSWORD_MIN_LEN, PASSWORD_MAX_LEN = 6, 50
NAME_MIN_LEN, NAME_MAX_LEN = 4, 30
LONG_MIN, LONG_MAX = 1, 9223372036854775807
ROLE_MIN_LEN, ROLE_MAX_LEN = 3, 4
STATUS_MIN_LEN, STATUS_MAX_LEN = 3, 6
VARCHAR_MAX_LEN = 255
TOKEN_LEN = 10

# TODO Ввести потом реальную длину токена в TOKEN_LEN

IPC_BUFFER_SIZE = 8196
IPC_NODE_MAX_IDLE_MS = 8000
IPC_TIME_TO_REPRESENT_MS = 1000
IPC_RECONNECT_RELOADING_MS = 10000