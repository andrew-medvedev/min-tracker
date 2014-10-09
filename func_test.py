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
    pass


def test_3():
    #/api/logout
    pass


def test_4():
    #/api/projects/c
    pass


def test_5():
    #/api/projects
    pass


def test_6():
    #/api/projects/f
    pass


def test_7():
    #/api/memb/add
    pass


def test_8():
    #/api/memb/rem
    pass


def test_9():
    #/api/memb/chr
    pass


def test_10():
    #/api/projects/add
    pass


def test_11():
    #/api/project/hie/add
    pass


def test_12():
    #/api/projects/hie/rem
    pass


def test_13():
    #/api/projects/edit
    pass


def test_14():
    #/api/tasks/c
    pass


def test_15():
    #/api/tasks
    pass


def test_16():
    #/api/tasks/f
    pass


def test_17():
    #/api/tasks/edit
    pass


def test_18():
    #/api/tasks/edit_s
    pass


def main():
    pass


if __name__ == '__main__':
    main()