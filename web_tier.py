__author__ = 'a.medvedev'

import re
import abc
import json
import logging
import utils
import limits
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
        logging.critical('At web_tier.init_web_tier - {}'.format(e))
        return
    tornado.ioloop.IOLoop.instance().start()


class DefaultHandler(tornado.web.RequestHandler):
    """
    Абстрактный(по идее) класс, который будет являться основой для всех веб-слушателей,
    содержит в себе внутренние методы парсинга аргументов из dict-тела, шаблонные get- и post- обработчики
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.is_valid = True
        self.error_m = None

    def _post_pat(self):
        if self.request.body is not None:
            try:
                in_body = json.loads(self.request.body.decode('utf-8'))
                self._parse_body(in_body)
                if not self.is_valid:
                    self.write(json.dumps({
                        "ans": "nok",
                        "m": self.error_m
                    }))
                else:
                    self._process_req()
                    return
            except Exception as e:
                logging.warning('Exception on {} : post - {}'.format(self.__class__.__name__, e.args))
                self.set_status(400)
        else:
            self.set_status(400)
        self.finish()

    @abc.abstractmethod
    def _parse_body(self, b):
        """
        Абстрактный(по идее) метод, который будет содержать в себе логику извлечения аргументов из тела запроса

        :param b: dict-тело post-запроса
        """
        pass

    def _process_req(self):
        """
        Метод, который отправляет запрос со всеми аргументами на исполнение(в очередь задач)
        По умолчанию - просто возвращает такой вот ответ:
        """
        self.write('{"ans":"ok","m":"Isn\'t implemented"}')
        self.finish()

    def _parse_str(self, b, k, min_len, max_len, spec_check=None):
        """
        Внутренний метод парсит строку из dict-тела b под ключем k. Если в процессе извлечения аргумента произошла
        какая-то ошибка, метод вернет None, и присвоит соответствующие значения self-переменным is_valid и error_m

        :param b: dict-тело, полученной в результате парсинга json-тела, сформированного клиентом
        :param k: str-значение ключа, под которым нужно искать нужный аргумент в теле b
        :param min_len: проверка на минимальное значение длины str-аргумента, если оный будет извлечен из тела
        :param max_len: проверка на максимальное значение длины str-аргумента, если оный будет извлечен из тела
        :param spec_check: лямбда для специальной проверки извлеченного значение. Функция должна возвращать str-значение
        ошибки, или None, если извлеченный аргумент прошел проверку
        :return: извлеченный из тела аргумент, или None, если есть проблемы
        """
        out = None

        if k in b:
            if type(b[k]) is str:
                out = True, b[k]
                if len(b[k]) < min_len or len(b[k]) > max_len:
                    out = False, 'Invalid {} length : must be [{}, {}]'.format(k, min_len, max_len)
                elif spec_check is not None:
                    err_m = spec_check(b[k])
                    if err_m is not None:
                        out = False, err_m
            else:
                out = False, 'Invalid argument type: {} must be str'.format(k)
        else:
            out = False, 'Invalid arguments: no {}'.format(k)

        return out

    def _parse_int(self, b, k, min_val, max_val, spec_check=None):
        """
        Внутренний метод парсит целое число из dict-тела b под ключем k. Если в процессе извлечения аргумента произошла
        какая-то ошибка, метод вернет None, и присвоит соответствующие значения self-переменным is_valid и error_m

        :param b: dict-тело, полученной в результате парсинга json-тела, сформированного клиентом
        :param k: str-значение ключа, под которым нужно искать нужный аргумент в теле b
        :param min_val: проверка на минимальное значение int-аргумента, если оный будет извлечен из тела
        :param max_val: проверка на максимальное значение int-аргумента, если оный будет извлечен из тела
        :param spec_check: лямбда для специальной проверки извлеченного значение. Функция должна возвращать str-значение
        ошибки, или None, если извлеченный аргумент прошел проверку
        :return: извлеченный из тела аргумент, или None, если есть проблемы
        """
        out = None

        if k in b:
            if type(b[k]) is int:
                out = True, b[k]
                if b[k] < min_val or b[k] > max_val:
                    out = False, 'Invalid {} range : must be [{}, {}]'.format(k, min_val, max_val)
                elif spec_check is not None:
                    err_m = spec_check(b[k])
                    if err_m is not None:
                        out = False, err_m
            else:
                out = False, 'Invalid argument type: {} must be integer'.format(k)
        else:
            out = False, 'Invalid arguments: no {}'.format(k)

        return out

    def _parse_kv_dict(self, b, k, **kwargs):
        """
        Внутренний метод парсит key-value словарь из dict-тела b под ключем k. Если в процессе извлечения произошла
        какая-то ошибка, метод вернет None, и присвоит соответствующие значения self-переменным is_valid и error_m.
        Весьма тупой алгоритм, но пока это - оптимальное решение

        :param b: dict-тело, полученной в результате парсинга json-тела, сформированного клиентом
        :param k1: str-значение ключа, под которым нужно искать нужный аргумент в теле b
        :param kwargs: хитрая система ниппель(filter - dict для сопоставления имен полей и типов, exclude - флаг,
        который исключает остальный поля, не входящие в filter, all_type - тип, которому должны пренадлежать все поля,
        all_need - флаг, указывающий, что все поля, указанные в фильтре, должны присутствовать)
        :return: извлеченный из тела аргумент, или None, если есть проблемы
        """
        out = None

        all_type = None
        filter = None
        exclude = False
        all_need = False
        if 'all_type' in kwargs:
            all_type = kwargs['all_type']
        else:
            if 'filter' in kwargs:
                filter = kwargs['filter']
            if 'exclude' in kwargs:
                exclude = kwargs['exclude']
            if 'all_need' in kwargs:
                all_need = kwargs['all_need']

        if k in b:
            if type(b[k]) is dict:
                out = True, []
                for k1 in b[k]:
                    if all_type is not None:
                        if b[k][k1] is all_type:
                            out[1].append((k1, b[k][k1]))
                    else:
                        if filter is not None:
                            if k1 in filter:
                                if b[k][k1] is filter[k1]:
                                    out[1].append((k1, b[k][k1]))
                            else:
                                if not exclude:
                                    out[1].append((k1, b[k][k1]))
                        else:
                            out[1].append((k1, b[k][k1]))
            else:
                out = False, '{} is not dict'.format(k)

        if out[0] and all_need and filter is not None:
            for key in filter:
                if key not in out:
                    out = False, 'Dict format of {} is invalid: no field {}'.format(k, key)

        return out

    def _parse_boolean(self, b, k):
        """
        Внутренний метод парсит булевую из dict-тела b под ключем k. Если в процессе извлечения аргумента произошла
        какая-то ошибка, метод вернет None, и присвоит соответствующие значения self-переменным is_valid и error_m

        :param b: dict-тело, полученной в результате парсинга json-тела, сформированного клиентом
        :param k: str-значение ключа, под которым нужно искать нужный аргумент в теле b
        :return: извлеченный из тела аргумент, или None, если есть проблемы
        """
        out = None

        if k in b:
            if type(b[k]) is str:
                out = True, b[k]
            else:
                out = False, 'Invalid argument type: {} must be bool'.format(k)
        else:
            out = False, 'Invalid arguments: no {}'.format(k)

        return out


class RegnH(DefaultHandler):
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
        self.login = None
        self.password = None
        self.name = None
        self.data = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        login = self._parse_str(b, 'login', limits.LOGIN_MIN_LEN, limits.LOGIN_MAX_LEN,
                                lambda i:
                                'Invalid login form: must be an email'
                                if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
                                                , i) else None)
        if login[0]:
            self.login = login[1]
        else:
            self.is_valid = False
            self.error_m = login[1]
            return

        password = self._parse_str(b, 'password', limits.PASSWORD_MIN_LEN, limits.PASSWORD_MAX_LEN)
        if password[0]:
            self.password = password[1]
        else:
            self.is_valid = False
            self.error_m = password[1]
            return

        name = self._parse_str(b, 'name', limits.NAME_MIN_LEN, limits.NAME_MAX_LEN)
        if name[0]:
            self.name = name[1]
        else:
            self.is_valid = False
            self.error_m = name[1]
            return

        data = self._parse_kv_dict(b, 'data', all_type=str)
        if data[0]:
            self.data = data[1]
        else:
            self.is_valid = False
            self.error_m = data[1]
            return


class LoginH(DefaultHandler):
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
        self.login = None
        self.password = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        login = self._parse_str(b, 'login', limits.LOGIN_MIN_LEN, limits.LOGIN_MAX_LEN)
        if login[0]:
            self.login = login[1]
        else:
            self.is_valid = False
            self.error_m = login[1]
            return

        password = self._parse_str(b, 'password', limits.PASSWORD_MIN_LEN, limits.PASSWORD_MAX_LEN)
        if password[0]:
            self.password = password[1]
        else:
            self.is_valid = False
            self.error_m = password[1]
            return


class LogoutH(DefaultHandler):
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
        self.tok = None

    @asynchronous
    def post(self):
        self._post_pat()

    def parse_body(self, b):
        tok = self._parse_str(b, 'tok', limits.TOKEN_LEN, limits.TOKEN_LEN)
        if tok[0]:
            self.tok = tok[1]
        else:
            self.is_valid = False
            self.error_m = tok[1]
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
        self.write('{"ans":"ok","m":"Isn\'t implemented"}')
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
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.my = None
        self.s = None
        self.is_valid = True
        self.error_m = None

    @asynchronous
    def get(self):
        self.parse_query()
        if self.is_valid:
            #TODO Отправка аргументов + self в task_queue на исполнение
            self.write('{"ans":"ok","m":"Isn\'t implemented"}')
            self.finish()
        else:
            self.write(json.dumps({
                "ans": "nok",
                "m": self.write_error
            }))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'my' in q:
            self.my = q['my'] == '1'
        if 's' in q:
            self.s = q['s']
            if len(self.s) < limits.STATUS_MIN_LEN or len(self.s) > limits.STATUS_MAX_LEN:
                self.is_valid = False
                self.error_m = 'Invalid argument s: length must be [{}, {}]'.format(limits.STATUS_MIN_LEN, limits.STATUS_MAX_LEN)
            if self.s != 'open' and self.s != 'freeze' and self.s != 'closed' and self.s != 'fail':
                self.is_valid = False
                self.error_m = 'Invalid argument s: must be "open", "freeze", "closed" or "fail"'


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
            #TODO Отправка аргументов + self в task_queue на исполнение
            self.write('{"ans":"ok","m":"Isn\'t implemented"}')
            self.finish()
        else:
            self.write(json.dumps({
                "ans": "nok",
                "m": self.error_m
            }))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'byid' in q:
            try:
                self.byid = int(q['byid'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: byid'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))
        else:
            self.is_valid = False
            self.error_m = 'Empty'


class MembAddH(DefaultHandler):
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
        self.memb_id = None
        self.proj_id = None
        self.role = None
        self.desc = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        memb_id = self._parse_int(b, 'memb_id', limits.LONG_MIN, limits.LONG_MAX)
        if memb_id[0]:
            self.memb_id = memb_id[1]
        else:
            self.is_valid = False
            self.error_m = memb_id[1]

        proj_id = self._parse_int(b, 'proj_id', limits.LONG_MIN, limits.LONG_MAX)
        if proj_id[0]:
            self.proj_id = proj_id[1]
        else:
            self.is_valid = False
            self.error_m = proj_id[1]

        role = self._parse_str(b, 'role', limits.ROLE_MIN_LEN, limits.ROLE_MAX_LEN,
                               lambda i: 'Invalid role : must be "man", "perf" or "vis"'
                               if i != 'man' and i != 'perf' and i != 'vis'
                               else None)
        if role[0]:
            self.role = role[1]
        else:
            self.is_valid = False
            self.error_m = role[1]

        desc = self._parse_str(b, 'desc', 1, limits.VARCHAR_MAX_LEN)
        if desc[0]:
            self.desc = desc[1]
        else:
            self.is_valid = False
            self.error_m = desc[1]


class MembRemH(DefaultHandler):
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
        self.memb_id = None
        self.proj_id = None
        self.desc = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        memb_id = self._parse_int(b, 'memb_id', limits.LONG_MIN, limits.LONG_MAX)
        if memb_id[0]:
            self.memb_id = memb_id[1]
        else:
            self.is_valid = False
            self.error_m = memb_id[1]

        proj_id = self._parse_int(b, 'proj_id', limits.LONG_MIN, limits.LONG_MAX)
        if proj_id[0]:
            self.proj_id = proj_id[1]
        else:
            self.is_valid = False
            self.error_m = proj_id[1]

        desc = self._parse_str(b, 'desc', 1, limits.VARCHAR_MAX_LEN)
        if desc[0]:
            self.desc = desc[1]
        else:
            self.is_valid = False
            self.error_m = desc[1]


class MembChrH(DefaultHandler):
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
        self.memb_id = None
        self.proj_id = None
        self.new_r = None
        self.desc = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        memb_id = self._parse_int(b, 'memb_id', limits.LONG_MIN, limits.LONG_MAX)
        if memb_id[0]:
            self.memb_id = memb_id[1]
        else:
            self.is_valid = False
            self.error_m = memb_id[1]

        proj_id = self._parse_int(b, 'proj_id', limits.LONG_MIN, limits.LONG_MAX)
        if proj_id[0]:
            self.proj_id = proj_id[1]
        else:
            self.is_valid = False
            self.error_m = proj_id[1]

        new_r = self._parse_str(b, 'new_r', limits.ROLE_MIN_LEN, limits.ROLE_MAX_LEN,
                                lambda i: 'Invalid new_role : must be "man", "perf" or "vis"'
                                if i != 'man' and i != 'perf' and i != 'vis'
                                else None)
        if new_r[0]:
            self.new_r = new_r[1]
        else:
            self.is_valid = False
            self.error_m = new_r[1]

        desc = self._parse_str(b, 'desc', 1, limits.VARCHAR_MAX_LEN)
        if desc[0]:
            self.desc = desc[1]
        else:
            self.is_valid = False
            self.error_m = desc[1]


class ProjectsAddH(DefaultHandler):
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
        self.name = None
        self.inf = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        name = self._parse_str(b, 'name', limits.NAME_MIN_LEN, limits.NAME_MAX_LEN)
        if name[0]:
            self.name = name[1]
        else:
            self.is_valid = False
            self.error_m = name[1]
            return

        inf = self._parse_kv_dict(b, 'inf', all_type=str)
        if inf[0]:
            self.inf = inf[1]
        else:
            self.is_valid = False
            self.error_m = inf[1]
            return


class ProjectsHieAddH(DefaultHandler):
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
        self.parent_id = None
        self.child_id = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        parent_id = self._parse_int(b, 'parent_id', limits.LONG_MIN, limits.LONG_MAX)
        if parent_id[0]:
            self.parent_id = parent_id[1]
        else:
            self.is_valid = False
            self.error_m = parent_id[1]
            return

        child_id = self._parse_int(b, 'child_id', limits.LONG_MIN, limits.LONG_MAX)
        if child_id[0]:
            self.child_id = child_id[1]
        else:
            self.is_valid = False
            self.error_m = child_id[1]
            return


class ProjectsHieRemH(DefaultHandler):
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
        self.parent_id = None
        self.child_id = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        parent_id = self._parse_int(b, 'parent_id', limits.LONG_MIN, limits.LONG_MAX)
        if parent_id[0]:
            self.parent_id = parent_id[1]
        else:
            self.is_valid = False
            self.error_m = parent_id[1]
            return

        child_id = self._parse_int(b, 'child_id', limits.LONG_MIN, limits.LONG_MAX)
        if child_id[0]:
            self.child_id = child_id[1]
        else:
            self.is_valid = False
            self.error_m = child_id[1]
            return


class ProjectsEditH(DefaultHandler):
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
        self.proj_id = None
        self.inf = None
        self.s = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        proj_id = self._parse_int(b, 'proj_id', limits.LONG_MIN, limits.LONG_MAX)
        if proj_id[0]:
            self.parent_id = proj_id[1]
        else:
            self.is_valid = False
            self.error_m = proj_id[1]
            return

        inf = self._parse_kv_dict(b, 'inf', all_type=str)
        if inf[0]:
            self.inf = inf[1]
        else:
            self.is_valid = False
            self.error_m = inf[1]
            return

        s = self._parse_str(b, 's', limits.STATUS_MIN_LEN, limits.STATUS_MAX_LEN,
                            lambda i: 'Invalid argument s: must be "open", "freeze", "closed" or "fail"'
                            if i != 'open' and i != 'freeze' and i != 'closed' and i != 'fail'
                            else None)
        if s[0]:
            self.s = s[1]
        else:
            self.is_valid = False
            self.error_m = s[1]


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
            #TODO Отправка аргументов + self в task_queue на исполнение
            self.write('{"ans":"ok","m":"Isn\'t implemented"}')
            self.finish()
        else:
            self.write(json.dumps({
                "ans": "nok",
                "m": self.error_m
            }))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'proj_id' in q:
            try:
                self.proj_id = int(q['proj_id'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: proj_id'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))
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
            #TODO Отправка аргументов + self в task_queue на исполнение
            self.write('{"ans":"ok","m":"Isn\'t implemented"}')
            self.finish()
        else:
            self.write(json.dumps({
                "ans": "nok",
                "m": self.error_m
            }))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'proj_id' in q:
            try:
                self.proj_id = int(q['proj_id'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: proj_id'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))
        else:
            self.is_valid = False
            self.error_m = 'No such project'

        if 'from' in q:
            try:
                self.from_ = int(q['from'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: from'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))

        if 'count' in q:
            try:
                self.count = int(q['count'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: count'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))


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
            #TODO Отправка аргументов + self в task_queue на исполнение
            self.write('{"ans":"ok","m":"Isn\'t implemented"}')
            self.finish()
        else:
            self.write(json.dumps({
                "ans": "nok",
                "m": self.error_m
            }))
            self.finish()

    def parse_query(self):
        q = utils.parse_query(self.request.query)
        if 'byid' in q:
            try:
                self.byid = int(q['byid'])
            except Exception as e:
                self.is_valid = False
                self.error_m = 'Invalid argument: byid'
                logging.warning('Exception on {} : parse_query - {}'.format(self.__class__.__name__, e.args))
        else:
            self.is_valid = False
            self.error_m = 'Empty'


class TasksEditH(DefaultHandler):
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
        self.byid = None
        self.name = None
        self.desc = None
        self.time = None
        self.ready = None
        self.parent_id = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        byid = self._parse_int(b, 'byid', limits.LONG_MIN, limits.LONG_MAX)
        if byid[0]:
            self.byid = byid[1]
        else:
            self.is_valid = False
            self.error_m = byid[1]
            return

        name = self._parse_int(b, 'name', limits.NAME_MIN_LEN, limits.NAME_MAX_LEN)
        if name[0]:
            self.name = name[1]
        else:
            self.is_valid = False
            self.error_m = name[1]
            return

        desc = self._parse_int(b, 'desc', 1, limits.VARCHAR_MAX_LEN)
        if desc[0]:
            self.desc = desc[1]
        else:
            self.is_valid = False
            self.error_m = desc[1]
            return

        time = self._parse_int(b, 'time', limits.LONG_MIN, limits.LONG_MAX)
        if time[0]:
            self.time = time[1]
        else:
            self.is_valid = False
            self.error_m = time[1]
            return

        ready = self._parse_int(b, 'ready', 0, 100)
        if ready[0]:
            self.ready = ready[1]
        else:
            self.is_valid = False
            self.error_m = ready[1]
            return

        parent_id = self._parse_int(b, 'parent_id', limits.LONG_MIN, limits.LONG_MAX)
        if parent_id[0]:
            self.parent_id = parent_id[1]
        else:
            self.is_valid = False
            self.error_m = parent_id[1]
            return


class TasksEditSH(DefaultHandler):
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
        self.byid = None
        self.s = None
        self.desc = None

    @asynchronous
    def post(self):
        self._post_pat()

    def _parse_body(self, b):
        byid = self._parse_int(b, 'byid', limits.LONG_MIN, limits.LONG_MAX)
        if byid[0]:
            self.byid = byid[1]
        else:
            self.is_valid = False
            self.error_m = byid[1]
            return

        s = self._parse_int(b, 's', limits.STATUS_MIN_LEN, limits.STATUS_MAX_LEN,
                            lambda i: 'Invalid status : must be "new", "open", "closed" or "failed"'
                            if i != 'new' and i != 'open' and i != 'closed' and i != 'failed'
                            else None)
        if s[0]:
            self.s = s[1]
        else:
            self.is_valid = False
            self.error_m = s[1]
            return

        desc = self._parse_int(b, 'desc', 1, limits.VARCHAR_MAX_LEN)
        if desc[0]:
            self.desc = desc[1]
        else:
            self.is_valid = False
            self.error_m = desc[1]
            return