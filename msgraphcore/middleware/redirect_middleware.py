from msgraphcore.middleware.middleware import BaseMiddleware


class RedirectMiddleware(BaseMiddleware):
    _DEFAULT_REDIRECT_CODES = [301, 302, 303, 307, 308]

    def __init__(self, redirect_configs: dict):
        self.allow_redirects: bool = redirect_configs.get("allow_redirects")
        self.max_redirects: int = redirect_configs.get("max_redirects")

        status_codes: [int] = redirect_configs.pop('redirect_on_status_codes', [])

        self._redirect_on_status_codes = set(status_codes) | set(self._DEFAULT_REDIRECT_CODES)

    @classmethod
    def disallow_redirects(cls):
        """Disallows redirection of requests"""
        return cls(redirect_configs={"allow_redirects": False})

    def configure_redirect_settings(self):
        """Configure redirect settings into the form of a dict."""
        return {
            'allow': self.allow_redirects,
            'max': self.max_redirects,
        }
