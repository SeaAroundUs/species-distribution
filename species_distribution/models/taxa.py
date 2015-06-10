""" Taxa data source """

from sqlalchemy import Column, Integer, Float
from sqlalchemy.schema import Table

from .db import SpecDisModel, engine, Base


class TaxonPara(SpecDisModel):
    __table__ = Table(
        'qryalltaxon',
        Base.metadata,
        Column('taxonkey', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine
    )

    def __str__(self):
        return str(self.taxonkey)

    @property
    def faos(self):
        """returns a list of FAO regions this taxon is found in"""

        ids = [18, 21, 27, 31, 34, 37, 41, 47, 48, 51, 57, 58, 61, 67,
            71, 77, 81, 87, 88]

        return list(filter(lambda id: getattr(self, 'fao'+str(id)) == 1, ids))

    @property
    def pelagic(self):
        return self.sppgroup or 3


# TaxonPara = Table('qryalltaxon', Base.metadata, autoload=True, autoload_with=engine)

class TaxonParameters(SpecDisModel):
    __tablename__ = 'taxon_parameters'
    TaxonKey = Column(Integer(), primary_key=True)
    HabitatDiversity = Column(Float())
    EffectiveD = Column(Float())
    Estuaries = Column(Float())
    Coral = Column(Float())
    Seagrass = Column(Float())
    Seamount = Column(Float())
    Others = Column(Float())
    Shelf = Column(Float())
    Slope = Column(Float())
    Abyssal = Column(Float())
    Inshore = Column(Float())
    Offshore = Column(Float())
    Offshore_Back = Column(Float())


class TaxonHabitat(SpecDisModel):
    __tablename__ = 'taxon_habitat'

    TaxonKey = Column(Integer(), primary_key=True)
    TaxLevel = Column(Integer())
    ClaCode = Column(Integer())
    OrdCode = Column(Integer())
    FamCode = Column(Integer())
    GenCode = Column(Integer())
    SpeCode = Column(Integer())
    HabitatDiversityIndex = Column(Float())
    EffectiveD = Column(Float())
    Estuaries = Column(Float())
    Coral = Column(Float())
    Seagrass = Column(Float())
    Seamount = Column(Float())
    Others = Column(Float())
    Shelf = Column(Float())
    Slope = Column(Float())
    Abyssal = Column(Float())
    Inshore = Column(Float())
    Offshore = Column(Float())
    Offshore_Back = Column(Float())
