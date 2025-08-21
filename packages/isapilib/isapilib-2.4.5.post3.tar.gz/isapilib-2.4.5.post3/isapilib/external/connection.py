from django.conf import settings
from django.db import connections

from isapilib.api.models import SepaBranch, SepaBranchUsers
from isapilib.core.exceptions import SepaException
from isapilib.core.utilities import is_test


def add_conn(user, branch: SepaBranch):
    conn_name = f'external-{branch.id}'

    if conn_name in connections.databases:
        connections.databases[conn_name] = create_conn(branch)
        return conn_name

    if not SepaBranchUsers.objects.filter(iduser=user, idbranch=branch).exists():
        raise SepaException('You do not have permissions on the agency', user, branch)

    if is_test() and not branch.allow_test:
        raise SepaException(f'Test is not allowed at this agency {branch.pk}', user, branch)

    connections.databases[conn_name] = create_conn(branch)
    return conn_name


def get_version(version=6000):
    version = version or 6000

    if 5000 > version >= 4000:
        return '4000'

    return '6000'


def create_conn(_branch):
    return {
        'ENGINE': 'mssql',
        'NAME': _branch.conf_db if _branch.conf_db else '',
        'USER': _branch.conf_user if _branch.conf_user else '',
        'PASSWORD': _branch.conf_pass if _branch.conf_pass else '',
        'HOST': _branch.conf_ip_ext if _branch.conf_ip_ext else '',
        'PORT': _branch.conf_port if _branch.conf_port else '',
        'INTELISIS_VERSION': get_version(_branch.version),
        'TIME_ZONE': None,
        'CONN_HEALTH_CHECKS': None,
        'CONN_MAX_AGE': None,
        'ATOMIC_REQUESTS': None,
        'AUTOCOMMIT': True,
        'OPTIONS': settings.DATABASES['default'].get('OPTIONS')
    }
