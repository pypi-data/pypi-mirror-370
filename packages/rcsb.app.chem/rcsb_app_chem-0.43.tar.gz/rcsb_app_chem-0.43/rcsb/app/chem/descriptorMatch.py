##
# File: descriptionMatch.py
# Date: 13-Mar-2020 jdw
#
# Updates:
#   23-Oct-2020 jdw add substructure search options
##
# pylint: skip-file

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging

from collections import namedtuple
from enum import Enum
from typing import List
from fastapi import APIRouter, Path, Query
from fastapi.encoders import jsonable_encoder

# pylint disable=no-name-in-module
from pydantic import BaseModel, Field

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

logger = logging.getLogger(__name__)

MatchResults = namedtuple("MatchResults", "ccId oeMol searchType matchOpts screenType fpType fpScore oeIdx formula", defaults=(None,) * 9)

router = APIRouter()


class DescriptorType(str, Enum):
    smiles = "SMILES"
    inchi = "InChI"


class DescriptorMatchType(str, Enum):
    exact = "graph-exact"
    relaxed = "graph-relaxed"
    relaxedStereo = "graph-relaxed-stereo"
    strict = "graph-strict"
    fuzzy = "fingerprint-similarity"
    exactSubStructure = "sub-struct-graph-exact"
    relaxedSubStructure = "sub-struct-graph-relaxed"
    relaxedStereoSubStructure = "sub-struct-graph-relaxed-stereo"
    strictSubStructure = "sub-struct-graph-strict"


class DescriptorQuery(BaseModel):
    query: str = Field(None, title="Descriptor string", description="SMILES or InChI chemical descriptor", example="c1ccc(cc1)[C@@H](C(=O)O)N")
    # generator: str = Field(None, title="Descriptor generator", description="Program or agent generating the descriptor", example="OpenEye Toolkit")
    matchType: DescriptorMatchType = Field(
        None,
        title="Query match type",
        description="""Graph matching, fingerprint similarity and substructure search:
            graph-exact (with fingerprint prefilter) (match criteria: atom type, formal charge, aromaticity, bond order, atom/bond stereochemistry,
                                                      degree, ring membersip, hydrogen count),
            graph-strict (with fingerprint prefilter) (match criteria: atom type, formal charge, aromaticity, bond order, atom/bond stereochemistry,
                                                       degree, ring membersip),
            graph-relaxed (with fingerprint prefilter) (match criteria: atom type, formal charge, bond type, aromaticity),
            graph-relaxed-stereo (with fingerprint prefilter) (match criteria: atom type, formal charge, bond type, aromaticity, atom/bond stereochemistry),
            fingerprint-similarity (TREE and MACCS),
            sub-struct-graph-exact (match criteria: atom type, formal charge, aromaticity, bond order, atom/bond stereochemistry,
                                    degree, ring membersip, hydrogen count),
            sub-struct-graph-strict (match criteria: atom type, formal charge, aromaticity, bond order, atom/bond stereochemistry,
                                     degree, ring membersip),
            sub-struct-graph-relaxed (match criteria: atom type, formal charge, bond type, aromaticity,),
            sub-struct-graph-relaxed-stereo (match criteria: atom type, formal charge, bond type, aromaticity, atom/bond stereochemistry),
        """,
        example="graph-relaxed",
    )


class DescriptorQueryResult(BaseModel):
    query: str = Field(None, title="Descriptor query string", description="SMILES or InChI chemical descriptor", example="c1ccc(cc1)[C@@H](C(=O)O)N")
    descriptorType: DescriptorType = Field(None, title="Descriptor type", description="SMILES or InChI", example="SMILES")
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes", example=["004"])
    matchedScoreList: List[float] = Field(None, title="Match scores", description="Match scores from fingerprint screen (1.0 - 0.0)", example=[0.99, 0.92, 0.90])


@router.get("/{descriptorType}", response_model=DescriptorQueryResult, tags=["descriptor"])
def matchGetQuery(
    query: str = Query(None, title="Descriptor string", description="SMILES or InChI chemical descriptor", example="c1ccc(cc1)[C@@H](C(=O)O)N"),
    matchType: DescriptorMatchType = Query(
        "graph-relaxed", title="Query match type", description="Qualitative graph matching or fingerprint comparison criteria", example="graph-relaxed"
    ),
    descriptorType: DescriptorType = Path(..., title="Descriptor type", description="Type of chemical descriptor (SMILES or InChI)", example="SMILES"),
):
    matchType = matchType if matchType else "graph-relaxed"
    logger.info("Got %r %r %r", descriptorType, query, matchType)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, ssL, fpL = ccsw.searchByDescriptor(query, descriptorType, matchOpts=matchType)
    logger.info("Result (%r) ssL (%d) fpL (%d)", retStatus, len(ssL), len(fpL))
    qL = fpL if matchType in ["fingerprint-similarity"] else ssL
    rD = {}
    for mr in qL:
        ccId = mr.ccId.split("|")[0]
        rD[ccId] = max(rD[ccId], mr.fpScore) if ccId in rD else mr.fpScore
    rTupL = sorted(rD.items(), key=lambda kv: kv[1], reverse=True)
    rL = [rTup[0] for rTup in rTupL]
    scoreL = [rTup[1] for rTup in rTupL]
    # ---
    return {"query": query, "descriptorType": descriptorType, "matchedIdList": rL, "matchedScoreList": scoreL}


@router.post("/{descriptorType}", response_model=DescriptorQueryResult, tags=["descriptor"])
def matchPostQuery(
    query: DescriptorQuery,
    descriptorType: DescriptorType = Path(..., title="Descriptor type", description="Type of chemical descriptor (SMILES or InChI)", example="SMILES"),
):

    logger.info("Got %r %r", descriptorType, query)
    qD = jsonable_encoder(query)
    logger.debug("qD %r", qD)
    matchType = qD["matchType"] if "matchType" in qD and qD["matchType"] else "graph-relaxed"
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, ssL, fpL = ccsw.searchByDescriptor(qD["query"], descriptorType, matchOpts=matchType)
    logger.info("Results (%r) ssL (%d) fpL (%d)", retStatus, len(ssL), len(fpL))
    #
    qL = fpL if matchType in ["fingerprint-similarity"] else ssL
    rD = {}
    for mr in qL:
        ccId = mr.ccId.split("|")[0]
        rD[ccId] = max(rD[ccId], mr.fpScore) if ccId in rD else mr.fpScore
    rTupL = sorted(rD.items(), key=lambda kv: kv[1], reverse=True)
    rL = [rTup[0] for rTup in rTupL]
    scoreL = [rTup[1] for rTup in rTupL]
    # ---
    return {"query": query.query, "descriptorType": descriptorType, "matchedIdList": rL, "matchedScoreList": scoreL}
