import threading

from rest_framework.permissions import BasePermission

_thread_local = threading.local()


class IsapilibPermission(BasePermission):
    def has_permission(self, request, view):
        self.set_current_request(request)
        return True

    @staticmethod
    def get_current_request():
        return getattr(_thread_local, 'request', None)

    @staticmethod
    def set_current_request(request):
        _thread_local.request = request
