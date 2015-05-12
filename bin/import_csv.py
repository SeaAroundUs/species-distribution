from sqlalchemy import MetaData

from species_distribution.models import engine, session, GridPoint

metadata = MetaData()
metadata.create_all(engine)
