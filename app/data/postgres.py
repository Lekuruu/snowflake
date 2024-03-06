
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from contextlib import contextmanager

from .objects import Base

import logging

class Postgres:
    def __init__(self, username: str, database_name: str, password: str, host: str, port: int) -> None:
        self.engine = create_engine(
            f'postgresql://{username}:{password}@{host}:{port}/{database_name}',
            pool_pre_ping=True,
            pool_recycle=900,
            pool_timeout=5,
            echo_pool=None,
            echo=None
        )

        self.engine.dispose()
        Base.metadata.create_all(bind=self.engine)

        self.sessionmaker = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

        self.logger = logging.getLogger('Postgres')

    @property
    def session(self) -> Session:
        return self.sessionmaker(bind=self.engine)

    @contextmanager
    def managed_session(self):
        session = self.sessionmaker(bind=self.engine)
        try:
            yield session
        except Exception as e:
            self.logger.fatal(f'Transaction failed: {e}', exc_info=e)
            self.logger.fatal('Performing rollback...')
            session.rollback()
            raise
        finally:
            session.close()
