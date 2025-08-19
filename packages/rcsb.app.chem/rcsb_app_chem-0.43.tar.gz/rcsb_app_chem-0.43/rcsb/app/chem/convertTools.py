##
# File: convertTools.py
# Date: 10-Decmber-2020 jdw
#
# Updates:
#
##
# pylint: skip-file

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging

from enum import Enum

# from typing import List
from fastapi import APIRouter, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

# pylint disable=no-name-in-module
from pydantic import BaseModel, Field

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper

logger = logging.getLogger(__name__)

router = APIRouter()


class ConvertIdentifierType(str, Enum):
    smiles = "SMILES"
    inchi = "InChI"
    identifierPdb = "IdentifierPDB"


class MoleculeFormatType(str, Enum):
    mol = "mol"
    sdf = "sdf"
    mol2 = "mol2"
    mol2h = "mol2h"


class ConvertMoleculeIdentifier(BaseModel):
    target: str = Field(None, title="Descriptor string", description="SMILES or InChI chemical descriptor", example="c1ccc(cc1)[C@@H](C(=O)O)N")
    fmt: MoleculeFormatType = Field(None, title="Molecule format", description="Molecule format type (mol, sdf, mol2, mol2h)", example="mol")


@router.get("/to-molfile/{convertIdentifierType}", tags=["convert"])
def toMolFileGet(
    target: str = Query(None, title="Target molecule identifier", description="SMILES, InChI or PDB identifier", example="c1ccc(cc1)[C@@H](C(=O)O)N"),
    fmt: MoleculeFormatType = Query(None, title="Molecule format type", description="Molecule format type (mol, sdf, mol2, mol2h)", example="mol"),
    convertIdentifierType: ConvertIdentifierType = Path(
        ..., title="Molecule identifier type", description="Molecule identifier type (SMILES, InChI or PDB identifier)", example="SMILES"
    ),
):
    logger.debug("Got %r %r %r", convertIdentifierType, target, fmt)
    # ---
    fmt = fmt.lower() if fmt else "mol"
    ccdw = ChemCompDepictWrapper()
    molfilePath = ccdw.toMolFile(target, convertIdentifierType, fmt=fmt)
    mimeTypeD = {"mol": "chemical/x-mdl-molfile", "sdf": "chemical/x-mdl-sdfile", "mol2": "chemical/x-mol2", "mol2h": "chemical/x-mol2"}
    mType = mimeTypeD[fmt]
    # ---
    return FileResponse(molfilePath, media_type=mType)


@router.post("/to-molfile/{convertIdentifierType}", tags=["convert"])
def toMolFilePost(
    target: ConvertMoleculeIdentifier,
    convertIdentifierType: ConvertIdentifierType = Path(
        ..., title="Molecule identifier type", description="Type of molecule identifier (SMILES, InChI or PDB identifier)", example="SMILES"
    ),
):
    qD = jsonable_encoder(target)
    logger.debug("qD %r", qD)
    fmt = qD["fmt"].lower() if "fmt" in qD and qD["fmt"] else "mol"
    logger.debug("Got %r %r %r", convertIdentifierType, target, fmt)
    # --
    ccdw = ChemCompDepictWrapper()
    molfilePath = ccdw.toMolFile(qD["target"], convertIdentifierType, fmt=fmt)
    mimeTypeD = {"mol": "chemical/x-mdl-molfile", "sdf": "chemical/x-mdl-sdfile", "mol2": "chemical/x-mol2", "mol2h": "chemical/x-mol2"}
    mType = mimeTypeD[fmt]
    # ---
    return FileResponse(molfilePath, media_type=mType)
