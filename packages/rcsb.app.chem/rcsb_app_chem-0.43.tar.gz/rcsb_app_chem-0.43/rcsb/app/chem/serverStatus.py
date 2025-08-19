##
# File: serverStatus.py
# Date: 14-Mar-2020
#
##
# pylint: skip-file
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
from fastapi import APIRouter

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status", tags=["status"])
def serverStatus():
    ccsw = ChemCompSearchWrapper()
    ccsw.status()
    return {"msg": "Service is up!"}


@router.get("/", tags=["status"])
def rootServerStatus():
    return {"msg": "Service is up!"}


@router.get("/healthcheck", tags=["status"])
def rootHealthCheck():
    return True


@router.get("/alive", tags=["status"])
def rootAliveCheck():
    return True
