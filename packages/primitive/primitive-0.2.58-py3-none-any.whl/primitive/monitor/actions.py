import sys
from time import sleep
from typing import Optional

from loguru import logger

from primitive.__about__ import __version__
from primitive.utils.actions import BaseAction
from primitive.utils.exceptions import P_CLI_100, P_CLI_101
from primitive.utils.psutil import kill_process_and_children

MAX_GET_STATUS_TIMEOUT = 30


class Monitor(BaseAction):
    def start(self, job_run_id: Optional[str] = None):
        logger.remove()
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
            level="DEBUG" if self.primitive.DEBUG else "INFO",
        )
        logger.info("primitive monitor")
        logger.info(f"Version: {__version__}")

        # TODO: tighten logic for determining if we're running in a container
        RUNNING_IN_CONTAINER = False
        if job_run_id is not None:
            logger.info("Running in container...")
            RUNNING_IN_CONTAINER = True

        # can't check if if it is a container
        if not RUNNING_IN_CONTAINER:
            try:
                # hey stupid:
                # do not set is_available to True here, it will mess up the reservation logic
                # only set is_available after we've checked that no active reservation is present
                # setting is_available of the parent also effects the children,
                # which may have active reservations as well
                self.primitive.hardware.check_in_http(is_online=True)
            except Exception as exception:
                logger.exception(f"Error checking in hardware: {exception}")
                sys.exit(1)

        # From Dylan on June 30th:
        # If passed an explicit job_run_id we know it is running in a container.
        # If no job_run_id is passed, we need to check that this device has an active reservation.
        # Fetch the active reservations. If it exists AND has a JobRun associated with it:
        # - check if the JobRun exists in the API
        #   - if it does exist, check if it is already running
        #   - if it is in status [pending, request_in_progress, in_progress] where we should wait for the PID
        #   - if it is in status [request_completed, completed] and there is a PID, kill it
        # Finally, if running in a container, kill the process.
        # Else, wait for a new active reservation to be created.

        try:
            active_reservation_data = None
            previous_reservation_id = None
            active_reservation_id = None

            last_provisioned_reservation_id = None

            while True:
                # this block determines if there is a reservation at all
                # handles cleanup of old reservations
                # obtains an active JobRun's ID
                if not RUNNING_IN_CONTAINER:
                    hardware = self.primitive.hardware.get_own_hardware_details()
                    # fetch the latest hardware and activeReservation details
                    if active_reservation_data := hardware["activeReservation"]:
                        active_reservation_id = active_reservation_data.get("id", None)
                        if previous_reservation_id is None:
                            previous_reservation_id = active_reservation_id
                    else:
                        active_reservation_data = None
                        active_reservation_id = None

                    # if there is no activeReservation or previous reservation, sync + sleep
                    if (
                        active_reservation_data is None
                        and active_reservation_id is None
                        and previous_reservation_id is None
                    ):
                        self.primitive.hardware.check_in_http(
                            is_available=True, is_online=True
                        )
                        self.primitive.hardware._sync_children(hardware=hardware)

                        sleep_amount = 5
                        logger.info(
                            f"No active reservation found... [sleeping {sleep_amount} seconds]"
                        )
                        sleep(sleep_amount)
                        continue

                    # if there is a previous_reservation_id but no activeReservation, cleanup
                    elif active_reservation_data is None and previous_reservation_id:
                        logger.info(
                            f"Cleaning up previous reservation {previous_reservation_id}..."
                        )
                        self.primitive.provisioning.remove_reservation_authorized_keys(
                            reservation_id=previous_reservation_id
                        )
                        job_run_data = (
                            self.primitive.reservations.get_job_run_for_reservation_id(
                                reservation_id=previous_reservation_id
                            )
                        )
                        job_run_id = job_run_data.get("id")
                        previous_reservation_id = None
                        last_provisioned_reservation_id = None

                    # if we are on the new reservation
                    elif (active_reservation_id is not None) and (
                        last_provisioned_reservation_id != active_reservation_id
                    ):
                        logger.info(
                            f"Reason: {active_reservation_data.get('reason', '')}"
                        )
                        self.primitive.provisioning.add_reservation_authorized_keys(
                            reservation_id=active_reservation_id
                        )
                        last_provisioned_reservation_id = active_reservation_id

                    # we have an active reservation, check if we have JobRuns attached to it
                    if active_reservation_id is not None:
                        logger.info(f"Active Reservation ID: {active_reservation_id}")
                        job_run_data = (
                            self.primitive.reservations.get_job_run_for_reservation_id(
                                reservation_id=active_reservation_id
                            )
                        )
                        job_run_id = job_run_data.get("id", None)

                    # Golden state for normal reservation
                    if not job_run_id and active_reservation_id:
                        self.primitive.hardware.check_in_http(
                            is_available=False, is_online=True
                        )
                        sleep_amount = 5
                        logger.info(
                            f"Waiting for Job Runs... [sleeping {sleep_amount} seconds]"
                        )
                        sleep(sleep_amount)
                        continue

                # job_run_data can come from 3 places:
                # 1. an explicitly passed job_run_id
                # 2. the previous reservation has an job_run_id (kill old PIDs)
                # 3. the active reservation has an job_run_id (check status)
                while job_run_id:
                    status_result = self.primitive.jobs.get_job_status(id=job_run_id)
                    get_status_timeout = 0
                    sleep_amount = 5

                    while get_status_timeout < MAX_GET_STATUS_TIMEOUT:
                        if not status_result or not status_result.data:
                            logger.error(
                                f"Error fetching job status for Job Run {job_run_id}. Retrying... [sleeping {sleep_amount} seconds]"
                            )
                            get_status_timeout += sleep_amount
                            sleep(sleep_amount)
                            continue
                        else:
                            break

                    if not status_result or not status_result.data:
                        raise P_CLI_101()

                    status_value = status_result.data["jobRun"]["status"]
                    parent_pid = status_result.data["jobRun"]["parentPid"]

                    if status_value in ["request_completed", "completed"]:
                        logger.info(
                            f"Job run {job_run_id} is completed. Killing children if they exist."
                        )
                        if parent_pid is not None:
                            kill_process_and_children(pid=parent_pid)
                        status_value = None
                        job_run_id = None
                    else:
                        logger.info(
                            f"Job Run {job_run_id} with Status {status_value} with PID {parent_pid}. [sleeping {sleep_amount} seconds]"
                        )
                        sleep(sleep_amount)
                        continue

        except KeyboardInterrupt:
            logger.info("Stopping primitive monitor...")
            try:
                if not RUNNING_IN_CONTAINER:
                    self.primitive.hardware.check_in_http(
                        is_available=False, is_online=False, stopping_agent=True
                    )

            except P_CLI_100 as exception:
                logger.error("Error stopping primitive monitor.")
                logger.error(str(exception))
            sys.exit()
