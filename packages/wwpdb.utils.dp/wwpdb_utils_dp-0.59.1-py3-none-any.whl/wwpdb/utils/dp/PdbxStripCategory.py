##
# File:    PdbxStripCategory.py
# Author:  jdw
# Date:    17-Dec-2012
# Version: 0.001
#
# Updated:
#
##
"""Remove selected categories from the first data container and
write the result.
"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import sys

from mmcif.api.PdbxContainers import DataContainer
from mmcif.io.PdbxReader import PdbxReader
from mmcif.io.PdbxWriter import PdbxWriter

logger = logging.getLogger(__name__)


class PdbxStripCategory:
    def __init__(self, verbose=False, log=sys.stderr):  # pylint: disable=unused-argument
        pass

    def strip(self, inpPath, outPath, stripList=None):
        """Strip categories from inpPath and write to outPath"""
        if stripList is None:
            stripList = []

        try:
            myDataList = []
            with open(inpPath) as ifh:
                pRd = PdbxReader(ifh)
                pRd.read(myDataList)
            myBlock = myDataList[0]
            myName = myBlock.getName()
            newContainer = DataContainer(myName)

            for objName in myBlock.getObjNameList():
                myObj = myBlock.getObj(objName)
                if myObj.getName() not in stripList:
                    newContainer.append(myObj)
            with open(outPath, "w") as ofh:
                pWr = PdbxWriter(ofh)
                pWr.setPreferSingleQuotes()
                pWr.write([newContainer])

            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            return False


def _maintest():
    stripList = [
        "pdbx_coord",
        # 'pdbx_entity_nonpoly',
        # 'pdbx_missing_residue_list',
        "pdbx_nonstandard_list",
        "pdbx_protein_info",
        "pdbx_solvent_info",
        "pdbx_struct_sheet_hbond",
        "pdbx_unobs_or_zero_occ_residues",
        "pdbx_validate_torsion",
        "struct_biol_gen",
        "struct_conf",
        "struct_conf_type",
        "struct_mon_prot_cis",
        "struct_sheet",
        "struct_sheet_order",
        "struct_sheet_range",
    ]

    strp = PdbxStripCategory(verbose=True, log=sys.stderr)
    strp.strip("test-in.cif", "test-out.cif", stripList)


if __name__ == "__main__":
    _maintest()
