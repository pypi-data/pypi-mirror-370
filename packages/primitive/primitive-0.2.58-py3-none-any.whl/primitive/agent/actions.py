import sys
from time import sleep
from typing import Optional

from loguru import logger

from primitive.__about__ import __version__
from primitive.agent.runner import Runner
from primitive.agent.uploader import Uploader
from primitive.utils.actions import BaseAction


class Agent(BaseAction):
    def start(self, job_run_id: Optional[str] = None):
        logger.remove()
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
            level="DEBUG" if self.primitive.DEBUG else "INFO",
        )
        logger.info("primitive agent")
        logger.info(f"Version: {__version__}")

        # TODO: tighten logic for determining if we're running in a container
        RUNNING_IN_CONTAINER = False
        if job_run_id is not None:
            logger.info("Running in container...")
            RUNNING_IN_CONTAINER = True

        # Create uploader
        uploader = Uploader(primitive=self.primitive)

        try:
            while True:
                logger.debug("Scanning for files to upload...")
                uploader.scan()

                logger.debug("Checking for pending job runs for this device...")

                # From Dylan June 30th:
                # If passed an explicit job_run_id:
                # - check if the JobRun exists in the API
                # - if it does, set it to request_in_progress
                # - if it does not, log an error and stop execution
                # If no job_run_id is passed:
                # - verify that this is a Node with an active Reservation
                # - if the Reservation is active AND it has a JobRun associated with it,
                #   then query for that JobRun
                # - if no JobRuns are found in the API, wait for another active reservation
                # - if a JobRun is found, set it to request_in_progress
                # - then wait for the JobRun to be in_progress from the API

                active_reservation_id = None
                job_run_data: dict = {}

                if RUNNING_IN_CONTAINER and job_run_id:
                    job_run_result = self.primitive.jobs.get_job_run(id=job_run_id)
                    if job_run_result.data:
                        job_run_data = job_run_result.data.get("jobRun", {})
                else:
                    hardware = self.primitive.hardware.get_own_hardware_details()
                    # fetch the latest hardware and activeReservation details
                    if active_reservation_data := hardware["activeReservation"]:
                        active_reservation_id = active_reservation_data.get("id", None)

                    if active_reservation_id is not None:
                        job_run_data = (
                            self.primitive.reservations.get_job_run_for_reservation_id(
                                reservation_id=active_reservation_id
                            )
                        )
                        job_run_id = job_run_data.get("id", None)

                if (
                    len(job_run_data.keys()) == 0
                    or not job_run_data.get("id")
                    or job_run_id is None
                ):
                    if RUNNING_IN_CONTAINER:
                        logger.info("Running in container, exiting due to no JobRun.")
                        break
                    logger.debug("No pending Job Run found, sleeping...")
                    sleep(5)
                    continue

                logger.debug("Found pending Job Run")
                logger.debug(f"Job Run ID: {job_run_data.get('id')}")
                logger.debug(f"Job Name: {job_run_data.get('job').get('name')}")

                job_run_status = job_run_data.get("status", None)

                while True:
                    if job_run_status == "pending":
                        # we are setting to request_in_progress here which puts a started_at time on the JobRun in the API's database
                        # any time spent pulling Git repositories, setting up, etc, counts as compute time
                        logger.info(
                            f"Setting JobRun {job_run_data.get('id')} to request_in_progress."
                        )
                        # get the status back from the job run update, this should be 'in progress'
                        job_run_update_result = self.primitive.jobs.job_run_update(
                            id=job_run_id, status="request_in_progress"
                        )
                        job_run_update_data = job_run_update_result.data
                        if job_run_update_data is not None:
                            # if the job_run_status is not in "in_progress", short circuit
                            job_run_status = job_run_update_data.get(
                                "jobRunUpdate", {}
                            ).get("status", None)
                    if job_run_status == "in_progress":
                        logger.info(f"JobRun {job_run_data.get('id')} in progress.")
                        break
                    if (
                        job_run_status == "request_completed"
                        or job_run_status == "completed"
                    ):
                        logger.error(
                            f"JobRun {job_run_data.get('jobRunNumber')} is already completed with status {job_run_data.get('status', 'unknown')} conclusion {job_run_data.get('conclusion', 'unknown')}. Exiting."
                        )
                        break

                    job_run_result = self.primitive.jobs.get_job_run(id=job_run_id)
                    if job_run_result.data is not None:
                        job_run_data = job_run_result.data.get("jobRun", {})
                        job_run_status = job_run_data.get("status", None)
                    logger.info(
                        f"Waiting for JobRun {job_run_data.get('id')} to be in_progress. Current status: {job_run_status}"
                    )
                    sleep(1)

                # the backend has said it's okay for the agent to run this job
                if job_run_status == "in_progress":
                    try:
                        runner = Runner(
                            primitive=self.primitive,
                            job_run=job_run_data,
                        )
                        runner.setup()
                    except Exception as exception:
                        logger.exception(
                            f"Exception while initializing runner: {exception}"
                        )
                        self.primitive.jobs.job_run_update(
                            id=job_run_id,
                            status="request_completed",
                            conclusion="failure",
                        )
                        continue

                    try:
                        runner.execute_job_run()
                    except Exception as exception:
                        logger.exception(f"Exception while executing job: {exception}")
                        self.primitive.jobs.job_run_update(
                            id=job_run_id,
                            status="request_completed",
                            conclusion="failure",
                        )
                    finally:
                        runner.cleanup()

                        # NOTE: also run scan here to force upload of artifacts
                        # This should probably eventually be another daemon?
                        uploader.scan()

                if RUNNING_IN_CONTAINER:
                    logger.info("Running in container, exiting after job run")
                    break

                sleep(5)
        except KeyboardInterrupt:
            logger.info("Stopping primitive agent...")
