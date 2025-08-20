##
# File:    PdbxMergeCategory.py
##
"""Merge/replace selected categories from the first data container and
write the result.
"""

__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "ezra.peisach@rcsb.org"
__license__ = "Apache 2.0"


import logging

from mmcif.io.IoAdapterCore import IoAdapterCore

logger = logging.getLogger(__name__)


class PdbxMergeCategory:
    def __init__(self):
        pass

    @staticmethod
    def merge(srcpath, newcontentpath, outpath, mergelist=None, replacelist=None):
        """Merges selected categories from newcontentpath (first block) into srcpath and outputs to outpath in
                   first data block.
        Categories in replacelist will replace category, if present in newcontentpath, otherwise leaves alone.
        Categories in mergelist must be single row. Attributes will be replaced/appended. Attributes not in
                   newcontentpath are ignored.

        newcontentpath will contain to combined file

        If the same category is in mergelist and replacelist, undefined behaviour

        """
        logger.debug("Starting merge %s %s %s", srcpath, newcontentpath, outpath)
        try:
            io = IoAdapterCore()
            srcin = io.readFile(srcpath)
            srcblock = srcin[0]

            newcontent = io.readFile(newcontentpath)
            newcontentblock = newcontent[0]

            # The plan is to replace/modify the datablock - and then rewrite
            if replacelist:
                for cat in replacelist:
                    if cat in newcontentblock.getObjNameList():
                        obj = newcontentblock.getObj(cat)
                        srcblock.append(obj)

            if mergelist:
                for cat in mergelist:
                    if cat in newcontentblock.getObjNameList():
                        obj = newcontentblock.getObj(cat)
                        if srcblock.exists(cat):
                            # Category exists in file
                            srcobj = srcblock.getObj(cat)
                            for attr in obj.getAttributeList():
                                val = obj.getValue(attr, 0)
                                if not srcobj.hasAttribute(attr):
                                    srcobj.appendAttribute(attr)
                                srcobj.setValue(val, attr, 0)
                        else:
                            # New category
                            srcblock.append(obj)

            ret = io.writeFile(outpath, srcin)
            return ret

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            return False
