##
# File: main.py
# Date: 12-Mar-2020
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper
from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

from . import convertTools
from . import depictTools
from . import descriptorMatch
from . import formulaMatch
from . import LogFilterUtils
from . import serverStatus

#
# ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# The following mimics the default Gunicorn logging format
formatter = logging.Formatter("%(asctime)s [%(process)d] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s", "[%Y-%m-%d %H:%M:%S %z]")
# The following mimics the default Uvicorn logging format
# formatter = logging.Formatter("%(levelname)s:     %(asctime)s-%(module)s.%(funcName)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = True
# Apply logging filters -
lu = LogFilterUtils.LogFilterUtils()
lu.addFilters()
# ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# http --verbose OPTIONS :8000/status  Access-Control-Request-Method:GET Origin:https://id-localtest.mydomain.co


@app.on_event("startup")
async def startupEvent():
    logger.info("Startup - loading search dependencies")
    #
    ccsw = ChemCompSearchWrapper()
    #
    clDataUrl = os.environ.get("CHEM_SEARCH_DATA_HOSTNAME", None)
    clDataPath = os.environ.get("CHEM_SEARCH_DATA_PATH", None)
    clChannel = os.environ.get("CHEM_SEARCH_UPDATE_CHANNEL", None)
    #
    logger.info("Dependency data host %r path %r update channel %r", clDataUrl, clDataPath, clChannel)
    if clDataUrl and clDataPath and clChannel in ["A", "B", "a", "b"]:
        ccsw.restoreDependencies("http://" + clDataUrl, clDataPath, bundleLabel=clChannel.upper())
    #
    ok1 = ccsw.readConfig()
    ok2 = ccsw.updateChemCompIndex(useCache=True)
    ok3 = ccsw.reloadSearchDatabase()
    ok4 = ccsw.updateSearchIndex(useCache=True)
    #
    logger.info("Completed - loading search dependencies status %r", ok1 and ok2 and ok3 and ok4)
    ccdw = ChemCompDepictWrapper()
    ok1 = ccdw.readConfig()
    logger.info("Completed - loading depict dependencies status %r", ok1)
    #
    ccsw.status()
    #


@app.on_event("shutdown")
def shutdownEvent():
    logger.info("Shutdown - application ended")


app.include_router(
    formulaMatch.router,
    prefix="/chem-match-v1",
)

app.include_router(
    descriptorMatch.router,
    prefix="/chem-match-v1",
)

app.include_router(
    depictTools.router,
    prefix="/chem-depict-v1",
)

app.include_router(
    convertTools.router,
    prefix="/chem-convert-v1",
)

app.include_router(serverStatus.router)
