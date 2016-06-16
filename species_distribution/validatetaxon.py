
import logging
from multiprocessing import Pool
import signal
import sys

import species_distribution.distribution as distribution
from species_distribution import sd_io as io
from species_distribution.models.db import Session
from species_distribution.models.validation import ValidationRule,ValidationResult
from species_distribution import settings
from sqlalchemy import exists, and_
import numpy as np


def refreshvalidation():
    with Session() as session:
        rules = session.query(ValidationRule) \
            .filter(and_(ValidationRule.rule_id >=400, ValidationRule.rule_id <= 499))
        for rule in rules:
            session.query("select * from recon.refresh_validation_result_partition(%s)" % rule.rule_id)
    return

def validationresult(taxonkeys):
    with Session() as session:
        results = session.query(ValidationResult) \
            .filter(and_(ValidationResult.rule_id >= 400, ValidationResult.rule_id <= 499))
        for result in results:
            taxalist.append(result.id)
        for taxa in taxalist:
            if taxa in taxonkeys:
                taxonkeys.remove(taxa)
    return taxonkeys








