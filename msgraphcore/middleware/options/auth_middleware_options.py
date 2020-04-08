from msgraphcore.constants import BASE_URL


class AuthMiddlewareOptions:
    def __init__(self, scopes=[]):
        self.scopes = scopes

    @property
    def scopes(self):
        return self._scopes

    @scopes.setter
    def scopes(self, list_of_scopes):
        if type(list_of_scopes) == list:
            graph_scopes = BASE_URL + '?scopes='

            for scope in list_of_scopes:
                graph_scopes += scope + '%20'

            self._scopes = graph_scopes
        elif type(list_of_scopes) == str:
            self._scopes = list_of_scopes
