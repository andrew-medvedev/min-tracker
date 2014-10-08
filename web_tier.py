__author__ = 'a.medvedev'

import re
import json
import logging
import utils
import tornado.web
import tornado.ioloop
import tornado.httputil
from tornado.web import asynchronous

LOGIN_MIN_LEN, LOGIN_MAX_LEN = 4, 30
PASSWORD_MIN_LEN, PASSWORD_MAX_LEN = 6, 50
NAME_MIN_LEN, NAME_MAX_LEN = 4, 30
ID_MIN_LEN, ID_MAX_LEN = 1, 19
ROLE_MIN_LEN, ROLE_MAX_LEN = 3, 4
STATUS_MIN_LEN, STATUS_MAX_LEN = 5, 10
VARCHAR_MAX_LEN = 255
TOKEN_LEN = 50

# TODO Ввести проверку по типам Json-тел
# TODO Ввести потом реальную длину токена в TOKEN_LEN

def init_web_tier(host, port):
    app = tornado.web.Application([
        (r'/api/regn', RegnH),
        (r'/api/login', LoginH),
        (r'/api/logout', LogoutH),
        (r'/api/projects/c', ProjectsCH),
        (r'/api/projects', ProjectsH),
        (r'/api/projects/f', ProjectsFH),
        (r'/api/memb/add', MembAddH),
        (r'/api/memb/rem', MembRemH),
        (r'/api/memb/chr', MembChrH),
        (r'/api/projects/add', ProjectsAddH),
        (r'/api/project/hie/add', ProjectsHieAddH),
        (r'/api/projects/hie/rem', ProjectsHieRemH),
        (r'/api/projects/edit', ProjectsEditH),
        (r'/api/tasks/c', TasksCH),
        (r'/api/tasks', TasksH),
        (r'/api/tasks/f', TasksFH),
        (r'/api/tasks/edit', TasksEditH),
        (r'/api/tasks/edit_s', TasksEditSH),
    ])
    try:
        app.listen(port, host)
    except Exception as e:
        logging.critical('At web_tier.init_web_tier :: {}'.format(e))
        return
    tornado.ioloop.IOLoop.instance().start()


class RegnH(tornado.web.RequestHandler):
    """
    -> Регистрация нового пользователя:
    Условия:
        логин должен являться email(будет проверяться по RegExp);
        проверка пароля на непустоту;
        проверка имени на латиницу + точка + ниж.подч.

    Запрос: @POST host/api/regn {
        "login": "example@gmail.com",
        "password": "123",
        "name": "v.pupkin",
        "data":{
            "fname": "vasiliy",
            "lname": "pupkin",
            "role": "Python Developer"
        }
    }

    Положительный ответ: {
        "ans": "ok",
        "nid": 321
    }
    Ответ с ошибкой: {
        "ans": "nok",
        "m": "Invalid name"
    }
    """

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.login = None
        self.password = None
        self.name = None
        self.data = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.RegnH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'login' in b:
            self.login = b['login']
            if len(self.login) < LOGIN_MIN_LEN or len(self.login) > LOGIN_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid login length : must be [{}, {}]'.format(LOGIN_MIN_LEN, LOGIN_MAX_LEN)
                return
            if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.login):
                self.is_valid = False
                self.error_m = 'Invalid login form: must be an email'
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no login'
            return

        if 'password' in b:
            self.password = b['password']
            if len(self.password) < PASSWORD_MIN_LEN or len(self.password) > PASSWORD_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid password length : must be [{}, {}]'.format(PASSWORD_MIN_LEN, PASSWORD_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no password'
            return

        if 'name' in b:
            self.name = b['name']
            if len(self.name) < NAME_MIN_LEN or len(self.name) > NAME_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid name length : must be [{}, {}]'.format(NAME_MIN_LEN, NAME_MAX_LEN)
                return
            if not utils.chlat_dot_etc(self.name):
                self.is_valid = False
                self.error_m = 'Invalid argument: name must be lat || dot || _'
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no password'
            return

        if 'data' in b:
            self.data = []
            for k in b['data']:
                if b['data'][k] is str:
                    self.data.append((k, b['data'][k]))
                elif b['data'][k] is int or b['data'][k] is float or b['data'][k] is bool:
                    self.data.append((k, str(b['data'][k])))
                else:
                    self.is_valid = False
                    self.error_m = 'Data format is invalid'
                    return


