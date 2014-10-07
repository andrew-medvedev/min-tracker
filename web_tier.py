__author__ = 'a.medvedev'

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
    app.listen(port, host)
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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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

    @asynchronous
    def post(self):
        self.set_status(501)
        self.finish()


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