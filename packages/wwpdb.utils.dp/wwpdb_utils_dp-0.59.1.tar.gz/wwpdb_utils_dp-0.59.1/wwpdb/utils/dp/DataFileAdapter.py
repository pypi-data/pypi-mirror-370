##
# File:    DataFileAdapter.py
# Date:    16-July-2012
#
# Updates:
#
#  4-Jan-2013 -jdw  add filters to remove derived categories after format conversion
# 12-Feb-2013  jdw  add option flags for stipping derived categories --
# 25-Feb-2013  jdw  add cif2pdb translation.
#  6-Aug-2013  jdw  add rcsb2PdbxWithPdbIdAlt()
# 11-Oct-2013  jdw  add option to strip  additional entity categories --
#  4-Dec-2013  jdw  check for duplicate source and destination paths.
# 24-Dec-2013  jdw  add pdbx2Assemblies(idCode,inpFilePath,outPath='.',idxFilePath=None)
# 24-Dec-2013  jdw  add cif2pdbx()
# 16-Jan-2014  jdw  Update method for cif2pdbx()
# 25-Sep-2014  jdw  add pdbx2nmrstar()
##
"""
Encapsulate data model format type conversions.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import os.path
import shutil
import sys
import traceback

from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility


class DataFileAdapter:
    """Convenience methods to manage data model and structure factor format conversions."""

    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = True
        self.__siteId = self.__reqObj.getValue("WWPDB_SITE_ID")
        self.__sObj = self.__reqObj.getSessionObj()
        # self.__sessionId = self.__sObj.getId()
        self.__sessionPath = self.__sObj.getPath()

    def pdbx2nmrstar(self, inpPath, outPath, pdbId=None):
        """PDBx to NMRSTAR"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            if pdbId is not None:
                dp.addInput(name="pdb_id", value=pdbId, type="param")
            dp.op("annot-pdbx2nmrstar")
            logPath = os.path.join(self.__sessionPath, "annot-pdbx2nmrstar.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def rcsb2Pdbx(self, inpPath, outPath, stripFlag=False, stripEntityFlag=False):
        """RCSB CIF -> PDBx conversion  (Using the smaller application in the annotation package)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)

            if stripFlag:
                if stripEntityFlag:
                    dp.op("annot-rcsb2pdbx-strip-plus-entity")
                else:
                    dp.op("annot-rcsb2pdbx-strip")
            else:
                dp.op("annot-rcsb2pdbx")

            logPath = os.path.join(self.__sessionPath, "annot-rcsb2pdbx.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def rcsb2PdbxWithPdbId(self, inpPath, outPath):
        """RCSB CIF -> PDBx conversion  (converting to PDB ID entry/datablock id.)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            dp.op("annot-rcsb2pdbx-withpdbid")
            logPath = os.path.join(self.__sessionPath, "annot-rcsb2pdbx.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def rcsb2PdbxWithPdbIdAlt(self, inpPath, outPath):
        """RCSB CIF -> PDBx conversion  (converting to PDB ID entry/datablock id.)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            dp.op("annot-rcsb2pdbx-alt")
            logPath = os.path.join(self.__sessionPath, "annot-rcsb2pdbxalt.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def rcsbEps2Pdbx(self, inpPath, outPath, stripFlag=False, stripEntityFlag=False):
        """RCSB CIFEPS -> PDBx conversion (This still requires using the full maxit application)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            if stripFlag:
                if stripEntityFlag:
                    dp.op("annot-rcsbeps2pdbx-strip-plus-entity")
                else:
                    dp.op("annot-rcsbeps2pdbx-strip")
            else:
                dp.op("annot-cif2cif")

            logPath = os.path.join(self.__sessionPath, "annot-rcsbeps2pdbx.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def cif2Pdb(self, inpPath, outPath):
        """CIF -> PDB conversion  (Using the smaller application in the annotation package)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            dp.op("annot-cif2pdb")
            logPath = os.path.join(self.__sessionPath, "annot-cif2pdb.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def cif2Pdbx(self, inpPath, outPath):
        """CIF -> PDBx conversion  (public subset with PDBid conversion)"""
        try:
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(inpPath)
            dp.op("cif2pdbx-public")
            logPath = os.path.join(self.__sessionPath, "annot-cif2pdbx.log")
            dp.expLog(logPath)
            dp.exp(outPath)
            if not self.__debug:
                dp.cleanup()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def modelConvertToPdbx(self, filePath=None, fileType="pdbx", pdbxFilePath=None):
        """Convert input model file format to PDBx.   Converted file is stored in the session
        directory using standard file naming.

        Return True for success or False otherwise.
        """
        if self.__verbose:
            self.__lfh.write("+DataFileAdapter.modelConvertToPdbx() filePath %s fileType %s pdbxFilePath %s\n" % (filePath, fileType, pdbxFilePath))
        try:
            ok = False
            if filePath is None or pdbxFilePath is None:
                return ok
            if fileType in ["pdbx-mmcif", "pdbx", "pdbx-cif"]:
                if filePath != pdbxFilePath:
                    shutil.copyfile(filePath, pdbxFilePath)
                ok = True
            elif fileType == "rcsb-mmcif":
                ok = self.rcsb2Pdbx(filePath, pdbxFilePath, stripFlag=False)
            elif fileType == "rcsb-mmcif-strip":
                ok = self.rcsb2Pdbx(filePath, pdbxFilePath, stripFlag=True)
            elif fileType == "rcsb-cifeps":
                ok = self.rcsbEps2Pdbx(filePath, pdbxFilePath, stripFlag=False)
            elif fileType == "rcsb-cifeps-strip":
                ok = self.rcsbEps2Pdbx(filePath, pdbxFilePath, stripFlag=True)
            else:
                ok = False
            return ok
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def pdbx2Assemblies(self, idCode, inpFilePath, outPath=".", indexFilePath=None):
        """Create model assemby files from input PDBx model file."""
        try:
            pdbxPath = inpFilePath
            logPath = os.path.join(self.__sessionPath, "pdbx-assembly.log")
            # indexFilePath=os.path.join(self.__sessionPath,"pdbx-assembly-index.txt")
            #
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(pdbxPath)
            if idCode is not None:
                dp.addInput(name="deposition_data_set_id", value=idCode, type="param")

            if indexFilePath is not None:
                dp.addInput(name="index_file_path", value=indexFilePath, type="param")

            dp.op("annot-gen-assem-pdbx")
            dp.expLog(logPath)
            pthList = dp.getResultPathList()
            # wrkPath = dp.getWorkingDir()
            for pth in pthList:
                if os.access(pth, os.R_OK):
                    (_t, fn) = os.path.split(pth)
                    shutil.copyfile(pth, os.path.join(outPath, fn))

            # if (not self.__debug):
            #     dp.cleanup()
            #
            if self.__verbose:
                self.__lfh.write("+DataFileAdapter.pdbx2Assemblies() - input  model file path: %s\n" % inpFilePath)
                self.__lfh.write("+DataFileAdapter.pdbx2Assemblies() - assembly output paths:  %r\n" % pthList)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            self.__lfh.write("+DataFileAdapter.pdbx2Assemblies() - failing for input file path %s output path %s\n" % (inpFilePath, outPath))
            traceback.print_exc(file=self.__lfh)
            return False

    def mtz2Pdbx(
        self,
        mtzFilePath,
        outSfFilePath,
        pdbxFilePath=None,
        logFilePath=None,
        diagsFilePath=None,  # noqa: ARG002
        dumpFilePath=None,
        timeout=120,
    ):  # noqa: ARG002 pylint: disable=unused-argument
        """Convert input MTZ format to PDBx sf file."""
        try:
            diagfn = logFilePath if logFilePath is not None else "sf-convert-diags.cif"
            dmpfn = dumpFilePath if dumpFilePath is not None else "sf-convert-mtzdmp.log"
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            dp.imp(mtzFilePath)
            dp.setTimeout(timeout)
            if pdbxFilePath is not None:
                dp.addInput(name="xyz_file_path", value=pdbxFilePath)
            dp.op("annot-sf-convert")
            dp.expLog(logFilePath)
            dp.expList(dstPathList=[outSfFilePath, diagfn, dmpfn])

            if not self.__debug:
                dp.cleanup()
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            self.__lfh.write("+DataFileAdapter.mtz2Pdbx() - failing for mtz file path %s output path %s\n" % (mtzFilePath, outSfFilePath))
            traceback.print_exc(file=self.__lfh)
            return False