class LoginH(tornado.web.RequestHandler):
    """
    -> Логин:
    Условия:
        просто проверка полей на непустоту;

    Запрос: @POST host/api/login {
        "login": "example@gmail.com",
        "password": "123"
    }

    Положительный ответ: {
        "ans": "ok",
        "tok": "123abc"
    }
    Ответ с ошибкой: {
        "ans": "nok",
        "m": "Invalid login or password"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.login = None
        self.password = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.LoginH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'login' in b:
            self.login = b['login']
            if len(self.login) < LOGIN_MIN_LEN or len(self.login) > LOGIN_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid login length : must be [{}, {}]'.format(LOGIN_MIN_LEN, LOGIN_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no login'
            return

        if 'password' in b:
            self.password = b['password']
            if len(self.password) < PASSWORD_MIN_LEN or len(self.password) > PASSWORD_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid password length : must be [{}, {}]'.format(PASSWORD_MIN_LEN, PASSWORD_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no password'
            return


class LogoutH(tornado.web.RequestHandler):
    """
    -> Логаут:
    Условия:
        Проверка токена на размер и непустоту;

    Запрос @POST host/api/logout {
        "tok": "123abc"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Ответ с ошибкой: {
        "ans": "nok",
        "m": "Invalid token"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.tok = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.LogoutH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'tok' in b:
            self.tok = b['tok']
            if len(self.tok) != TOKEN_LEN:
                self.is_valid = False
                self.error_m = 'Invalid tok length : must be {}'.format(TOKEN_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no tok'
            return


class ProjectsCH(tornado.web.RequestHandler):
    """
    -> Получить количество всех корневых проектов:
    Условия:
        Нет проверок;

    Запрос: @GET host/api/projects/c

    Ответ: {
        "ans": "ok",
        "c": 14
    }
    """

    @asynchronous
    def get(self):
        #TODO Отправка аргументов + self в task_queue на исполнение
        pass


class ProjectsH(tornado.web.RequestHandler):
    """
    -> Листинг корневых проектов:
    Условия:
        проверка аргументов;
        проверка аргумента s на соответствие одному из 4 литералов;

    Запрос: @GET host/api/projects
    Аргументы:
        my=1 - Только те, в которых учавствую я;
        s=open / s=freeze / s=closed / s=fail - Фильтр по статусу(Открыт / Заморожен / Закрыт / Провален);

    Ответ: [{
        "id": 1,
        "name": "Проект 1",
        "desc": "Описание",
        "s": "open",
        "parent_id": 0,
        "children": [2, 3]
        }, {
        "id": 4,
        "name": "Проект 2",
        "desc": "Описание",
        "s": "freeze",
        "parent_id": 0,
        "children": []
    }]
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.my = None
        self.s = None

    @asynchronous
    def get(self):
        self.parse_query()
        #TODO Отправка аргументов + self в task_queue на исполнение

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'my' in q:
            self.my = q['my']
        if 's' in q:
            self.s = q['s']


class ProjectsFH(tornado.web.RequestHandler):
    """
    -> Получить проект:
    Условия:
        проверка аргумента byid на присутсвие числовых знаков;

    Запрос: @GET host/api/projects/f
    Аргументы:
        byid=3 - Сделать запрос по ID;

    Положительный ответ: {
        "ans": "ok",
        "f": {
        "id": 3,
        "name": "Супер-проект",
        "s": "open",
        "inf": {
            "sub": "way",
            "lol": "olo"
        }
        "memb":[{
            "id": 1,
            "name": "vasya",
            "role": "man"
            }, {
            "id": 2,
            "name": "john",
            "role": "perf"
        }],
        "parent_id": 4,
        "children": [5, 6]
        }
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "Empty"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.byid = None
        self.is_valid = True
        self.error_m = None

    @asynchronous
    def get(self):
        self.parse_query()
        if self.is_valid:
            pass
            #TODO Отправка аргументов + self в task_queue на исполнение
        else:
            self.write(r'"ans":"nok","m":{}'.format(self.error_m))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'byid' in q:
            self.byid = q['byid']
        else:
            self.is_valid = False
            self.error_m = 'Empty'


class MembAddH(tornado.web.RequestHandler):
    """
    -> Добавить участника в проект:
    Условия:
        проверка аргументов + IDшек на существование;
        проверка, является ли пользователь менеджером данного проекта;
        проверка, не является ли memb_id уже участником проекта;

    Запрос: @POST host/api/memb/add {
        "memb_id": 13,
        "proj_id": 37,
        "role": "perf",
        "desc": "Покачену"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.memb_id = None
        self.proj_id = None
        self.role = None
        self.desc = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.MembAddH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'memb_id' in b:
            self.memb_id = b['memb_id']
            if len(self.memb_id) < ID_MIN_LEN or len(self.memb_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid mem_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no memb_id'
            return

        if 'proj_id' in b:
            self.proj_id = b['proj_id']
            if len(self.proj_id) < ID_MIN_LEN or len(self.proj_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid proj_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no proj_id'
            return

        if 'role' in b:
            self.role = b['role']
            if len(self.role) < ROLE_MIN_LEN or len(self.role) > ROLE_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid role length : must be [{}, {}]'.format(ROLE_MIN_LEN, ROLE_MAX_LEN)
                return
            if self.role != 'man' and self.role != 'perf' and self.role != 'vis':
                self.is_valid = False
                self.error_m = r'Invalid role : must be "man", "perf" or "vis"'
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no role'
            return

        if 'desc' in b:
            self.desc = b['desc']
            if len(self.desc) < 1 or len(self.desc) > VARCHAR_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid desc length : must be [{}, {}]'.format(1, VARCHAR_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no desc'
            return


class MembRemH(tornado.web.RequestHandler):
    """
    -> Удалить участника из проекта(или удалиться самому):
    Условия:
        проверка аргументов + IDшек на существование;
        проверка на пренадлежность дан. пользователя к дан. проекту;
        проверка, является ли пользователь менеджером;
        если пользователь менеджер и IDшки совпадают, то проверка, не является ли он последним менеджером;

    Запрос: @POST host/api/memb/rem {
        "memb_id": 13,
        "proj_id": 37,
        "desc": "Ну нах"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.memb_id = None
        self.proj_id = None
        self.desc = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.MembRemH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'memb_id' in b:
            self.memb_id = b['memb_id']
            if len(self.memb_id) < ID_MIN_LEN or len(self.memb_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid mem_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no memb_id'
            return

        if 'proj_id' in b:
            self.proj_id = b['proj_id']
            if len(self.proj_id) < ID_MIN_LEN or len(self.proj_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid proj_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no proj_id'
            return

        if 'desc' in b:
            self.desc = b['desc']
            if len(self.desc) < 1 or len(self.desc) > VARCHAR_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid desc length : must be [{}, {}]'.format(1, VARCHAR_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no desc'
            return


class MembChrH(tornado.web.RequestHandler):
    """
    -> Изменить роль участника проекта:
    Условия:
        проверка аргументов + IDшек на существование;
        проверка на пренадлежность дан. пользователя к дан. проекту;
        проверка, является ли пользователь менеджером;
        если пользователь менеджер и IDшки совпадают, то проверка, не является ли он последним менеджером;
        проверка, не является ли пользователь уже данной ролью;

    Запрос: @POST host/api/memb/chr {
        "memb_id": 13,
        "proj_id": 37,
        "new_r": "man",
        "desc": "Повышение"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "This is user is not member of given project."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.memb_id = None
        self.proj_id = None
        self.new_r = None
        self.desc = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.MembChrH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'memb_id' in b:
            self.memb_id = b['memb_id']
            if len(self.memb_id) < ID_MIN_LEN or len(self.memb_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid mem_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no memb_id'
            return

        if 'proj_id' in b:
            self.proj_id = b['proj_id']
            if len(self.proj_id) < ID_MIN_LEN or len(self.proj_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid proj_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no proj_id'
            return

        if 'new_r' in b:
            self.new_r = b['new_r']
            if len(self.new_r) < ROLE_MIN_LEN or len(self.new_r) > ROLE_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid new_r length : must be [{}, {}]'.format(ROLE_MIN_LEN, ROLE_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no new_r'
            return

        if 'desc' in b:
            self.desc = b['desc']
            if len(self.desc) < 1 or len(self.desc) > VARCHAR_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid desc length : must be [{}, {}]'.format(1, VARCHAR_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no desc'
            return


class ProjectsAddH(tornado.web.RequestHandler):
    """
    -> Создать проект:
    Условия:
        проверка аргументов;
        проверка, нет ли проекта с таким именем;
        пользователь сразу же становится менеджером проекта;

    Запрос: @POST host/api/projects/add {
        "name": "Проект ИКС",
        "inf": {
            "desc": "Супер-проект по выращиванию мутантов"
        }
    }

    Положительный ответ: {
        "ans": "ok",
        "nid": 13
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "Project with this name already exists."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.name = None
        self.inf = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.ProjectsAddH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'name' in b:
            self.name = b['name']
            if len(self.name) < NAME_MIN_LEN or len(self.name) > NAME_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid name length : must be [{}, {}]'.format(NAME_MIN_LEN, NAME_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no name'
            return

        if 'inf' in b:
            self.inf = []
            for k in b['inf']:
                if b['inf'][k] is str:
                    self.inf.append((k, b['inf'][k]))
                elif b['inf'][k] is int or b['inf'][k] is float or b['inf'][k] is bool:
                    self.inf.append((k, str(b['inf'][k])))
                else:
                    self.is_valid = False
                    self.error_m = 'Inf format is invalid'
                    return


class ProjectsHieAddH(tornado.web.RequestHandler):
    """
    -> Назначить для проекта родительский проект:
    Условия:
        проверка IDшек на существование;
        проверка, является ли пользователь менеджером в обоих проектах;
        проверка, не имеют ли проекты каких-то отношений;

    Запрос: @POST host/api/project/hie/add {
        "parent_id": 13,
        "child_id": 37
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.parent_id = None
        self.child_id = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.ProjectsHieAddH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'parent_id' in b:
            self.parent_id = b['parent_id']
            if len(self.parent_id) < ID_MIN_LEN or len(self.parent_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid parent_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no parent_id'
            return

        if 'child_id' in b:
            self.child_id = b['child_id']
            if len(self.child_id) < ID_MIN_LEN or len(self.child_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid child_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no child_id'
            return


class ProjectsHieRemH(tornado.web.RequestHandler):
    """
    -> Удалить проект из отношения родитель-ребенок:
    Условия:
        проверка IDшек на существование;
        проверка, является ли пользователь менеджером в обоих проектах;
        проверка, имеют ли проекты соответствующие отношения;

    Запрос: @POST host/api/projects/hie/rem {
        "parent_id": 13,
        "child_id": 37
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.parent_id = None
        self.child_id = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.ProjectsHieRemH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'parent_id' in b:
            self.parent_id = b['parent_id']
            if len(self.parent_id) < ID_MIN_LEN or len(self.parent_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid parent_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no parent_id'
            return

        if 'child_id' in b:
            self.child_id = b['child_id']
            if len(self.child_id) < ID_MIN_LEN or len(self.child_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid child_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no child_id'
            return


class ProjectsEditH(tornado.web.RequestHandler):
    """
    -> Редактировать проект:
    Условия:
        проверка аргументов + IDхи;
        проверка, является ли пользователь менеджером;

    Запрос: @POST host/api/projects/edit {
        "proj_id": 13,
        "inf": {
            "iam": "new info"
        }
        "s": "closed"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.proj_id = None
        self.inf = None
        self.s = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.ProjectsEditH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'proj_id' in b:
            self.proj_id = b['proj_id']
            if len(self.proj_id) < ID_MIN_LEN or len(self.proj_id) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid proj_id length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no proj_id'
            return

        if 'inf' in b:
            self.inf = []
            for k in b['inf']:
                if b['inf'][k] is str:
                    self.inf.append((k, b['inf'][k]))
                elif b['inf'][k] is int or b['inf'][k] is float or b['inf'][k] is bool:
                    self.inf.append((k, str(b['inf'][k])))
                else:
                    self.is_valid = False
                    self.error_m = 'Inf format is invalid'
                    return

        if 's' in b:
            self.s = b['s']
            if len(self.s) < STATUS_MIN_LEN or len(self.s) > STATUS_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid s length : must be [{}, {}]'.format(STATUS_MIN_LEN, STATUS_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no s'
            return


class TasksCH(tornado.web.RequestHandler):
    """
    -> Получить количество заданий проекта:
    Условия:
        проверка ID на существование;

    Запрос: @GET host/api/tasks/c
    Аргументы:
        ?proj_id=13 - ID проекта, чьи задания считаем

    Положительный ответ: {
        "ans": "ok",
        "c": 36
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No such project."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.proj_id = None
        self.is_valid = True
        self.error_m = None

    @asynchronous
    def get(self):
        self.parse_query()
        if self.is_valid:
            pass
            #TODO Отправка аргументов + self в task_queue на исполнение
        else:
            self.write(r'"ans":"nok","m":{}'.format(self.error_m))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'proj_id' in q:
            self.proj_id = q['proj_id']
        else:
            self.is_valid = False
            self.error_m = 'No such project'


class TasksH(tornado.web.RequestHandler):
    """
    -> Листинг заданий проекта:
    Условия:
        проверка аргументов;
        проверка, является ли пользователь членом проекта;

    Запрос: @GET host/api/tasks
    Аргументы:
        ?proj_id=13 - ID проекта, чьи задания получаем;
        ?from=0 - Откуда начинать порцию;
        ?count=20 - Размер порции заданий;

    Положительный ответ: [{
        "id": 2,
        "t": "bug",
        "name": "Отваливается все",
        "s": "new",
        "perf_id": 66,
        "ready": 0,
        "last_ts": 1454654654
        }, {
        "id": 3,
        "t": "feat",
        "name": "Кольцевой генератор",
        "s": "in_w",
        "perf_id": 66,
        "ready": 75,
        "last_ts": 1467332323
    }]
    Отрицательный ответ: {
        "ans": "nok",
        "m": "Empty"
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.proj_id = None
        self.from_ = None
        self.count = None
        self.is_valid = True
        self.error_m = None

    @asynchronous
    def get(self):
        self.parse_query()
        if self.is_valid:
            pass
            #TODO Отправка аргументов + self в task_queue на исполнение
        else:
            self.write(r'"ans":"nok","m":{}'.format(self.error_m))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'proj_id' in q:
            self.proj_id = q['proj_id']
        else:
            self.is_valid = False
            self.error_m = 'No such project'

        if 'from' in q:
            self.from_ = q['from']

        if 'count' in q:
            self.count = q['count']


class TasksFH(tornado.web.RequestHandler):
    """
    -> Получить задание по ID:
    Условия:
        проверка аргументов;
        проверка, является ли пользователь членом проекта;

    Запрос: @GET host/api/tasks/f
    Аргументы:
        ?byid=13 - Получить задание по конкретному ID;

    Положительный ответ: {
        "ans": "ok",
        "f": {
        "id": 13,
            "t": "bug",
            "name": "Отвалилось",
            "desc": "Все отвалилось",
            "s": "new",
            "reporter": 2,
            "pref": 45,
            "add_ts": 144465465544,
            "fixed_ts": 14546466644,
            "lastch_ts": 14465465465,
            "time": 32132123,
            "ready": 0,
            "parent_id": 12,
            "children": [14, 69]
        }
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.byid = None
        self.is_valid = True
        self.error_m = None

    @asynchronous
    def get(self):
        self.parse_query()
        if self.is_valid:
            pass
            #TODO Отправка аргументов + self в task_queue на исполнение
        else:
            self.write(r'"ans":"nok","m":{}'.format(self.error_m))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'byid' in q:
            self.byid = q['byid']
        else:
            self.is_valid = False
            self.error_m = 'Empty'


class TasksEditH(tornado.web.RequestHandler):
    """
    -> Редактирование задачи:
    Условия:
        проверка аргументов + IDхи;
        проверка, является ли пользователь создателем/исполнителем, или менеджером проекта;

    Запрос: @POST host/api/tasks/edit {
        "byid": 13,
        "name": "Отваляколось",
        "desc": "Развалякалось",
        "time": 99999999999999,
        "ready": 12,
        "parent_id": 0
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.byid = None
        self.name = None
        self.desc = None
        self.time = None
        self.ready = None
        self.parent_id = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.TasksEditH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 'byid' in b:
            self.byid = b['byid']
            if len(self.byid) < ID_MIN_LEN or len(self.byid) > ID_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid byid length : must be [{}, {}]'.format(ID_MIN_LEN, ID_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no byid'
            return

        if 'name' in b:
            self.name = b['name']
            if len(self.name) < NAME_MIN_LEN or len(self.name) > NAME_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid name length : must be [{}, {}]'.format(NAME_MIN_LEN, NAME_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no name'
            return

        if 'desc' in b:
            self.desc = b['desc']
            if len(self.desc) < 1 or len(self.desc) > VARCHAR_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid desc length : must be [{}, {}]'.format(1, VARCHAR_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no desc'
            return

        #TODO Работа с числовым типом - byid, time, ready, parent_id


class TasksEditSH(tornado.web.RequestHandler):
    """
    -> Изменение статуса задачи:
    Условия:
        проверка аргументов + IDхи;
        проверка, является ли пользователь создателем/исполнителем, или менеджером проекта;

    Запрос: @POST host/api/tasks/edit_s {
        "byid": 13,
        "s": "in_w",
        "desc": "В работе"
    }

    Положительный ответ: {
        "ans": "ok"
    }
    Отрицательный ответ: {
        "ans": "nok",
        "m": "No permissions."
    }
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.byid = None
        self.s = None
        self.desc = None
        self.error_m = None

    @asynchronous
    def post(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self.parse_body(in_body)
                if not self.is_valid:
                    self.write(r'{"ans":"nok","m":{}}'.format(self.error_m))
                else:
                    #TODO Отправка аргументов + self в task_queue на исполнение
                    return
            except Exception as e:
                logging.warning('Exception on web_tier.TasksEditSH : post - {}'.format(e))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    def parse_body(self, b):
        if 's' in b:
            self.s = b['s']
            if len(self.s) < STATUS_MIN_LEN or len(self.s) > STATUS_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid s length : must be [{}, {}]'.format(STATUS_MIN_LEN, STATUS_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no s'
            return

        if 'desc' in b:
            self.desc = b['desc']
            if len(self.desc) < 1 or len(self.desc) > VARCHAR_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid desc length : must be [{}, {}]'.format(1, VARCHAR_MAX_LEN)
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no desc'
            return