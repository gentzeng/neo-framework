from django.conf import settings

from .utils import ReactWrapper

LOGIN_URL = settings.LOGIN_URL
ALLOWED_HOSTS = settings.ALLOWED_HOSTS


class LoginResearcherView(ReactWrapper):
    httpCodes = {
        "successGoToNext": [200],
        "clientErrors": [400, 401],
    }
    fieldNames = ["username", "password"]
    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "headline": "Login as researcher",
        "submitButtonLabel": "Login",
        "goToButtonLabel": "Sign up",
        "submitURL": "/api/auth/login-researcher/",
        "goToURL": "/sign-up-researcher/",
        "nextURL": "/dashboard/",
        "httpCodes": httpCodes,
        "fieldNames": fieldNames,
    }


class SignUpResearcherView(ReactWrapper):
    httpCodes = {
        "successGoToNext": [201],
        "clientErrors": [400],
    }
    fieldNames = [
        "username",
        "email",
        "password",
        "confirm_password",
        "first_name",
        "last_name",
    ]
    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "headline": "Sign up as researcher",
        "submitButtonLabel": "Sign up",
        "goToButtonLabel": "Login",
        "submitURL": "/api/auth/sign-up-researcher/",
        "goToURL": LOGIN_URL,
        "nextURL": LOGIN_URL,
        "httpCodes": httpCodes,
        "fieldNames": fieldNames,
    }
