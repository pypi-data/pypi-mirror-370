from functools import lru_cache, wraps
from typing import Callable

from flask import request
from flask_basicauth import BasicAuth


class MultiuserBasicAuth(BasicAuth):
    def __init__(
        self,
        app,
        admins: dict[str, str] | None = None,
        users: dict[str, str] | None = None,
        login_callback: Callable | None = None,
        enforce=False,
    ):
        super(MultiuserBasicAuth, self).__init__(app)
        self.admins = admins or {}
        self.users = users or {}
        self.login_callback = login_callback
        self.enforce = enforce

    @lru_cache()
    def check_credentials(self, username: str, password: str, admin: bool):
        if admin:
            success = self.admins.get(username) == password
            if self.login_callback:
                self.login_callback(username, success)
            return success

        if self.users.get(username) == password:
            if self.login_callback:
                self.login_callback(username, True)
            return True
        else:
            return self.check_credentials(username, password, True)

    def authenticate(self, admin):
        auth = request.authorization
        return auth and auth.type == "basic" and self.check_credentials(auth.username, auth.password, admin)

    def user_required(self, view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if (not self.enforce) or self.authenticate(False):
                return view_func(*args, **kwargs)
            else:
                return self.challenge()

        return wrapper

    def admin_required(self, view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if (not self.enforce) or self.authenticate(True):
                return view_func(*args, **kwargs)
            else:
                return self.challenge()

        return wrapper

    def current_user(self) -> str:
        if not self.enforce:
            return "-"

        try:
            auth = request.authorization
            if auth and auth.type == "basic":
                return f"{auth.username}"
            else:
                return "-"
        except RuntimeError:
            return "[suvi]"
