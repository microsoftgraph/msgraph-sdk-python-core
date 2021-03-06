from msgraphcore.middleware.middleware import BaseMiddleware
from msgraphcore.middleware.options.middleware_control import middleware_control


class RedirectMiddleware(BaseMiddleware):
    DEFAULT_ALLOW_REDIRECTS = True
    DEFAULT_TOTAL_REDIRECTS = 5
    MAX_MAX_REDIRECTS = 20
    DEFAULT_REDIRECT_CODES = frozenset([301, 302, 303, 307, 308])

    def __init__(self, redirect_configs: dict = {}):
        self.allow_redirects: bool = redirect_configs.pop(
            "allow_redirects", self.DEFAULT_ALLOW_REDIRECTS
        )
        self.total_redirects: int = min(
            redirect_configs.pop("total_redirects", self.DEFAULT_TOTAL_REDIRECTS),
            self.MAX_MAX_REDIRECTS
        )

        redirect_codes: [int] = redirect_configs.pop('redirect_on_status_codes', [])

        self._redirect_status_codes = set(redirect_codes) | set(self.DEFAULT_REDIRECT_CODES)

    @classmethod
    def disallow_redirects(cls):
        """Disallows redirection of requests"""
        return cls(redirect_configs={"allow_redirects": False})

    def get_redirect_options(self):
        """
        Check if request specific redirect configs have been passed and override session defaults
        Then return these options in the form of a dict.
        """
        redirect_config_options = middleware_control.get('REDIRECT_MIDDLEWARE_OPTIONS')
        if redirect_config_options:
            return {
                'allow_redirects':
                redirect_config_options.allow_redirects
                if redirect_config_options.allow_redirects is not None else self.allow_redirects,
                'total_redirects':
                min(redirect_config_options.total_redirects, self.MAX_MAX_REDIRECTS)
                if redirect_config_options.total_redirects is not None else self.total_redirects,
                'redirect_codes':
                set(redirect_config_options.redirect_status_codes)
                | set(self.DEFAULT_REDIRECT_CODES) if redirect_config_options.redirect_status_codes
                is not None else self._redirect_status_codes,
            }
        return {
            'allow_redirects': self.allow_redirects,
            'total_redirects': self.total_redirects,
            'redirect_codes': self._redirect_status_codes,
        }
