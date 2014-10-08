__author__ = 'a.medvedev'

import re
import json
import logging
import utils
import tornado.web
import tornado.ioloop
import tornado.httputil
from tornado.web import asynchronous


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
            if len(self.login) < 4 or len(self.login) > 30:
                self.is_valid = False
                self.error_m = 'Invalid login length : must be [4, 30]'
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
            if len(self.password) < 6 or len(self.password) > 50:
                self.is_valid = False
                self.error_m = 'Invalid password length : must be [6, 50]'
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no password'
            return

        if 'name' in b:
            self.name = b['name']
            if not utils.chlat_dot_etc(self.name):
                self.is_valid = False
                self.error_m = 'Invalid argument: name must be lat || dot'
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
            if len(self.login) < 4 or len(self.login) > 30:
                self.is_valid = False
                self.error_m = 'Invalid login length : must be [4, 30]'
                return
        else:
            self.is_valid = False
            self.error_m = 'Invalid arguments: no login'
            return

        if 'password' in b:
            self.password = b['password']
            if len(self.password) < 6 or len(self.password) > 50:
                self.is_valid = False
                self.error_m = 'Invalid password length : must be [6, 50]'
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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def get(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def get(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def get(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def get(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def get(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()