"""
Tasks
"""

# Standard Library
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

# Third Party
from bravado.exception import HTTPNotFound
from celery import shared_task

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce
from esi.models import Token

# Alliance Auth (External Libs)
from app_utils.esi import fetch_esi_status
from app_utils.logging import LoggerAddTag

# AA Fleet Finder
from fleetfinder import __title__
from fleetfinder.models import Fleet
from fleetfinder.providers import esi

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


ESI_ERROR_LIMIT = 50
ESI_TIMEOUT_ONCE_ERROR_LIMIT_REACHED = 60
ESI_MAX_RETRIES = 3
ESI_MAX_ERROR_COUNT = 3
ESI_ERROR_GRACE_TIME = 75

TASK_TIME_LIMIT = 120  # Stop after 2 minutes

# Params for all tasks
TASK_DEFAULT_KWARGS = {"time_limit": TASK_TIME_LIMIT, "max_retries": ESI_MAX_RETRIES}


class FleetViewAggregate:  # pylint: disable=too-few-public-methods
    """
    Helper class
    """

    def __init__(self, fleet, aggregate):
        self.fleet = fleet
        self.aggregate = aggregate


@shared_task
def _send_invitation(character_id, fleet_commander_token, fleet_id):
    """
    Open the fleet invite window in the eve client

    :param character_id:
    :param fleet_commander_token:
    :param fleet_id:
    """

    invitation = {"character_id": character_id, "role": "squad_member"}

    esi.client.Fleets.post_fleets_fleet_id_members(
        fleet_id=fleet_id,
        token=fleet_commander_token.valid_access_token(),
        invitation=invitation,
    ).result()


def _close_esi_fleet(fleet: Fleet, reason: str) -> None:
    """
    Closing registered fleet

    :param fleet:
    :param reason:
    """

    logger.info(
        msg=(
            f'Fleet "{fleet.name}" of {fleet.fleet_commander} (ESI ID: {fleet.fleet_id}) » '
            f"Closing: {reason}"
        )
    )

    fleet.delete()


def _esi_fleet_error_handling(fleet: Fleet, error_key: str) -> None:
    """
    ESI error handling

    :param fleet:
    :type fleet:
    :param error_key:
    :type error_key:
    :return:
    :rtype:
    """

    time_now = timezone.now()

    # Close ESI fleet if the consecutive error count is too high
    if (
        fleet.last_esi_error == error_key
        and fleet.last_esi_error_time
        >= (time_now - timedelta(seconds=ESI_ERROR_GRACE_TIME))
        and fleet.esi_error_count >= ESI_MAX_ERROR_COUNT
    ):
        _close_esi_fleet(fleet=fleet, reason=error_key.label)

        return

    error_count = (
        fleet.esi_error_count + 1
        if fleet.last_esi_error == error_key
        and fleet.last_esi_error_time
        >= (time_now - timedelta(seconds=ESI_ERROR_GRACE_TIME))
        else 1
    )

    logger.info(
        f'Fleet "{fleet.name}" of {fleet.fleet_commander} (ESI ID: {fleet.fleet_id}) » '
        f'Error: "{error_key.label}" ({error_count} of {ESI_MAX_ERROR_COUNT}).'
    )

    fleet.esi_error_count = error_count
    fleet.last_esi_error = error_key
    fleet.last_esi_error_time = time_now
    fleet.save()


@shared_task
def _get_fleet_aggregate(fleet_infos):
    """
    Getting numbers for fleet composition

    :param fleet_infos:
    :return:
    """

    counts = {}

    for member in fleet_infos:
        type_ = member.get("ship_type_name")

        if type_ and isinstance(type_, str) and type_.strip():
            type_ = type_.strip()  # Normalize ship type name

            if type_ in counts:
                counts[type_] += 1
            else:
                counts[type_] = 1

    return counts


def _check_for_esi_fleet(fleet: Fleet):
    """
    Check for required ESI scopes

    :param fleet:
    :type fleet:
    :return:
    :rtype:
    """

    required_scopes = ["esi-fleets.read_fleet.v1"]

    # Check if there is a fleet
    try:
        fleet_commander_id = fleet.fleet_commander.character_id
        esi_token = Token.get_token(fleet_commander_id, required_scopes)

        fleet_from_esi = esi.client.Fleets.get_characters_character_id_fleet(
            character_id=fleet_commander_id,
            token=esi_token.valid_access_token(),
        ).result()

        return {"fleet": fleet_from_esi, "token": esi_token}
    except HTTPNotFound:
        _esi_fleet_error_handling(error_key=Fleet.EsiError.NOT_IN_FLEET, fleet=fleet)
    except Exception:  # pylint: disable=broad-exception-caught
        _esi_fleet_error_handling(error_key=Fleet.EsiError.NO_FLEET, fleet=fleet)

    return False


