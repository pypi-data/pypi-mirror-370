from datetime import timezone

from starlette.requests import Request


class ContextUtils:
    def __init__(self, request: Request):
        self.request = request
        self.headers = dict(request.headers)

    def get_timezone(self):
        return self.headers.get("x-timezone")

    def get_locale(self):
        return self.headers.get("x-locale")