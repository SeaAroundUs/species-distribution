""" DB data source """

from contextlib import contextmanager
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from species_distribution import settings


connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)

logger = logging.getLogger(__name__)

def get_engine():

    return create_engine(
        connection_str,
        echo=False,
        poolclass=NullPool,
        isolation_level='READ UNCOMMITTED'
    )

Base = declarative_base()
Base.metadata.bind = get_engine()

@contextmanager
def Session():
    """Provide a transactional scope around a series of operations."""
    try:
        engine = get_engine()
        session_maker = sessionmaker(bind=engine, autocommit=True) # autocommit=True, autoflush=False, expire_on_commit=False)
        session = session_maker()
        yield session

    except Exception as e:
        logger.debug('caught session error: ' + str(e))
        raise
    finally:
        session.close()


class SpecDisModel(Base):
    __abstract__ = True
