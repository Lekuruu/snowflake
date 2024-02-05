
from sqlalchemy.orm import Session
from functools import wraps
import app.session

def session_wrapper(func):
    """Function wrapper for database session management.

    Example usage:
    ```
    @session_wrapper
    def fetch_one(id: int, session: Session | None = None) -> YourModel:
        return session.query(YourModel).all()

    fetch_one(1)                   # Will use a new session
    fetch_one(1, session=session)  # Will use the existing session
    ```
    """
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