def _process_fleet(fleet: Fleet) -> None:
    """
    Processing a fleet

    :param fleet: Fleet object to process
    :type fleet: Fleet
    :return: None
    :rtype: None
    """

    logger.info(
        f'Processing information for fleet "{fleet.name}" '
        f"of {fleet.fleet_commander} (ESI ID: {fleet.fleet_id})"
    )

    # Check if there is a fleet
    esi_fleet = _check_for_esi_fleet(fleet=fleet)

    if not esi_fleet:
        return

    # Fleet IDs don't match, FC changed fleets
    if fleet.fleet_id != esi_fleet["fleet"]["fleet_id"]:
        _esi_fleet_error_handling(
            fleet=fleet, error_key=Fleet.EsiError.FC_CHANGED_FLEET
        )
        return

    # Check if we deal with the fleet boss here
    try:
        _ = esi.client.Fleets.get_fleets_fleet_id_members(
            fleet_id=fleet.fleet_id,
            token=esi_fleet["token"].valid_access_token(),
        ).result()
    except Exception:  # pylint: disable=broad-exception-caught
        _esi_fleet_error_handling(fleet=fleet, error_key=Fleet.EsiError.NOT_FLEETBOSS)


@shared_task
def send_fleet_invitation(fleet_id: int, character_ids: list) -> None:
    """
    Send fleet invitations to characters through ESI
    This task sends fleet invitations to a list of character IDs using the ESI API.

    :param fleet_id: The ID of the fleet to which invitations are sent
    :type fleet_id: int
    :param character_ids: List of character IDs to invite to the fleet
    :type character_ids: list[int]
    :return: None
    :rtype: None
    """

    required_scopes = ["esi-fleets.write_fleet.v1"]
    fleet = Fleet.objects.get(fleet_id=fleet_id)
    fleet_commander_token = Token.get_token(
        character_id=fleet.fleet_commander.character_id, scopes=required_scopes
    )

    with ThreadPoolExecutor(max_workers=50) as ex:
        futures = [
            ex.submit(
                _send_invitation,
                character_id=character_id,
                fleet_commander_token=fleet_commander_token,
                fleet_id=fleet_id,
            )
            for character_id in character_ids
        ]

        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred


@shared_task(**{**TASK_DEFAULT_KWARGS}, **{"base": QueueOnce})
def check_fleet_adverts() -> None:
    """
    Check all registered fleets and process them

    :return: None
    :rtype: None
    """

    fleets = Fleet.objects.all()

    if not fleets.exists():
        logger.info("No registered fleets found. Nothing to do...")

        return

    logger.info(f"Processing {fleets.count()} registered fleets...")

    # Abort if ESI seems to be offline or above the error limit
    if not fetch_esi_status().is_ok:
        logger.warning("ESI doesn't seem to be available at this time. Aborting.")

        return

    for fleet in fleets:
        _process_fleet(fleet=fleet)


@shared_task
def get_fleet_composition(fleet_id: int) -> FleetViewAggregate | None:
    """
    Get the composition of a fleet by its ID
    This task retrieves the composition of a fleet using its ESI ID.

    :param fleet_id: The ESI ID of the fleet to retrieve
    :type fleet_id:  int
    :return: FleetViewAggregate containing fleet members and aggregate data
    :rtype: FleetViewAggregate | None
    """

    try:
        fleet = Fleet.objects.get(fleet_id=fleet_id)
    except Fleet.DoesNotExist:
        logger.error(f"Fleet with ID {fleet_id} not found")

        return None

    logger.info(
        f'Getting fleet composition for fleet "{fleet.name}" '
        f"of {fleet.fleet_commander.character_name} (ESI ID: {fleet_id})"
    )

    required_scopes = ["esi-fleets.read_fleet.v1"]

    try:
        token = Token.get_token(
            character_id=fleet.fleet_commander.character_id, scopes=required_scopes
        )

        fleet_infos = esi.client.Fleets.get_fleets_fleet_id_members(
            fleet_id=fleet_id, token=token.valid_access_token()
        ).result()

        # Get all unique IDs and fetch names in one call
        all_ids = {
            item_id
            for member in fleet_infos
            for item_id in [
                member["character_id"],
                member["solar_system_id"],
                member["ship_type_id"],
            ]
        }

        ids_to_name = esi.client.Universe.post_universe_names(
            ids=list(all_ids)
        ).result()

        # Create a lookup dictionary for names
        name_lookup = {item["id"]: item["name"] for item in ids_to_name}

        # Add names to fleet members
        for member in fleet_infos:
            member.update(
                {
                    "character_name": name_lookup[member["character_id"]],
                    "solar_system_name": name_lookup[member["solar_system_id"]],
                    "ship_type_name": name_lookup[member["ship_type_id"]],
                }
            )

        aggregate = _get_fleet_aggregate(fleet_infos=fleet_infos)

        return FleetViewAggregate(fleet=fleet_infos, aggregate=aggregate)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Failed to get fleet composition for fleet {fleet_id}: {e}")

        return None
