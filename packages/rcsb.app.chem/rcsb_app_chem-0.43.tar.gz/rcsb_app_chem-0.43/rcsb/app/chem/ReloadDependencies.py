##
# File:    ReloadDependencies.py
# Author:  J. Westbrook
# Date:    11-May-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Fixture to prepare data dependencies for ChemCompSearchWrapper() and ChemCompDepictWrapper()

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import platform
import resource
import time

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper
from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ReloadDependencies(object):
    def __init__(self, cachePath=None, ccFileNamePrefix=None):
        self.__startTime = time.time()
        self.__cachePath = cachePath if cachePath else os.environ.get("CHEM_SEARCH_CACHE_PATH", "./CACHE")
        self.__ccFileNamePrefix = ccFileNamePrefix if ccFileNamePrefix else os.environ.get("CHEM_SEARCH_CC_PREFIX", "cc-full")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def resourceInfo(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed at %s (%.4f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def buildConfiguration(self, ccUrlTarget=None, birdUrlTarget=None):
        """Build bootstrap configuration files"""

        try:
            configFlagFull = self.__ccFileNamePrefix == "cc-full"
            logger.info("Update configuration for prefix %r configFlagFull %r", self.__ccFileNamePrefix, configFlagFull)
            logger.info("Data source cc %r bird %r", ccUrlTarget, birdUrlTarget)
            ccsw = ChemCompSearchWrapper(cachePath=self.__cachePath, ccFileNamePrefix=self.__ccFileNamePrefix)
            ok1 = ccsw.setConfig(ccUrlTarget=ccUrlTarget, birdUrlTarget=birdUrlTarget)
            ccdw = ChemCompDepictWrapper()
            ok2 = ccdw.setConfig(self.__cachePath)
            return ok1 and ok2
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def updateDependencies(self):
        """Rebuild search indices using configuration files."""
        try:
            logger.info("Starting update %r in %r", self.__ccFileNamePrefix, self.__cachePath)
            ccsw = ChemCompSearchWrapper(cachePath=self.__cachePath, ccFileNamePrefix=self.__ccFileNamePrefix)
            ok1 = ccsw.readConfig()
            ok2 = ccsw.updateChemCompIndex()
            ok3 = ccsw.updateSearchIndex()
            ok4 = ccsw.updateSearchMoleculeProvider()
            # verify access -
            ok5 = ccsw.reloadSearchDatabase()
            return ok1 and ok2 and ok3 and ok4 and ok5
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False


if __name__ == "__main__":
    rmd = ReloadDependencies()
    rmd.buildConfiguration()
    rmd.updateDependencies()
    rmd.resourceInfo()
