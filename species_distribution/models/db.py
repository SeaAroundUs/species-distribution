""" DB data source """

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

Base = declarative_base()

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)
engine = create_engine(connection_str, echo=False)

# Base.metadata.schema = 'species_distribution'


def session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class SpecDisModel(Base):
    __abstract__ = True