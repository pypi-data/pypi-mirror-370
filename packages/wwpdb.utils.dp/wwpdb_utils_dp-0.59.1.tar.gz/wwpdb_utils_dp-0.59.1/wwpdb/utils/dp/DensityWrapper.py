import argparse
import logging
import os
import shutil
import sys
import tempfile

from wwpdb.utils.config.ConfigInfo import getSiteId
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility

logger = logging.getLogger()


class DensityWrapper:
    def __init__(self, site_id=None):
        self.__site_id = site_id or getSiteId()

    def convert_xray_density_map(self, coord_file, in_2fofc_cif, in_fofc_cif, out_binary_volume, working_dir):
        logging.info("Converting X-ray maps to binary cif")
        logging.debug(working_dir)
        rdb = RcsbDpUtility(tmpPath=working_dir, siteId=self.__site_id, verbose=True)
        rdb.imp(coord_file)
        rdb.addInput(name="two_fofc_cif", value=in_2fofc_cif, type="file")
        rdb.addInput(name="one_fofc_cif", value=in_fofc_cif, type="file")
        rdb.op("xray-density-bcif")
        rdb.exp(out_binary_volume)
        rdb.cleanup()

        if out_binary_volume:
            if os.path.exists(out_binary_volume):
                return True
        return False

    def convert_em_volume(self, in_em_volume, out_binary_volume, working_dir):
        logging.info("Converting EM maps to binary cif")
        logging.debug(working_dir)
        rdb = RcsbDpUtility(tmpPath=working_dir, siteId=self.__site_id, verbose=True)
        rdb.imp(in_em_volume)
        rdb.op("em-density-bcif")
        rdb.exp(out_binary_volume)
        rdb.cleanup()

        if out_binary_volume:
            if os.path.exists(out_binary_volume):
                return True
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--em_map", help="EM map", type=str)
    parser.add_argument("--binary_map_out", help="Output filename of binary map", type=str, required=True)
    parser.add_argument("--debug", help="debugging", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)

    args = parser.parse_args()
    # logger = logging.getLogger()
    logger.setLevel(args.loglevel)

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit()

    dw = DensityWrapper()
    working_dir = tempfile.mkdtemp()
    if args.em_map:
        dw.convert_em_volume(in_em_volume=args.em_map, out_binary_volume=args.binary_map_out, working_dir=working_dir)

    shutil.rmtree(working_dir)


if __name__ == "__main__":
    main()
