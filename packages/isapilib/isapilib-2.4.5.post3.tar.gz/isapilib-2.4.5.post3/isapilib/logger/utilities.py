import json
import sys
from datetime import timezone, datetime

from isapilib.api.models import ApiLogs


def get_response_content(response) -> str:
    try:
        return str(response.data)
    except Exception:
        return str(response.content.decode('utf-8'))


def insert_log(request, response, interfaz, tipo, time=0):
    if 'test' in sys.argv: return
    try:
        response_content = get_response_content(response)
        log = ApiLogs()
        log.iduser = request.user.pk
        log.tipo = str(tipo or '')
        log.header = str(json.dumps(dict(request.headers)))
        log.request = str(json.dumps(request.data) if isinstance(request.data, (dict, list)) else request.data or '')
        log.response = str(response_content or '')
        log.status = response.status_code if hasattr(response, 'status_code') else 0
        log.url = request.build_absolute_uri()
        log.interfaz = str(interfaz or '')
        log.response_time = time
        log.fecharegistro = datetime.now(tz=timezone.utc)
        log.save(using='default')
    except Exception as e:
        print(f'Warning: Failed to save logs, ({type(e)}) {e}')
