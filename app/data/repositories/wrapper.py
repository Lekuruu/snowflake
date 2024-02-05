
from sqlalchemy.orm import Session
from functools import wraps
import app.session

def session_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('session'):
            # Use existing session
            return func(*args, **kwargs)

        if args and isinstance(args[-1], Session):
            # Use existing session
            return func(*args, **kwargs)

        with app.session.database.managed_session() as session:
            # Get new session for this function
            kwargs['session'] = session
            return func(*args, **kwargs)

    return wrapper
