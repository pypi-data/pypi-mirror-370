from .db import DBGlobal
from .environment import Environment


class CookieProperties:
    login_cookie_prefix = "chatbot_"
    max_age = 60*60*24*50  # expires in 50 days

    @property
    def login_cookie_path(self):
        return Environment.get_app_root_path(
            DBGlobal.get_config().get("port"))

    @property
    def login_cookies(self):
        return {  # cookies and default values
            "id": DBGlobal.get_config().get("chatbot_id"),
            "username": None,
            "useremail": None,
        }


cookieProperties = CookieProperties()
