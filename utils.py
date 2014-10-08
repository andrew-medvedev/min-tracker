__author__ = 'a.medvedev'


def chlat_dot_etc(str):
    for c in str:
        ci = ord(c)
        if not (65 <= ci <= 90) and not (97 <= ci <= 122) and ci != 46 and ci != 95:
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