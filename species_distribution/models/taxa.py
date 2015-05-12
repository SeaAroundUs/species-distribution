""" Taxa data source """

from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.schema import Table

from .db import SpecDisModel, engine, Base


# class Taxon(SpecDisModel):
#     __tablename__ = 'taxon'
#     TaxonKey = Column(Integer(), primary_key=True)
#     Seq = Column(Integer())
#     SuperTarget = Column(Integer())
#     Saup = Column(Integer())
#     Commercial = Column(Integer())
#     TaxGrp = Column(Integer())
#     TaxLevel = Column(Integer())
#     ISSCAAP = Column(Integer())
#     ClaCode = Column(Integer())
#     OrdCode = Column(String())
#     FamCode = Column(String())
#     GenCode = Column(String())
#     SpeCode = Column(String())
#     TaxonName = Column(String())
#     CommonName = Column(String())
#     TargetGrpNum = Column(Integer())

class TaxonPara(SpecDisModel):
    __table__ = Table('qryalltaxon', Base.metadata, Column('taxonkey', Integer(), primary_key=True), autoload=True, autoload_with=engine)


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


# class TaxonParameters(SpecDisModel):
#     __tablename__ = 'taxon_parameters'
#     TaxonKey = Column(Integer(), primary_key=True)
#     HabitatDiversity = Column(Float())
#     EffectiveD = Column(Float())
#     Estuaries = Column(Float())
#     Coral = Column(Float())
#     Seagrass = Column(Float())
#     Seamount = Column(Float())
#     Others = Column(Float())
#     Shelf = Column(Float())
#     Slope = Column(Float())
#     Abyssal = Column(Float())
#     Inshore = Column(Float())
#     Offshore = Column(Float())
#     Offshore_Back = Column(Float())


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

