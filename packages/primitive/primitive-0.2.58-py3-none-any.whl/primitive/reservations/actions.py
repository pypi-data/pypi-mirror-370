import typing

from primitive.graphql.relay import from_base64

if typing.TYPE_CHECKING:
    pass

from datetime import datetime, timedelta
from time import sleep
from typing import List, Optional

from gql import gql
from loguru import logger

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.mutations import reservation_create_mutation, reservation_release_mutation
from .graphql.queries import reservation_query, reservations_query


class Reservations(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @guard
    def get_reservations(
        self,
        status: str = "in_progress",
    ):
        query = gql(reservations_query)

        filters = {}
        if status:
            filters["status"] = {"exact": status}

        variables = {
            "filters": filters,
        }
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def get_reservation(self, reservation_id: str):
        query = gql(reservation_query)

        variables = {
            "id": reservation_id,
        }

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def create_reservation(
        self,
        reason: str,
        wait: bool = True,
        requested_hardware_ids: Optional[List[str]] = None,
        organization_id: Optional[str] = None,
        hardware_identifier: Optional[str] = None,
    ):
        mutation = gql(reservation_create_mutation)

        if hardware_identifier and not requested_hardware_ids:
            hardware = self.primitive.hardware.get_hardware_from_slug_or_id(
                hardware_identifier=hardware_identifier
            )
            requested_hardware_ids = [hardware["id"]]

        if not organization_id:
            whoami_result = self.primitive.auth.whoami()
            default_organization = whoami_result.data["whoami"]["defaultOrganization"]
            organization_id = default_organization["id"]

        input = {
            "requestedHardwareIds": requested_hardware_ids,
            "reason": reason,
            "organizationId": organization_id,
        }

        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        if messages := result.data.get("reservationCreate").get("messages"):
            for message in messages:
                if message.get("kind") == "ERROR":
                    logger.error(message.get("message"))
                else:
                    logger.debug(message.get("message"))
            return False

        if wait:
            reservation = result.data["reservationCreate"]
            result = self.wait_for_reservation_status(
                reservation_id=reservation["id"], desired_status="in_progress"
            )

        return result

    @guard
    def release_reservation(self, reservation_or_hardware_identifier: str):
        mutation = gql(reservation_release_mutation)
        try:
            # check if it is a base64 encoded id
            type_name, _id = from_base64(reservation_or_hardware_identifier)
            if type_name == "Reservation":
                reservation_id = reservation_or_hardware_identifier
            elif type_name == "Hardware":
                hardware = self.primitive.hardware.get_hardware_from_slug_or_id(
                    hardware_identifier=reservation_or_hardware_identifier
                )
                reservation_id = hardware["activeReservation"]["id"]
        except ValueError:
            # if not, its a string and check for it here
            hardware = self.primitive.hardware.get_hardware_from_slug_or_id(
                hardware_identifier=reservation_or_hardware_identifier
            )
            reservation_id = hardware["activeReservation"]["id"]

        input = {
            "reservationId": reservation_id,
        }
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def wait_for_reservation_status(
        self, reservation_id: str, desired_status: str, total_sleep_time: int = 30
    ):
        reservation_result = self.get_reservation(reservation_id=reservation_id)
        reservation = reservation_result.data["reservation"]
        current_status = reservation["status"]

        logger.debug(
            f"Waiting {total_sleep_time}s for reservation {reservation_id} to be in_progress."
        )

        now = datetime.now()
        future_time = now + timedelta(seconds=total_sleep_time)

        while current_status != desired_status:
            now = datetime.now()
            logger.debug(
                f"[{(future_time - now).seconds}s remaining] Waiting for reservation {reservation_id} to be {desired_status}. Current status: {current_status}"
            )
            if now > future_time:
                logger.info(
                    f"Reservation {reservation_id} did not reach {desired_status} status in {total_sleep_time}s."
                )
                break
            if current_status == "completed":
                logger.error(
                    f"Reservation {reservation_id} concluded with {reservation['conclusionMessage']}. Reason: {reservation['conclusionMessage']}"
                )
                break

            reservation_result = self.get_reservation(reservation_id=reservation_id)
            reservation = reservation_result.data["reservation"]
            current_status = reservation["status"]
            if current_status == desired_status:
                break
            sleep(1)

        if current_status == "waiting_for_hardware":
            logger.info(
                f"Reservation {reservation_id} is waiting for hardware to come online."
            )

        return reservation_result

    @guard
    def get_job_run_for_reservation_id(self, reservation_id: str) -> dict:
        if not reservation_id:
            logger.error("No reservation ID provided.")
            return {}

        job_runs_for_reservation = self.primitive.jobs.get_job_runs(
            first=1,
            reservation_id=reservation_id,
        )

        while job_runs_for_reservation is None or job_runs_for_reservation.data is None:
            sleep_amount = 5
            logger.info(f"Error fetching job runs... [sleeping {sleep_amount} seconds]")
            sleep(sleep_amount)
            continue

        if not job_runs_for_reservation.data["jobRuns"]["edges"]:
            logger.info("No job runs found for the given reservation ID.")
            return {}

        return job_runs_for_reservation.data["jobRuns"]["edges"][0]["node"]
