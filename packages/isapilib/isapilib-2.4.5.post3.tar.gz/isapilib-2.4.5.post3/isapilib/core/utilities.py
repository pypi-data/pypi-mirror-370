import sys


def to_bool(s):
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        s = s.lower()
        if s in ['true', '1', 'yes']:
            return True
        elif s in ['false', '0', 'no']:
            return False
        else:
            return False
    return False


def get_sucursal_from_request(request):
    return int(request.user.id_intelisis or 0)


def is_test():
    return sys.argv[1] == 'test'
