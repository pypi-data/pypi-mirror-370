import json
import logging
import os
import shlex
import shutil
import subprocess

logger = logging.getLogger(__name__)


def run_command(command, process_name, workdir=None):
    """
    run a command and check the output
    :param str command: the command to be run
    :param str process_name: a name for the process
    :param str None workdir: a path or None for a working directory
    :return bool: True if exit status is zero, False otherwise
    """
    try:
        logger.debug(command)
        command_list = shlex.split(command)
        if workdir and workdir is not None:
            process = subprocess.Popen(command_list, cwd=workdir)
        else:
            process = subprocess.Popen(command_list)
        out, err = process.communicate()
        if out:
            logger.info(out)
        if err:
            logger.error(err)
        rc = process.returncode
        if rc != 0:
            logger.error("process failed: {}".format(process_name))  # pylint: disable=logging-format-interpolation
            return False
        logger.info("process worked: {}".format(process_name))  # pylint: disable=logging-format-interpolation
        return True
    except Exception as e:  # noqa: BLE001
        logger.error(e)
    return False


def run_command_and_check_output_file(command, process_name, output_file, workdir=None):
    """
    run a command and check the output file exists
    :param str command: the command to be run
    :param str None workdir: path or None
    :param str process_name: a name for the process
    :param str output_file: the output file to check for
    :return bool: True if the command exits with status 0 and the output file exists, False otherwise
    """
    if command and output_file:
        ret = run_command(command=command, workdir=workdir, process_name=process_name)
        if ret:
            logger.debug("checking for {}".format(output_file))  # pylint: disable=logging-format-interpolation
            if os.path.exists(output_file):
                logger.debug("file exists")
                return True
            logger.error("output file missing: {}".format(output_file))  # pylint: disable=logging-format-interpolation
        else:
            logger.error("command returned non-zero exit status")
    else:
        logger.error("either command or output file not set")

    return False


def convert_mdb_to_binary_cif(node_path, volume_server_query_path, map_id, source_id, mdb_map_path, output_file, working_dir, detail=4):
    query_kind = "cell"
    map_file_name = "{}_{}-{}_d{}.bcif".format(map_id, source_id, query_kind, detail)
    if not working_dir:
        working_dir = os.getcwd()
    temp_out_file = os.path.join(working_dir, map_file_name)
    json_filename = "conversion.json"
    json_content = [
        {
            "source": {"filename": mdb_map_path, "name": map_id, "id": source_id},
            "query": {"kind": query_kind},
            "params": {"detail": detail, "asBinary": True},
            "outputFolder": working_dir,
            "outputFilename": map_file_name,
        }
    ]
    if working_dir:
        working_json = os.path.join(working_dir, json_filename)
    else:
        working_json = json_filename
    with open(working_json, "w") as out_file:
        json.dump(json_content, out_file)
    command = "{} {} --jobs {}".format(node_path, volume_server_query_path, working_json)
    ret = run_command_and_check_output_file(command=command, process_name="mdb_to_binary_cif", workdir=working_dir, output_file=temp_out_file)
    if ret:
        output_folder = os.path.dirname(output_file)
        if output_folder:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
        shutil.copy(temp_out_file, output_file)
        logger.debug("output file {}".format(output_file))  # pylint: disable=logging-format-interpolation
        return True
    return False
