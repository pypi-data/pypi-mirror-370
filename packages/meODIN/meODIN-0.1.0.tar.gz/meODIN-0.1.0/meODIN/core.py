from .auth import Authenticator

class BaseSecuredLib:
    def __init__(self, token=None):
        self.token = token
        self.authenticator = Authenticator(token) if token else None
        self.has_token = self.authenticator.is_token_valid() if self.authenticator else False

    def refresh_token(self):
        if self.authenticator:
            self.has_token = self.authenticator.is_token_valid()
        else:
            self.has_token = False
        return self.has_token
