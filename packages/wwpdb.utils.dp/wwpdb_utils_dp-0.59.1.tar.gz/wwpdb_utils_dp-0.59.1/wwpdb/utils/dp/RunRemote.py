# pylint: disable=logging-format-interpolation
import argparse
import logging
import os
import shutil
import subprocess
import tempfile
import time
from enum import Enum
from textwrap import dedent

from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def remove_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as _e:  # noqa: F841
            pass


class JobStatus(Enum):
    OOM = "OUT_OF_MEMORY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    OTHER = "OTHER"


class RunRemote:
    def __init__(
        self,
        command,
        job_name,
        log_dir,
        run_dir=None,
        timeout=90,
        memory_limit=16000,
        number_of_processors=1,
        add_site_config=False,
        add_site_config_database=False,
    ):
        self.command = command
        self.job_name = job_name
        self.log_dir = log_dir
        self.run_dir = run_dir
        self.timeout = 90 if timeout == 0 else str(timeout)
        self.memory_limit = str(memory_limit)
        self.number_of_processors = str(number_of_processors)
        self.add_site_config = add_site_config
        self.add_site_config_database = add_site_config_database

        if not self.run_dir:
            self.run_dir = tempfile.mkdtemp(prefix="run_remote_")  # this won't work as cluster nodes have different temp dirs
        self._shell_script = os.path.join(self.run_dir, "run_{}.sh".format(self.job_name))

        self.siteId = getSiteId()
        self.cI = ConfigInfo(self.siteId)
        self.pdbe_cluster_queue = str(self.cI.get("PDBE_CLUSTER_QUEUE"))
        self._stdout_file = os.path.join(self.log_dir, self.job_name + ".out")
        self._stderr_file = os.path.join(self.log_dir, self.job_name + ".err")

    def get_job_status_by_id(self, job_id) -> JobStatus:
        """Get the status of a single job by ID."""
        cmd = [
            "squeue",
            "--noheader",
            "-t",
            "all",
            "--Format",
            "State",
            "--jobs",
            str(job_id),
        ]
        squeue_output = subprocess.run(cmd, check=True, capture_output=True)
        status_text = squeue_output.stdout.decode("utf-8").strip()

        if status_text in ["FAILED", "TIMEOUT"]:
            return JobStatus.FAILED
        if status_text == "OUT_OF_MEMORY":
            return JobStatus.OOM
        if status_text == "COMPLETED":
            return JobStatus.COMPLETED
        if status_text in ["RUNNING", "PENDING", "CONFIGURING", "COMPLETING"]:
            return JobStatus.RUNNING
        if status_text == "CANCELLED":
            return JobStatus.CANCELLED
        return JobStatus.OTHER

    def requeue_job(self, job_id):
        """Requeue a single job."""
        cmd = ["scontrol", "requeue", str(job_id)]
        subprocess.run(cmd, check=True)
        logger.info(f"Requeued failed job {job_id}")

    def monitor(self, job_id, frequency=10):
        """Monitor a job by ID, requeueing if it fails."""
        logging.info(f"Monitoring job {job_id}")

        while True:
            status = self.get_job_status_by_id(job_id)

            if status in (JobStatus.CANCELLED, JobStatus.FAILED, JobStatus.OOM):
                logger.warning(f"Job {job_id} failed with status {status}")
                break
            if status == JobStatus.COMPLETED:
                logger.info(f"Job {job_id} completed successfully")
                break
            else:
                logger.debug(f"Job {job_id} status: {status}")

            time.sleep(frequency)

        return self.get_job_status_by_id(job_id)

    def _build_sbatch_command(self, command):
        sbatch_args = [
            "sbatch",
            "--job-name=%s" % self.job_name,
            "--partition=%s" % self.pdbe_cluster_queue,
            "--cpus-per-task=%s" % self.number_of_processors,
            "--mem=%s" % self.memory_limit,
            "--time=%s" % self.timeout,
            "--chdir=%s" % self.run_dir,
            "--output=%s" % self._stdout_file,
            "--error=%s" % self._stderr_file,
        ]

        with open(self._shell_script, "w") as f:
            cmd = f"""\
            #!/bin/bash
            set -e
            export XDG_RUNTIME_DIR={self.run_dir}
            {command}
            """
            f.write(dedent(cmd))
            f.flush()
        os.chmod(self._shell_script, 0o775)

        sbatch_args += [self._shell_script]
        return sbatch_args

    def _cleanup(self):
        if self.run_dir.startswith("/tmp/run_remote_"):  # noqa: S108
            shutil.rmtree(self.run_dir)

    def _source_site_config(self, database=False):
        suffix = ""
        if database:
            suffix = "--database"

        site_config_path = self.cI.get("TOP_WWPDB_SITE_CONFIG_DIR")
        site_loc = self.cI.get("WWPDB_SITE_LOC")
        site_config_command = ". {}/init/env.sh --siteid {} --location {} {} > /dev/null".format(site_config_path, self.siteId, site_loc, suffix)

        return "{}; {}".format(site_config_command, self.command)

    def run(self, retries=3):
        status = JobStatus.OTHER
        wf_command = self.command

        if self.add_site_config_database or self.add_site_config:
            wf_command = self._source_site_config(database=self.add_site_config_database)

        while retries > 0:
            sbatch_cmd = self._build_sbatch_command(command=wf_command)
            logger.info(" ".join(sbatch_cmd))

            output = subprocess.run(sbatch_cmd, check=True, capture_output=True)
            job_id = int(output.stdout.decode("utf-8").split()[-1])
            logger.debug(f"Submitted: {job_id}")

            self._cleanup()
            status = self.monitor(job_id=job_id)

            if status == JobStatus.COMPLETED:
                break

            if status == JobStatus.OOM:
                self.memory_limit = str(int(self.memory_limit) * 2)

            logger.info(f"Retrying job {job_id} with memory limit {self.memory_limit}")
            retries -= 1

        return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="comm")

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("-d", "--debug", help="debugging", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser_run.add_argument("--command", help="command to run", type=str, required=True)
    parser_run.add_argument("--job_name", help="name for the job", type=str, required=True)
    parser_run.add_argument("--log_dir", help="directory to store log file in", type=str, required=True)
    parser_run.add_argument("--run_dir", help="directory to run", type=str)
    parser_run.add_argument("--memory_limit", help="starting memory limit", type=int, default=16000)
    parser_run.add_argument("--num_processors", help="number of processors", type=int, default=1)
    parser_run.add_argument("--add_site_config", help="add site config to command", action="store_true")
    parser_run.add_argument("--add_site_config_with_database", help="add site config with database to command", action="store_true")

    args = parser.parse_args()

    logger.info(f"Running command: {args.comm}")
    if args.comm == "run":
        run_remote = RunRemote(
            command=args.command,
            job_name=args.job_name,
            log_dir=args.log_dir,
            run_dir=args.run_dir,
            memory_limit=args.memory_limit,
            number_of_processors=args.num_processors,
            add_site_config=args.add_site_config,
            add_site_config_database=args.add_site_config_with_database,
        )
        status_ret = run_remote.run()
        logger.info(f"Job finished with status: {status_ret}")
