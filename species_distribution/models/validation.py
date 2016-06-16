""" World data source """

from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table
from sqlalchemy import and_
from .db import SpecDisModel, Base, Session


class ValidationRule(SpecDisModel):
    __table__ = Table(
        'validation_rule',
        Base.metadata,
        Column('rule_id', Integer(), primary_key=True),
        autoload=True,
        extend_existing=True
    )


class ValidationResult(SpecDisModel):
    __table__ = Table(
        'validation_result',
        Base.metadata,
        autoload=True,
        extend_existing=True
    )


def refresh_validation_rules():
    with Session() as session:
        rules = session.query(ValidationRule) \
            .filter(and_(ValidationRule.rule_id >=400, ValidationRule.rule_id <= 499)) \
            .all()

        for rule in rules:
            session.query("select * from recon.refresh_validation_result_partition(%s)" % rule.rule_id)


def filter_taxa_against_validation_results(taxonkeys):
    if taxonkeys and len(taxonkeys) > 0:
        with Session() as session:
            results = session.execute("select distinct rs.id from recon.validation_result rs where rule_id between 400 and 499")

            for result in results:
                errorTaxon = result.id
                if errorTaxon in taxonkeys:
                    taxonkeys.remove(errorTaxon)

    return taxonkeys
