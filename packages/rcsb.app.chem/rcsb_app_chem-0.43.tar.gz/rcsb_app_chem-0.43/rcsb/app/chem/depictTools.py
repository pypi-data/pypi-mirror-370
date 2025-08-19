##
# File: depictTools.py
# Date: 11-May-2020 jdw
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


class MoleculeIdentifierType(str, Enum):
    smiles = "SMILES"
    inchi = "InChI"
    identifierPdb = "IdentifierPDB"


class DisplayStyle(str, Enum):
    labeled = "labeled"
    unLabeled = "unlabeled"


class DepictMoleculeIdentifier(BaseModel):
    target: str = Field(None, title="Descriptor string", description="SMILES or InChI chemical descriptor", example="c1ccc(cc1)[C@@H](C(=O)O)N")
    displayStyle: DisplayStyle = Field(None, title="Display style", description="", example="labeled")


@router.get("/molecule/{moleculeIdentifierType}", tags=["depict"])
def depictGet(
    target: str = Query(None, title="Target molecule identifier", description="SMILES, InChI or PDB identifier", example="c1ccc(cc1)[C@@H](C(=O)O)N"),
    displayStyle: DisplayStyle = Query(None, title="Display style", description="", example="labeled"),
    moleculeIdentifierType: MoleculeIdentifierType = Path(
        ..., title="Molecule identifier type", description="Molecule identifier type (SMILES, InChI or PDB identifier)", example="SMILES"
    ),
):
    displayStyle = displayStyle.lower() if displayStyle else "labeled"
    logger.info("Got %r %r %r", moleculeIdentifierType, target, displayStyle)
    # ---
    if "unlabeled" in displayStyle:
        kwargs = {"labelAtomName": False, "labelAtomCIPStereo": False, "labelBondCIPStereo": False}
    else:
        kwargs = {"labelAtomName": True, "labelAtomCIPStereo": True, "labelBondCIPStereo": True}
    # ---
    ccdw = ChemCompDepictWrapper()
    imagePath = ccdw.depictMolecule(target, moleculeIdentifierType, **kwargs)
    # ---
    return FileResponse(imagePath, media_type="image/svg+xml")


@router.post("/molecule/{moleculeIdentifierType}", tags=["depict"])
def depictPost(
    target: DepictMoleculeIdentifier,
    moleculeIdentifierType: MoleculeIdentifierType = Path(
        ..., title="Molecule identifier type", description="Type of molecule identifier (SMILES, InChI or PDB identifier)", example="SMILES"
    ),
):
    logger.info("Got %r %r", moleculeIdentifierType, target)
    qD = jsonable_encoder(target)
    logger.debug("qD %r", qD)
    displayStyle = qD["displayStyle"].lower() if "displayStyle" in qD and qD["displayStyle"] else "labeled"
    # ---
    if "unlabeled" in displayStyle:
        kwargs = {"labelAtomName": False, "labelAtomCIPStereo": False, "labelBondCIPStereo": False}
    else:
        kwargs = {"labelAtomName": True, "labelAtomCIPStereo": True, "labelBondCIPStereo": True}
    # --
    ccdw = ChemCompDepictWrapper()
    imagePath = ccdw.depictMolecule(qD["target"], moleculeIdentifierType, **kwargs)
    # ---
    return FileResponse(imagePath, media_type="image/svg+xml")


@router.get("/alignpair", tags=["depict"])
def depictAlignGet(
    referenceIdentifier: str = Query(None, title="Target molecule identifier", description="SMILES, InChI or PDB identifier", example="c1ccc(cc1)[C@@H](C(=O)O)N"),
    referenceIdentifierType: MoleculeIdentifierType = Query(
        ..., title="Reference molecule identifier type", description="Reference molecule identifier type (SMILES, InChI or PDB identifier)", example="SMILES"
    ),
    fitIdentifier: str = Query(None, title="Fit molecule identifier", description="Fit molecule Chemical Component or BIRD identifier", example="ATP"),
    fitIdentifierType: MoleculeIdentifierType = Query(
        ..., title="Fit molecule identifier type", description="Fit molecule identifier type (SMILES, InChI or PDB identifier)", example="IdentifierPDB"
    ),
    displayStyle: DisplayStyle = Query(None, title="Display style", description="", example="labeled"),
):
    #
    displayStyle = displayStyle.lower() if displayStyle else "labeled"
    logger.info("Got %r %r %r %r %r", referenceIdentifierType, referenceIdentifier, displayStyle, fitIdentifier, fitIdentifierType)
    # ---
    if "unlabeled" in displayStyle:
        kwargs = {"labelAtomName": False, "labelAtomCIPStereo": False, "labelBondCIPStereo": False}
    else:
        kwargs = {"labelAtomName": True, "labelAtomCIPStereo": True, "labelBondCIPStereo": True}
    # ---
    ccdw = ChemCompDepictWrapper()
    imagePath = ccdw.alignMoleculePair(referenceIdentifier, referenceIdentifierType, fitIdentifier, fitIdentifierType, **kwargs)
    # ---
    return FileResponse(imagePath, media_type="image/svg+xml")
