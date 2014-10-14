__author__ = 'a.medvedev'

import time

UNICODE_UPPER_A = 65
UNICODE_UPPER_Z = 90

UNICODE_LOWER_A = 97
UNICODE_LOWER_Z = 122

UNICODE_DOT = 46
UNICODE_LOW_LINE = 95


def chlat_dot_etc(str):
    for c in str:
        ci = ord(c)
        if not (UNICODE_UPPER_A <= ci <= UNICODE_UPPER_Z) and not \
                (UNICODE_LOWER_A <= ci <= UNICODE_LOWER_Z) and \
                        ci != UNICODE_DOT and \
                        ci != UNICODE_LOW_LINE:
            return False

    return True


def parse_query(q):
    out = {}

    ar = q.split('&')
    for s in ar:
        kvarr = s.split('=')
        if len(kvarr) == 2:
            out[kvarr[0]] = kvarr[1]

    return out


def timestamp():
    return int(time.time() * 1000)