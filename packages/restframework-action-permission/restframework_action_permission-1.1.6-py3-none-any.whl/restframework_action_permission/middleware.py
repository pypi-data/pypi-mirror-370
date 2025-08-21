from django.http.request import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class AuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if isinstance(request.user, AnonymousUser):
            request._force_auth_user = get_user_model().objects.get(id=1)
        response = self.get_response(request)
        return response
