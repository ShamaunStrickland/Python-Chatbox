from functools import wraps
from threading import Thread


def before(f, chain=False):
    """Runs f before the decorated function."""
    def decorator(g):
        @wraps(g)
        def h(*args, **kargs):
            if chain:
                return g(f(*args, **kargs))
            else:
                f(*args, **kargs)
                return g(*args, **kargs)
        return h
    return decorator


def after(f, chain=False):
    """Runs f with the result of the decorated function."""
    def decorator(g):
        @wraps(g)
        def h(*args, **kargs):
            if chain:
                return f(g(*args, **kargs))
            else:
                r = g(*args, **kargs)
                f(*args, **kargs)
                return r
        return h
    return decorator


def during(f):
    """Runs f during the decorated function's execution in a separate thread."""
    def decorator(g):
        @wraps(g)
        def h(*args, **kargs):
            tf = Thread(target=f, args=args, kwargs=kargs)
            tf.start()
            r = g(*args, **kargs)
            tf.join()
            return r
        return h
    return decorator
