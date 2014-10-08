__author__ = 'a.medvedev'


def chlat_dot_etc(str):
    for c in str:
        ci = ord(c)
        if ci < 65 and ci > 90 and ci < 97 and ci > 122 and ci != 46 and ci != 95:
            return False

    return True
    # TODO make a unit test