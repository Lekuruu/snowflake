
from importlib import import_module
from sqlalchemy.orm import Session
from functools import wraps
from typing import Any

"""
Used with `session: Session = SessionProvider` in repository functions.
When @session_wrapper is used, this will guarantee that a session is always provided, either by the caller or by the wrapper itself.
"""
SessionProvider: Any | Session = ...

def session_wrapper(func):
    """Function wrapper for database session management.

    Example usage:
    ```
    @session_wrapper
    def fetch_one(id: int, session: Session = SessionProvider) -> YourModel:
        return session.query(YourModel).all()

    fetch_one(1)                   # Will use a new session
    fetch_one(1, session=session)  # Will use the existing session
    ```
    """
    app_state = import_module('app.session')
    assert hasattr(app_state, 'database'), "application state must have a 'database' instance"

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('session'):
            # Use existing session
            return func(*args, **kwargs)

        if args and isinstance(args[-1], Session):
            # Use existing session
            return func(*args, **kwargs)

        with app_state.database.managed_session() as session:
            # Get new session for this function
            kwargs['session'] = session
            return func(*args, **kwargs)

    return wrapper
