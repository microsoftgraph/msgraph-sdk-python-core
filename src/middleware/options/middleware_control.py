class MiddlewareControl:
    def __init__(self):
        self.middleware_options = {}

    def set(self, middleware_option_name, middleware_option):
        self.middleware_options.update({middleware_option_name: middleware_option})

    def get(self, middleware_option_name):
        return self.middleware_options.get(middleware_option_name, None)
