##
# File: formulaMatch.py
# Date: 12-Mar-2020
#
##
# pylint: skip-file
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
from typing import Dict, List
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder

# pylint disable=no-name-in-module
from pydantic import BaseModel, Field  # pylint disable=no-name-in-module

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper
from rcsb.app.chem.ElementSymbol import ElementSymbol

logger = logging.getLogger(__name__)

router = APIRouter()


class ElementRange(BaseModel):
    min: int = Field(None, ge=0, title="Mininum element count", description="Minimum number of occurences of element in molecular formula (inclusive)")
    max: int = Field(None, ge=0, title="Maximum element count", description="Maximum number of occurences of element in molecular formula (inclusive)")


class FormulaQuery(BaseModel):
    query: str = Field(None, title="Molecular formula", description="Molecular formula (ex. C8H9NO2)", example="C8H9NO2")
    matchSubset: bool = Field(False, title="Formula subsets", description="Match formulas satisfying only the subset of query the conditions", example=False)


class FormulaQueryResult(BaseModel):
    query: str = Field(None, title="Molecular formula", description="Molecular formula (ex. C8H9NO2)", example="C8H9NO2")
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes", example=["004"])


class FormulaRangeQuery(BaseModel):
    query: Dict[ElementSymbol, ElementRange] = Field(
        None,
        title="Formula query dictionary",
        description="Dictionary representing a formula query as a dictionary of element symbols and minimum and maximum boundary conditions",
        example={"C": {"min": 5, "max": 9}, "H": {"min": 5, "max": 10}, "N": {"min": 1, "max": 1}, "O": {"min": 1, "max": 3}},
    )
    matchSubset: bool = Field(False, title="Match formula subsets", description="Match formulas satisfying only the subset of query the conditions", example="False")


class FormulaRangeQueryResult(BaseModel):
    query: Dict[str, ElementRange] = Field(
        None,
        title="Formula range query dictionary",
        description="Dictionary representing a formula query as a dictionary of element symbols and minimum and maximum boundary conditions",
        example={"C": {"min": 5, "max": 9}, "H": {"min": 5, "max": 10}, "N": {"min": 1, "max": 1}, "O": {"min": 1, "max": 3}},
    )
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes", example=["004"])


@router.get("/formula", tags=["formula"], response_model=FormulaQueryResult)
def matchGetQuery(
    query: str = Query(None, title="Molecular formula", description="Molecular formula (ex. C8H9NO2)", example="C8H9NO2"),
    matchSubset: bool = Query(False, title="Formula subsets", description="Find formulas satisfying only the subset of query the conditions", example=False),
):
    logger.debug("Got %r", query)
    # ---
    ccsw = ChemCompSearchWrapper()
    logger.debug("matchSubset %r", matchSubset)
    retStatus, matchResultL = ccsw.matchByFormula(query, matchSubset=matchSubset)
    logger.info("Results (%r) rL (%d)", retStatus, len(matchResultL))
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": query, "matchedIdList": rL}


@router.post("/formula", tags=["formula"], response_model=FormulaQueryResult)
def matchPostQuery(query: FormulaQuery):
    logger.debug("Got %r", query)
    qD = jsonable_encoder(query)
    logger.info("qD %r", qD)
    #
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, matchResultL = ccsw.matchByFormula(qD["query"], matchSubset=qD["matchSubset"])
    logger.info("Results (%r) rL (%d)", retStatus, len(matchResultL))
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": qD["query"], "matchedIdList": rL}


@router.post("/formula/range", tags=["formula"], response_model=FormulaRangeQueryResult)
def matchRangePostQuery(query: FormulaRangeQuery):
    logger.debug("Got %r", query)
    qD = jsonable_encoder(query)
    logger.debug("qD %r", qD)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, matchResultL = ccsw.matchByFormulaRange(qD["query"], qD["matchSubset"])
    logger.info("Results (%r) rL (%d)", retStatus, len(matchResultL))
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": qD["query"], "matchedIdList": rL}
