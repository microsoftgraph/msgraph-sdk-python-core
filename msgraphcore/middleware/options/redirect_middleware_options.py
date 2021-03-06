class RedirectMiddlewareOptions:
    def __init__(self, redirect_configs: dict):
        self.allow_redirects: bool = redirect_configs.get("allow_redirects")
        self.total_redirects: int = redirect_configs.get("total_redirects")
        self.redirect_status_codes: [int] = redirect_configs.get("redirect_on_status_codes")
