""" DB data source """

from contextlib import contextmanager
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from species_distribution import settings


logger = logging.getLogger(__name__)

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)

engine = create_engine(connection_str, echo=False)
Base = declarative_base()
Base.metadata.bind = engine


@contextmanager
def Session():
    """Provide a transactional scope around a series of operations."""
    try:
        _engine = create_engine(connection_str, echo=False)
        session_maker = sessionmaker(bind=_engine, autocommit=True, autoflush=False)
        session = scoped_session(session_maker)
        yield session
    except Exception as e:
        logger.debug('caught session error: ' + str(e))
        raise
    finally:
        session.close()


class SpecDisModel(Base):
    __abstract__ = True
