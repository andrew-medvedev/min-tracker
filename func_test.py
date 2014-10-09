__author__ = 'a.medvedev'

from urllib.request import urlopen, Request
import json

HOST = 'http://localhost:1337'


def http(method, path, body=None):
    req = Request(HOST + path, bytes(json.dumps(body), encoding='utf-8'))
    req.get_method = lambda: method

    response = urlopen(req)
    code = response.getcode()
    out_raw, out = None, None
    if code == 200:
        out_raw = response.read.decode('utf-8')
        try:
            out = json.loads(out_raw)
        except:
            pass

    return code, out_raw, out


def fail():
    print('FAIL')


def success():
    print('SUCCESS')


def test_1():
    #/api/regn
    code, out_raw, out = http('POST', '/api/regn', {
        'login': 'andrew.medvedev.nh@gmail.com',
        'password': '123456789',
        'name': 'andrew.medvedev',
        'data': {
            'fname': 'andrew',
            'lname': 'medvedev',
            'role': 'Developer'
        }
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_2():
    #/api/login
    code, out_raw, out = http('POST', '/api/login', {
        'login': 'andrew.medvedev.nh@gmail.com',
        'password': '123456789'
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_3():
    #/api/logout
    code, out_raw, out = http('POST', '/api/logout', {
        'tok': 'vj58jrf5s0'
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_4():
    #/api/projects/c
    code, out_raw, out = http('GET', '/api/projects/c')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_5():
    #/api/projects
    code, out_raw, out = http('GET', '/api/projects?my=1&s=open')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_6():
    #/api/projects/f
    code, out_raw, out = http('GET', '/api/projects/f?byid=3')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_7():
    #/api/memb/add
    code, out_raw, out = http('POST', '/api/memb/add', {
        'memb_id': 13,
        'proj_id': 37,
        'role': 'perf',
        'desc': 'Покачену'
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_8():
    #/api/memb/rem
    code, out_raw, out = http('POST', '/api/memb/rem', {
        'memb_id': 13,
        'proj_id': 37,
        'desc': 'Покачену'
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_9():
    #/api/memb/chr
    code, out_raw, out = http('POST', '/api/memb/chr', {
        "memb_id": 13,
        "proj_id": 37,
        "new_r": "man",
        "desc": "Повышение"
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_10():
    #/api/projects/add
    code, out_raw, out = http('POST', '/api/projects/add', {
        "name": "Проект ИКС",
        "inf": {
            "desc": "Супер-проект по выращиванию мутантов"
        }
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_11():
    #/api/project/hie/add
    code, out_raw, out = http('POST', '/api/projects/hie/add', {
        "parent_id": 13,
        "child_id": 37
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_12():
    #/api/projects/hie/rem
    code, out_raw, out = http('POST', '/api/projects/hie/rem', {
        "parent_id": 13,
        "child_id": 37
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_13():
    #/api/projects/edit
    code, out_raw, out = http('POST', '/api/projects/edit', {
        "proj_id": 13,
        "inf": {
            "iam": "the law!"
        },
        "s": "closed"
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_14():
    #/api/tasks/c
    code, out_raw, out = http('POST', '/api/tasks/c?proj_id=13')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_15():
    #/api/tasks
    code, out_raw, out = http('POST', '/api/tasks?proj_id=13&from=0&count=20')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_16():
    #/api/tasks/f
    code, out_raw, out = http('POST', '/api/tasks/f?byid=13')
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_17():
    #/api/tasks/edit
    code, out_raw, out = http('POST', '/api/tasks/edit', {
        "byid": 13,
        "name": "Отваляколось",
        "desc": "Развалякалось",
        "time": 99999999999999,
        "ready": 12,
        "parent_id": 0
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def test_18():
    #/api/tasks/edit_s
    code, out_raw, out = http('POST', '/api/tasks/edit_s', {
        "byid": 13,
        "s": "in_w",
        "desc": "В работе"
    })
    if code != 200:
        fail()
        return False
    elif out is None:
        fail()
        return False
    elif 'ans' in out and 'm' in out:
        success()
        return True
    else:
        fail()
        return False


def main():
    pass


if __name__ == '__main__':
    main()