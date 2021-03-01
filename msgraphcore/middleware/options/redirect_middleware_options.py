class RedirectMiddlewareOptions:
    def __init__(self, redirect_configs: dict):
        self.allow_redirects: bool = redirect_configs.get("allow_redirects")
        self.max_redirects: int = redirect_configs.get("max_redirects")
