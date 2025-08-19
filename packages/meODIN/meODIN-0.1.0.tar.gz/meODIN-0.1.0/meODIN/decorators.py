from functools import wraps

def requires_auth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "has_token", False):
            raise PermissionError(f"Function '{func.__name__}' requires a valid token.")
        return func(self, *args, **kwargs)
    return wrapper
