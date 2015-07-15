""" DB data source """

from contextlib import contextmanager
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings


logger = logging.getLogger(__name__)

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)

engine = create_engine(connection_str, echo=False)
Base = declarative_base()
Base.metadata.bind = engine


@contextmanager
def Session():
    """Provide a transactional scope around a series of operations."""
    _engine = create_engine(connection_str, echo=False)
    session_maker = sessionmaker(bind=_engine)

    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.debug('rolling back. Error: ' + str(e))
        session.rollback()
        raise
    finally:
        session.close()


class SpecDisModel(Base):
    __abstract__ = True
