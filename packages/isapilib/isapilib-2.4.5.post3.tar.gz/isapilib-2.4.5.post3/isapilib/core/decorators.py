from django.conf import settings
from django.http import JsonResponse

from rest_framework.exceptions import APIException

from isapilib.core.utilities import is_test
import traceback


def safe_method(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except APIException as e:
            raise e
        except Exception as e:
            if is_test() or settings.DEBUG: traceback.print_exc()
            return JsonResponse({
                'type': str(type(e)),
                'message': str(e)
            }, status=500)

    return wrapped_view
