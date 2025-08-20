import argparse
import logging
import os
import shutil
import sys
import tempfile

import gemmi

from wwpdb.utils.dp.electron_density.common_functions import convert_mdb_to_binary_cif, run_command_and_check_output_file

logger = logging.getLogger(__name__)


class XrayVolumeServerMap:
    def __init__(
        self,
        coord_path,
        binary_map_out,
        node_path,
        volume_server_pack_path,
        volume_server_query_path,
        working_dir,
        two_fofc_mmcif_map_coeff_in,
        fofc_mmcif_map_coeff_in,
    ):
        self.coord_path = coord_path
        self.binary_map_out = binary_map_out
        self.node_path = node_path
        self.volume_server_pack_path = volume_server_pack_path
        self.volume_server_query_path = volume_server_query_path
        self.working_dir = working_dir
        self.two_fofc_mmcif_map_coeff_in = two_fofc_mmcif_map_coeff_in
        self.fofc_mmcif_map_coeff_in = fofc_mmcif_map_coeff_in

        # intermediate files
        self.mdb_map_path = os.path.join(self.working_dir, "mdb_map.mdb")
        self.two_fo_fc_map = os.path.join(self.working_dir, "2fofc.map")
        self.fo_fc_map = os.path.join(self.working_dir, "fofc.map")

    def run_process(self):
        ok = False
        ok1 = self.gemmi_sf2map(
            sf_mmcif_in=self.two_fofc_mmcif_map_coeff_in,
            map_out=self.two_fo_fc_map,
            f_column="pdbx_FWT",
            phi_column="pdbx_PHWT",
        )
        ok2 = self.gemmi_sf2map(
            sf_mmcif_in=self.fofc_mmcif_map_coeff_in,
            map_out=self.fo_fc_map,
            f_column="pdbx_DELFWT",
            phi_column="pdbx_DELPHWT",
        )
        if ok1 and ok2:
            ok = self.make_maps_to_serve_with_volume_server(
                two_fofc_map_in=self.two_fo_fc_map,
                fofc_map_in=self.fo_fc_map,
            )
            if ok:
                ok = self.convert_mdb_map_to_binary_cif()
            else:
                logger.error("making mdb maps failed")
        else:
            logger.error("making maps failed")

        return ok

    def gemmi_sf2map(self, sf_mmcif_in, map_out, f_column, phi_column):
        """
        converts input mmCIF file map coefficients to map
        :param sf_mmcif_in: mmCIF structure factor input file
        :param map_out: map output file
        :param f_column: F column
        :param phi_column: PHI column
        :return: True if worked, False if failed
        """
        st = gemmi.read_structure(self.coord_path, format=gemmi.CoorFormat.Mmcif)
        fbox = st.calculate_fractional_box(margin=5)
        if sf_mmcif_in:
            if os.path.exists(sf_mmcif_in):
                doc = gemmi.cif.read(sf_mmcif_in)  # pylint: disable=no-member
                rblocks = gemmi.as_refln_blocks(doc)
                if f_column in rblocks[0].column_labels() and phi_column in rblocks[0].column_labels():  # pylint: disable=unsubscriptable-object
                    ccp4 = gemmi.Ccp4Map()
                    ccp4.grid = rblocks[0].transform_f_phi_to_map(f_column, phi_column)  # pylint: disable=unsubscriptable-object
                    ccp4.update_ccp4_header(2, True)
                    ccp4.set_extent(fbox)
                    ccp4.write_ccp4_map(map_out)

                    if os.path.exists(map_out):
                        return True
                    logger.error("output map file {} missing".format(map_out))  # pylint: disable=logging-format-interpolation)
                else:
                    logger.error("{} {} columns not found in mmCIF {}".format(f_column, phi_column, sf_mmcif_in))  # pylint: disable=logging-format-interpolation
            else:
                logger.error("cannot find input file {}".format(sf_mmcif_in))  # pylint: disable=logging-format-interpolation)

                # command = "{} sf2map -f {} -p {} {} {}".format(gemmi_path, f_column, phi_column, mmcif_in, map_out)
                # return self.run_command(command=command, output_file=map_out)
        logger.error("converting {} to {} failed".format(sf_mmcif_in, map_out))  # pylint: disable=logging-format-interpolation)
        return False

    def make_maps_to_serve_with_volume_server(
        self,
        two_fofc_map_in,
        fofc_map_in,
    ):
        if not self.node_path:
            logger.error("node path not set")
            return False
        if self.volume_server_pack_path:
            return self.make_volume_server_map(
                two_fofc_map_in=two_fofc_map_in,
                fofc_map_in=fofc_map_in,
            )
        return False

    def make_volume_server_map(self, two_fofc_map_in, fofc_map_in):
        """
        make map for Volume server to serve
        :param: map_in: input map file
        :param: map_out: output map file
        :return: True if worked, False if failed
        """
        if not self.node_path:
            logger.error("node path not set")
            return False
        if not self.volume_server_pack_path:
            logger.error("volume server executable not set")
            return False
        if not os.path.exists(self.volume_server_pack_path):
            logger.error("volume server executable not found at {}".format(self.volume_server_pack_path))  # pylint: disable=logging-format-interpolation
            return False
        if os.path.exists(two_fofc_map_in) and os.path.exists(fofc_map_in):
            command = "{} {} xray {} {} {}".format(self.node_path, self.volume_server_pack_path, two_fofc_map_in, fofc_map_in, self.mdb_map_path)
            return run_command_and_check_output_file(command=command, workdir=None, process_name="make mdb_map", output_file=self.mdb_map_path)
        return False

    def convert_mdb_map_to_binary_cif(self):
        return convert_mdb_to_binary_cif(
            map_id="x_ray_volume",
            source_id="x-ray",
            output_file=self.binary_map_out,
            working_dir=self.working_dir,
            mdb_map_path=self.mdb_map_path,
            volume_server_query_path=self.volume_server_query_path,
            node_path=self.node_path,
            detail=4,
        )


