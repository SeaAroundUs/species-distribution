""" DB data source """

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

Base = declarative_base()

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)
engine = create_engine(connection_str, echo=False)

# Base.metadata.schema = 'species_distribution'

session_maker = sessionmaker(bind=engine)


@contextmanager
def Session():
    """Provide a transactional scope around a series of operations."""
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SpecDisModel(Base):
    __abstract__ = True
