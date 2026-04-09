import uuid
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.deprecation import MiddlewareMixin

class NewSessionOnLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.session.session_key is None:
            # User is logging in and has no session ID
            request.session.cycle_key()