__author__ = 'a.medvedev'

import web_tier
import sys


def main():
    if len(sys.argv) != 3:
        print('NOPE!')
    else:
        print('go on host {} and port {}'.format(sys.argv[1], sys.argv[2]))
        web_tier.init_web_tier(sys.argv[1], int(sys.argv[2]))

if __name__ == '__main__':
    main()
