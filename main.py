"""
Программе нужны аргументы запуска:

 -> host - адрес, на котором будет запущен web-сервер Tornado
 -> port - порт для web-сервера
 -> log - уровень логов
"""

__author__ = 'a.medvedev'

import web_tier
import sys
import logging


def main():
    # args = parse_arguments()
    # if args is None:
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.WARN)
    #     logging.warning('Invalid program arguments')
    #     return
    # if args['log'].upper() == 'DEBUG':
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)
    # elif args['log'].upper() == 'INFO':
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    # elif args['log'].upper() == 'WARN' or args['log'].upper() == 'WARNING':
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.WARNING)
    # elif args['log'].upper() == 'ERROR':
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.ERROR)
    # elif args['log'].upper() == 'CRITICAL':
    #     logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.CRITICAL)
    #
    # logging.info('go on host {} and port {}'.format(args['host'], args['port']))
    # web_tier.init_web_tier(args['host'], int(args['port']))
    import json
    str = r'{"lala1": "shit", "lala2":1337, "lala3": 13.37, "lala4":true, "lala5":{}, "lala6":[]}'
    j = json.loads(str)
    for k in j:
        print('k = {}, v = {}, type = {}'.format(k, j[k], type(j[k])))


def parse_arguments():
    out = {}

    for s in sys.argv[1:]:
        kv = s.split('=')
        if len(kv) != 2:
            continue
        out[kv[0]] = kv[1]
    if 'host' not in out or 'port' not in out or 'log' not in out:
        out = None

    return out

if __name__ == '__main__':
    main()