def run_process_with_gemmi(
    node_path,
    coord_file,
    two_fofc_mmcif_map_coeff_in,
    fofc_mmcif_map_coeff_in,
    binary_map_out,
    volume_server_pack_path=None,
    volume_server_query_path=None,
):
    """
    Process 2fo-fc and fo-fc mmCIF files and convert to maps for volume server
    :param node_path: path to node executable
    :param coord_file: path to mmCIF coordinate file
    :param two_fofc_mmcif_map_coeff_in: input 2Fo-Fc map coefficient mmCIF file
    :param fofc_mmcif_map_coeff_in: input Fo-Fc map coefficient mmCIF file
    :return: True if worked, False if failed
    """

    if not volume_server_pack_path:
        logger.error("volume-server-pack path must be set")
        return False

    if not volume_server_query_path:
        logger.error("volume-server-query path must be set")
        return False

    if not coord_file:
        logger.error("coordinate file must be provided")
        return False

    if not node_path:
        logger.error("node not set")
        return False

    if not os.path.exists(node_path):
        logger.error("node not found: {}".format(node_path))  # pylint: disable=logging-format-interpolation
        return False

    if not os.path.exists(two_fofc_mmcif_map_coeff_in) or not os.path.exists(fofc_mmcif_map_coeff_in):
        logger.error("input mmcif files not found: {} or {}".format(two_fofc_mmcif_map_coeff_in, fofc_mmcif_map_coeff_in))  # pylint: disable=logging-format-interpolation)
        return False

    run_working_directory = tempfile.mkdtemp()
    logger.debug("working directory: {}".format(run_working_directory))  # pylint: disable=logging-format-interpolation
    xrsm = XrayVolumeServerMap(
        coord_path=coord_file,
        node_path=node_path,
        volume_server_pack_path=volume_server_pack_path,
        binary_map_out=binary_map_out,
        working_dir=run_working_directory,
        two_fofc_mmcif_map_coeff_in=two_fofc_mmcif_map_coeff_in,
        fofc_mmcif_map_coeff_in=fofc_mmcif_map_coeff_in,
        volume_server_query_path=volume_server_query_path,
    )

    ret = xrsm.run_process()

    # Cleanup
    shutil.rmtree(run_working_directory, ignore_errors=True)

    return ret


def main():  # pragma: no cover
    FORMAT = "[%(levelname)s]-%(module)s.%(funcName)s: %(message)s"
    logging.basicConfig(format=FORMAT)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--two_fofc_mmcif_map_coeff_in",
        help="2fofc mmCIF containing map coefficients",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--fofc_mmcif_map_coeff_in",
        help="fofc mmCIF containing map coefficients",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--binary_map_out",
        help="binary map output file name",
        type=str,
        required=True,
    )
    parser.add_argument("--node_path", help="node program path", type=str, required=True)
    parser.add_argument("--coordinate_file", help="mmCIF coordinate file", type=str, required=True)
    parser.add_argument("--volume_server_pack_path", help="volume-server-pack path", type=str, required=True)
    parser.add_argument("--volume_server_query_path", help="volume-server-query path", type=str, required=True)
    parser.add_argument("--keep_working", help="Keep working directory", action="store_true")
    parser.add_argument(
        "-d",
        "--debug",
        help="debugging",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )

    args = parser.parse_args()
    logger_in = logging.getLogger()
    logger_in.setLevel(args.loglevel)

    ok = run_process_with_gemmi(
        node_path=args.node_path,
        volume_server_pack_path=args.volume_server_pack_path,
        volume_server_query_path=args.volume_server_query_path,
        two_fofc_mmcif_map_coeff_in=args.two_fofc_mmcif_map_coeff_in,
        fofc_mmcif_map_coeff_in=args.fofc_mmcif_map_coeff_in,
        coord_file=args.coordinate_file,
        binary_map_out=args.binary_map_out,
    )

    if not ok:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
