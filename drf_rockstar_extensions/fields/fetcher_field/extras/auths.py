class BaseAuth:
    name = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs

    @classmethod
    def get_auth(cls, **kwargs):
        return {}


class BasicAuth(BaseAuth):
    name = 'basic'

    @classmethod
    def get_auth(cls, **kwargs):
        return {
            'auth': (None, None)
        }
