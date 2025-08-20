#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from wwpdb.utils.dp.electron_density.common_functions import convert_mdb_to_binary_cif, run_command_and_check_output_file

logger = logging.getLogger()


class EmVolumes:
    def __init__(
        self,
        em_map,
        node_path,
        volume_server_pack_path,
        volume_server_query_path,
        binary_map_out,
        working_dir,
    ):
        self.em_map = em_map
        self.em_map_name = os.path.basename(em_map)
        self.mdb_map = "em_map.mdb"
        self.node_path = node_path
        self.volume_server_pack_path = volume_server_pack_path
        self.volume_server_query_path = volume_server_query_path
        self.mdb_map_path = None
        self.bcif_map_path = binary_map_out
        self.workdir = working_dir or os.getcwd()

    def run_conversion(self):
        bcif_dir_out = os.path.dirname(self.bcif_map_path)
        if bcif_dir_out:
            if not os.path.exists(bcif_dir_out):
                os.makedirs(bcif_dir_out)
        logging.debug("temp working folder: %s", self.workdir)
        self.mdb_map_path = os.path.join(self.workdir, self.mdb_map)

        worked = self.make_volume_server_map()

        if worked:
            worked = self.convert_map_to_binary_cif()

        return worked

    def make_volume_server_map(self):
        if os.path.exists(self.em_map):
            command = "%s %s em %s %s" % (self.node_path, self.volume_server_pack_path, self.em_map, self.mdb_map_path)
            logging.debug(command)
            return run_command_and_check_output_file(
                command=command, process_name="make Volume server map", workdir=self.workdir, output_file=self.mdb_map_path
            )
        logging.error("input map file missing: %s", self.em_map)
        return False

    def convert_map_to_binary_cif(self):
        return convert_mdb_to_binary_cif(
            node_path=self.node_path,
            volume_server_query_path=self.volume_server_query_path,
            map_id="em_volume",
            source_id="em",
            output_file=self.bcif_map_path,
            working_dir=self.workdir,
            mdb_map_path=self.mdb_map_path,
            detail=1,
        )


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--em_map", help="EM map", type=str, required=True)
    parser.add_argument("--working_dir", help="working dir", type=str, required=True)
    parser.add_argument("--binary_map_out", help="Output filename of binary map", type=str, required=True)
    parser.add_argument("--node_path", help="path to node", type=str, required=True)
    parser.add_argument("--volume_server_pack_path", help="path to volume-server-pack", type=str, required=True)
    parser.add_argument("--volume_server_query_path", help="path to volume-server-query", type=str, required=True)
    parser.add_argument("--keep_working_directory", help="keep working directory", action="store_true")
    parser.add_argument("--debug", help="debugging", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)

    args = parser.parse_args()
    logger.setLevel(args.loglevel)

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit()

    em = EmVolumes(
        em_map=args.em_map,
        node_path=args.node_path,
        volume_server_pack_path=args.volume_server_pack_path,
        volume_server_query_path=args.volume_server_query_path,
        binary_map_out=args.binary_map_out,
        working_dir=args.working_dir,
    )
    worked = em.run_conversion()
    logging.info("EM map conversion worked: {}".format(worked))  # noqa: G001 pylint: disable=logging-format-interpolation
    if not worked:
        sys.exit(1)


if __name__ == "__main__":
    main()
