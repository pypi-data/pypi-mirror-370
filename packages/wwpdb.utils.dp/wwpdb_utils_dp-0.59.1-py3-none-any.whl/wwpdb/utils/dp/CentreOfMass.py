import argparse
import logging
import os
import sys

import gemmi
from mmcif.api.DataCategory import DataCategory
from mmcif.io.IoAdapterCore import IoAdapterCore

from wwpdb.io.locator.PathInfo import PathInfo
from wwpdb.utils.config.ConfigInfo import getSiteId

logger = logging.getLogger()


def get_model_file(depid, version_id, mileStone=None, siteId=None):
    if siteId is None:
        siteId = getSiteId()
    pi = PathInfo(siteId, sessionPath=".", verbose=True, log=sys.stderr)
    mmcif = pi.getModelPdbxFilePath(dataSetId=depid, fileSource="archive", versionId=version_id, mileStone=mileStone)
    logging.debug("mmcif file path: %s", mmcif)
    return mmcif


def get_center_of_mass(data_block):
    try:
        st = gemmi.make_structure_from_block(data_block)
        model = st[0]
        center_of_mass = model.calculate_center_of_mass()
        return center_of_mass
    except Exception as e:  # noqa: BLE001
        logging.error(e)
        return False


def get_deposition_ids(file):
    deposition_ids = []
    with open(file) as f:
        for line in f:
            deposition_ids.append(line.strip())
    return deposition_ids


def process_entry(file_in, file_out):
    try:
        cif_file = gemmi.cif.read(file_in)  # pylint: disable=no-member
        data_block = cif_file[0]
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to read cif file in Gemmi")
        logger.error(e)
        return 1

    logging.info("Finding Centre of Mass")
    com = get_center_of_mass(data_block)
    if not com:
        return 1

    try:
        io = IoAdapterCore()
        ccL = io.readFile(file_in)
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to read cif file using IoAdapterCore %s", e)
        return 1

    if len(ccL) == 0:
        logger.error("No data parsed from file")
        return 1

    # First block only
    b0 = ccL[0]

    obj = b0.getObj("struct")
    # If category does not exist
    if obj is None:
        # Need entry.id
        eid = "XXXX"
        eobj = b0.getObj("entry")
        if eobj:
            if "id" in eobj.getAttributeList():
                eid = eobj.getValue("id", 0)
        obj = DataCategory("struct")
        obj.appendAttribute("entry_id")
        obj.setValue(eid, "entry_id", 0)
        ccL[0].append(obj)

    newdata = [["pdbx_center_of_mass_x", com.x], ["pdbx_center_of_mass_y", com.y], ["pdbx_center_of_mass_z", com.z]]
    for [it, val] in newdata:
        if it not in obj.getAttributeList():
            obj.appendAttribute(it)
        obj.setValue(str(val), it, 0)

    try:
        logging.info("Writing mmcif file: %s", file_out)
        ret = io.writeFile(file_out, ccL)
        if not ret:
            logger.info("Writing failed error %s", ret)
            return 1
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to write ccif file in IoAdapater %s", e)
        return 1

    # existing_data = data_block.get_mmcif_category('_struct.')
    # new_data = {
    #     **existing_data,
    #     'pdbx_center_of_mass_x': [com.x],
    #     'pdbx_center_of_mass_y': [com.y],
    #     'pdbx_center_of_mass_z': [com.z]
    # }
    # logging.info("Writing mmcif file: %s", file_out)
    # try:
    #     data_block.set_mmcif_category('_struct.', new_data)
    #     cif_file.write_file(file_out)
    # except Exception as e:
    #     logger.error("Failed to write cif file in Gemmi")
    #     logger.error(e)
    #     return 1
    return 0


def calculate_for_list(args, siteId=None):
    logging.info("Calculating for list of entries")
    deposition_ids = get_deposition_ids(args.list)
    failed_dep_ids = []
    for depid in deposition_ids:
        logging.info("Calculating for Dep ID: %s ", depid)
        latest_model = get_model_file(depid, "latest", siteId=siteId)
        next_model = get_model_file(depid, "next", siteId=siteId)
        result = process_entry(latest_model, next_model)
        if result:
            logger.info("Failed to Calculate Centre of Mass for %s", depid)
            failed_dep_ids.append(depid)
    return failed_dep_ids


def calculate_for_file(args):
    logging.info("Calculating for a single file")
    result = process_entry(args.model_file_in, args.model_file_out)
    if result:
        logger.info("Failed to Calculate Centre of Mass")


def main(args):
    if args.list and os.path.isfile(args.list):
        failures = calculate_for_list(args)
        if len(failures) > 0:
            logger.info("Failed Dep Ids: \n%s", "\n".join(failures))
            return 1

    elif os.path.isfile(args.model_file_in):
        calculate_for_file(args)
        return 0
    else:
        logger.error("Input model file doesn't exists")
        return 1

    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--model-file-in", help="Coordinate file to add centre of Mass", type=str)
    parser.add_argument("-o", "--model-file-out", help="Output Coordinate file, with added items", type=str)
    parser.add_argument("-l", "--list", help="list of Deposition Ids to calculate and append centre of Mass", type=str)
    parser.add_argument("-log", "--log-level", help="Log level", type=str, default="INFO")
    parser.add_argument("-s", "--siteid", help="optional siteId", type=str)

    args = parser.parse_args()
    logger.setLevel(args.log_level)

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit()

    main(args)


if "__main__" in __name__:
    parse_args()
