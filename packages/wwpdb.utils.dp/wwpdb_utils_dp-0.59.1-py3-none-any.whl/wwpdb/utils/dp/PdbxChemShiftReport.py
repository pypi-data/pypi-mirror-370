##
# File:    PdbxChemShiftReport.py
# Author:  jdw
# Date:    11-Sep-2014
# Version: 0.001
#
# Updated:
#
##
"""Read diagnostics in the chemical shift diagnostics report."""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2,9"
__version__ = "V0.01"

import logging
import sys

# from mmcif.api.PdbxContainers import *
from mmcif.io.PdbxReader import PdbxReader

logger = logging.getLogger(__name__)


class PdbxChemShiftReport:
    def __init__(self, inputPath, verbose=False, log=sys.stderr):  # noqa: ARG002 pylint: disable=unused-argument
        self.__myContainerList = []
        self.__read(inputPath)

    def __read(self, inputPath):
        """Read status file"""
        try:
            self.__myContainerList = []
            with open(inputPath) as ifh:
                pRd = PdbxReader(ifh)
                pRd.read(self.__myContainerList)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def getStatus(self):
        return self.__get("pdbx_shift_check", "status")

    def getWarnings(self):
        return self.__get("pdbx_shift_check_warning_message", "text")

    def getErrors(self):
        return self.__get("pdbx_shift_check_error_message", "text")

    def __get(self, categoryName, attributeName):
        retVal = []
        try:
            c0 = self.__myContainerList[0]
            catObj = c0.getObj(categoryName)
            if catObj is None:
                return retVal
            _nm, aList, rList = catObj.get()

            if attributeName in aList:
                idx = aList.index(attributeName)
                for r in rList:
                    retVal.append(str(r[idx]).strip())
        except Exception:  # noqa: BLE001
            pass

        return retVal


if __name__ == "__main__":
    pass
