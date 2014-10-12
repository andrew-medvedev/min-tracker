__author__ = 'a.medvedev'

from urllib.request import urlopen, Request, HTTPError
import json

HOST = 'http://localhost:1337'


def http(method, path, body=None):
    req = Request(HOST + path, bytes(json.dumps(body), encoding='utf-8'))
    req.get_method = lambda: method
    try:
        response = urlopen(req)
    except HTTPError as http_err:
        return http_err.getcode(), None, None
    code = response.getcode()
    out_raw, out = None, None
    if code == 200:
        out_raw = response.read().decode('utf-8')
        try:
            out = json.loads(out_raw)
        except:
            pass

    return code, out_raw, out


def fail(wut):
    print('FAIL - {}'.format(wut))


def success(wut):
    print('SUCCESS - {}'.format(wut))


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
        fail('test_1')
        return False
    elif out is None:
        fail('test_1')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_1')
        return True
    else:
        fail('test_1')
        return False


def test_2():
    #/api/login
    code, out_raw, out = http('POST', '/api/login', {
        'login': 'andrew.medvedev.nh@gmail.com',
        'password': '123456789'
    })
    if code != 200:
        fail('test_2')
        return False
    elif out is None:
        fail('test_2')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_2')
        return True
    else:
        fail('test_2')
        return False


def test_3():
    #/api/logout
    code, out_raw, out = http('POST', '/api/logout', {
        'tok': 'vj58jrf5s0'
    })
    if code != 200:
        fail('test_3')
        return False
    elif out is None:
        fail('test_3')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_3')
        return True
    else:
        fail('test_3')
        return False


def test_4():
    #/api/projects/c
    code, out_raw, out = http('GET', '/api/projects/c')
    if code != 200:
        fail('test_4')
        return False
    elif out is None:
        fail('test_4')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_4')
        return True
    else:
        fail('test_4')
        return False


def test_5():
    #/api/projects
    code, out_raw, out = http('GET', '/api/projects?my=1&s=open')
    if code != 200:
        fail('test_5')
        return False
    elif out is None:
        fail('test_5')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_5')
        return True
    else:
        fail('test_5')
        return False


def test_6():
    #/api/projects/f
    code, out_raw, out = http('GET', '/api/projects/f?byid=3')
    if code != 200:
        fail('test_6')
        return False
    elif out is None:
        fail('test_6')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_6')
        return True
    else:
        fail('test_6')
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
        fail('test_7')
        return False
    elif out is None:
        fail('test_7')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_7')
        return True
    else:
        fail('test_7')
        return False


def test_8():
    #/api/memb/rem
    code, out_raw, out = http('POST', '/api/memb/rem', {
        'memb_id': 13,
        'proj_id': 37,
        'desc': 'Покачену'
    })
    if code != 200:
        fail('test_8')
        return False
    elif out is None:
        fail('test_8')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_8')
        return True
    else:
        fail('test_8')
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
        fail('test_9')
        return False
    elif out is None:
        fail('test_9')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_9')
        return True
    else:
        fail('test_9')
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
        fail('test_10')
        return False
    elif out is None:
        fail('test_10')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_10')
        return True
    else:
        fail('test_10')
        return False


def test_11():
    #/api/project/hie/add
    code, out_raw, out = http('POST', '/api/projects/hie/add', {
        "parent_id": 13,
        "child_id": 37
    })
    if code != 200:
        fail('test_11')
        return False
    elif out is None:
        fail('test_11')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_11')
        return True
    else:
        fail('test_11')
        return False


def test_12():
    #/api/projects/hie/rem
    code, out_raw, out = http('POST', '/api/projects/hie/rem', {
        "parent_id": 13,
        "child_id": 37
    })
    if code != 200:
        fail('test_12')
        return False
    elif out is None:
        fail('test_12')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_12')
        return True
    else:
        fail('test_12')
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
        fail('test_13')
        return False
    elif out is None:
        fail('test_13')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_13')
        return True
    else:
        fail('test_13')
        return False


def test_14():
    #/api/tasks/c
    code, out_raw, out = http('GET', '/api/tasks/c?proj_id=13')
    if code != 200:
        fail('test_14 #1')
        return False
    elif out is None:
        fail('test_14 #2')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_14 #3')
        return True
    else:
        fail('test_14 #4')
        return False


def test_15():
    #/api/tasks
    code, out_raw, out = http('GET', '/api/tasks?proj_id=13&from=0&count=20')
    if code != 200:
        fail('test_15')
        return False
    elif out is None:
        fail('test_15')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_15')
        return True
    else:
        fail('test_15')
        return False


def test_16():
    #/api/tasks/f
    code, out_raw, out = http('GET', '/api/tasks/f?byid=13')
    if code != 200:
        fail('test_16')
        return False
    elif out is None:
        fail('test_16')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_16')
        return True
    else:
        fail('test_16')
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
        fail('test_17')
        return False
    elif out is None:
        fail('test_17')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_17')
        return True
    else:
        fail('test_17')
        return False


def test_18():
    #/api/tasks/edit_s
    code, out_raw, out = http('POST', '/api/tasks/edit_s', {
        "byid": 13,
        "s": "in_w",
        "desc": "В работе"
    })
    if code != 200:
        fail('test_18')
        return False
    elif out is None:
        fail('test_18')
        return False
    elif 'ans' in out and 'm' in out:
        success('test_18')
        return True
    else:
        fail('test_18')
        return False


def main():
    testing = [
        test_1,
        test_2,
        test_3,
        test_4,
        test_5,
        test_6,
        test_7,
        test_8,
        test_9,
        test_10,
        test_11,
        test_12,
        test_13,
        test_14,
        test_15,
        test_16,
        test_17,
        test_18
    ]
    for test in testing:
        if not test():
            return


if __name__ == '__main__':
    main()