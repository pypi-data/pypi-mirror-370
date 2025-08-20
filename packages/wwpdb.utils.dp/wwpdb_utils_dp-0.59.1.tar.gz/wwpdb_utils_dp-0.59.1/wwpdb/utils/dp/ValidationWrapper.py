# File:    VaildationWrapper.py
#
# Updates:
# 30-Jun-2020 zf  Add image tar file output after svg file for "annot-wwpdb-validate-all", "annot-wwpdb-validate-all-v2" & "annot-wwpdb-validate-all-sf"
##
"""Class to act as a front end to validation calculations and repackaging.
Access pattern mirrors RscbDpUtility.

Provides an op annot-wwpdb-validate-all-sf which provides SF coefficients by intercepting output ops
"""

__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "ezra.peisach@rcsb.org"
__license__ = "Apache 2.0"

import logging
import os
import sys

from mmcif.io.IoAdapterCore import IoAdapterCore

from wwpdb.io.file.DataFile import DataFile
from wwpdb.utils.dp.PdbxSFMapCoefficients import PdbxSFMapCoefficients
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility

logger = logging.getLogger(__name__)


class ValidationWrapper(RcsbDpUtility):
    def __init__(self, tmpPath="/scratch", siteId="DEV", verbose=False, log=sys.stderr):
        logger.debug("Starting")
        super(ValidationWrapper, self).__init__(tmpPath=tmpPath, siteId=siteId, verbose=verbose, log=log)
        self.__op = None
        self._tmppath = tmpPath
        self.__siteId = siteId
        self.__modelfile = None

    def __getPDBId(self):
        """Returns the PDB accession code in model file or None"""
        if not self.__modelfile:
            return None
        io = IoAdapterCore()
        cont = io.readFile(self.__modelfile, selectList=["database_2"])
        if cont:
            block = cont[0]
            catObj = block.getObj("database_2")
            if catObj:
                vals = catObj.selectValuesWhere("database_code", "PDB", "database_id")
                if len(vals) > 0 and vals[0] and vals[0] and len(vals[0]) > 0 and vals[0] not in [".", "?"]:
                    return vals[0]

        return None

    def imp(self, srcPath=None):
        self.__modelfile = srcPath
        super(ValidationWrapper, self).imp(srcPath)

    def op(self, op):
        logger.info("Starting op %s", op)
        if op not in ["annot-wwpdb-validate-all", "annot-wwpdb-validate-all-v2", "annot-wwpdb-validate-all-sf"]:
            logger.error("Operation not known %s", op)
            return False
        self.__op = op

        if op == "annot-wwpdb-validate-all-sf":
            op = "annot-wwpdb-validate-all-v2"
        return super(ValidationWrapper, self).op(op)

    def expList(self, dstPathList=None):
        if dstPathList is None:
            dstPathList = []

        if self.__op in ["annot-wwpdb-validate-all", "annot-wwpdb-validate-all-v2"]:
            return super(ValidationWrapper, self).expList(dstPathList)

        logger.debug("Intercepting expList")
        # Op should be annot-wwpdb-validate-all-sf - so we will "pull" and interpret

        # Handle the first arguments
        # ofpdf,ofxml,offullpdf,ofpng,ofsvg,ofmtz

        basedst = dstPathList[0:7]
        outfosf = dstPathList[7]
        out2fosf = dstPathList[8]
        mtzfile = os.path.join(self.getWorkingDir(), "mapcoef.mtz")
        basedst.append(mtzfile)
        ret = super(ValidationWrapper, self).expList(basedst)

        logger.debug("expList ret is %s", ret)

        # Need to "produce files" for last arguments if possible
        if not os.path.exists(mtzfile):
            return False

        pdbid = self.__getPDBId()
        logger.info("pdbID %s", pdbid)
        if not pdbid:
            pdbid = "xxxx"

        psm = PdbxSFMapCoefficients(siteid=self.__siteId, tmppath=self._tmppath)
        ret = psm.read_mtz_sf(mtzfile)
        logger.debug("read_mtz_sf ret %s", ret)

        if ret:
            # Ensure map coefficients produced in conversion - returns True if present
            ret = psm.has_map_coeff()
            logger.debug("Check for map coeffcients returns %s", ret)
            scrpath = self.getWorkingDir()
            fotemp = os.path.join(scrpath, "fotemp.cif")
            twofotemp = os.path.join(scrpath, "twofotemp.cif")

            if ret:
                ret = psm.write_mmcif_coef(fopathout=fotemp, twofopathout=twofotemp, entry_id=pdbid.lower())
                df = DataFile(fotemp)
                if df.srcFileExists():
                    df.copy(outfosf)
                df = DataFile(twofotemp)
                if df.srcFileExists():
                    df.copy(out2fosf)

        logger.debug("Returning %s", ret)
        return ret
