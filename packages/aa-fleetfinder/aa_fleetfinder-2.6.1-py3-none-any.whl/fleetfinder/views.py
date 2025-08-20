"""
Views
"""

# Third Party
from bravado.exception import HTTPNotFound

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import character_portrait_url
from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_all_characters_from_user
from allianceauth.groupmanagement.models import AuthGroup
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required
from esi.models import Token

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Fleet Finder
from fleetfinder import __title__
from fleetfinder.models import Fleet
from fleetfinder.providers import esi
from fleetfinder.tasks import get_fleet_composition, send_fleet_invitation

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def _get_and_validate_fleet(token: Token, character_id: int) -> tuple:
    """
    Get fleet information and validate fleet commander permissions

    :param token: Token object containing the access token
    :type token: Token
    :param character_id: The character ID of the fleet commander
    :type character_id: int
    :return: Tuple containing the fleet result, fleet commander, and fleet ID
    :rtype: tuple
    """

    fleet_result = esi.client.Fleets.get_characters_character_id_fleet(
        character_id=token.character_id, token=token.valid_access_token()
    ).result()

    logger.debug(f"Fleet result: {fleet_result}")

    fleet_commander = EveCharacter.objects.get(character_id=token.character_id)
    fleet_id = fleet_result.get("fleet_id")
    fleet_boss_id = fleet_result.get("fleet_boss_id")

    if not fleet_id:
        raise ValueError(f"No fleet found for {fleet_commander.character_name}")

    if fleet_boss_id != character_id:
        raise ValueError(f"{fleet_commander.character_name} is not the fleet boss")

    return fleet_result


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def dashboard(request):
    """
    Dashboard view

    :param request:
    :return:
    """

    context = {}

    logger.info(msg=f"Module called by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/dashboard.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def ajax_dashboard(request) -> JsonResponse:  # pylint: disable=too-many-locals
    """
    Ajax :: Dashboard information

    :param request:
    :return:
    """

    data = []
    groups = request.user.groups.all()
    user_characters = get_all_characters_from_user(user=request.user)
    fleets = (
        Fleet.objects.filter(
            Q(groups__group__in=groups)
            | Q(groups__isnull=True)
            | Q(fleet_commander__in=user_characters)
        )
        .distinct()
        .order_by("name")
    )

    for fleet in fleets:
        fleet_commander_name = fleet.fleet_commander.character_name
        fleet_commander_portrait_url = character_portrait_url(
            character_id=fleet.fleet_commander.character_id, size=32
        )
        fleet_commander_portrait = (
            '<img class="rounded eve-character-portrait" '
            f'src="{fleet_commander_portrait_url}" '
            f'alt="{fleet_commander_name}" loading="lazy">'
        )
        fleet_commander_html = fleet_commander_portrait + fleet_commander_name

        button_join_url = reverse(
            viewname="fleetfinder:join_fleet", args=[fleet.fleet_id]
        )
        button_join_text = _("Join fleet")
        button_join = (
            f'<a href="{button_join_url}" '
            f'class="btn btn-sm btn-primary">{button_join_text}</a>'
        )

        button_details = ""
        button_edit = ""

        if request.user.has_perm(perm="fleetfinder.manage_fleets"):
            button_details_url = reverse(
                viewname="fleetfinder:fleet_details", args=[fleet.fleet_id]
            )
            button_details_text = _("View fleet details")
            button_details = (
                f'<a href="{button_details_url}" '
                f'class="btn btn-sm btn-primary">{button_details_text}</a>'
            )

            button_edit_url = reverse(
                viewname="fleetfinder:edit_fleet", args=[fleet.fleet_id]
            )
            button_edit_text = _("Edit fleet advert")
            button_edit = (
                f'<a href="{button_edit_url}" '
                f'class="btn btn-sm btn-primary">{button_edit_text}</a>'
            )

        data.append(
            {
                "fleet_commander": {
                    "html": fleet_commander_html,
                    "sort": fleet_commander_name,
                },
                "fleet_name": fleet.name,
                "created_at": fleet.created_at,
                "join": button_join,
                "details": button_details,
                "edit": button_edit,
            }
        )

    return JsonResponse(data=data, safe=False)


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
@token_required(scopes=("esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"))
def create_fleet(request, token):
    """
    Create fleet view

    :param request:
    :param token:
    :return:
    """

    # Validate the token and check if the character is in a fleet and is the fleet boss
    try:
        _get_and_validate_fleet(token, token.character_id)
    except (HTTPNotFound, ValueError) as ex:
        logger.debug(f"Error during fleet creation: {ex}", exc_info=True)

        if isinstance(ex, HTTPNotFound):
            error_detail = ex.swagger_result["error"]
        else:
            error_detail = str(ex)

        error_message = _(
            f"<h4>Error!</h4><p>There was an error creating the fleet: {error_detail}</p>"
        )

        messages.error(request, mark_safe(error_message))

        return redirect("fleetfinder:dashboard")

    if request.method != "POST":
        return redirect("fleetfinder:dashboard")

    auth_groups = AuthGroup.objects.filter(internal=False)
    context = {"character_id": token.character_id, "auth_groups": auth_groups}

    return render(
        request=request,
        template_name="fleetfinder/create-fleet.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def edit_fleet(request, fleet_id):
    """
    Fleet edit view

    :param request:
    :param fleet_id:
    :return:
    """

    try:
        fleet = Fleet.objects.get(fleet_id=fleet_id)
    except Fleet.DoesNotExist:
        logger.debug(f"Fleet with ID {fleet_id} does not exist.")

        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>Fleet does not exist or is no longer available.</p>"
                )
            ),
        )

        return redirect("fleetfinder:dashboard")

    auth_groups = AuthGroup.objects.filter(internal=False)

    context = {
        "character_id": fleet.fleet_commander.character_id,
        "auth_groups": auth_groups,
        "fleet": fleet,
    }

    logger.debug("Context for fleet edit: %s", context)

    logger.info(msg=f"Fleet {fleet_id} edit view by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/edit-fleet.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def join_fleet(request, fleet_id):
    """
    Join fleet view

    :param request:
    :param fleet_id:
    :return:
    """

    context = {}
    groups = request.user.groups.all()
    fleet = Fleet.objects.filter(
        Q(groups__group__in=groups) | Q(groups=None), fleet_id=fleet_id
    ).count()

    if fleet == 0:
        return redirect(to="fleetfinder:dashboard")

    if request.method == "POST":
        character_ids = request.POST.getlist(key="character_ids", default=[])
        send_fleet_invitation.delay(character_ids=character_ids, fleet_id=fleet_id)

        return redirect(to="fleetfinder:dashboard")

    characters = (
        EveCharacter.objects.filter(character_ownership__user=request.user)
        .select_related()
        .order_by("character_name")
    )

    context["characters"] = characters

    return render(
        request=request,
        template_name="fleetfinder/join-fleet.html",
        context=context,
    )


@login_required()
@permission_required("fleetfinder.manage_fleets")
def save_fleet(request):
    """
    Save fleet

    :param request:
    :return:
    """

    def _edit_or_create_fleet(
        character_id: int,
        free_move: bool,
        name: str,
        groups: list,
        motd: str = None,  # pylint: disable=unused-argument
    ) -> None:
        """
        Edit or create a fleet from a fleet in EVE Online

        :param character_id: The character ID of the fleet commander
        :type character_id: int
        :param free_move: Whether the fleet is free move or not
        :type free_move: bool
        :param name: Name of the fleet
        :type name: str
        :param groups: Groups that are allowed to access the fleet
        :type groups: list[AuthGroup]
        :param motd: Message of the Day for the fleet
        :type motd: str
        :return: None
        :rtype: None
        """

        required_scopes = ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"]
        token = Token.get_token(character_id=character_id, scopes=required_scopes)

        fleet_result = _get_and_validate_fleet(token, character_id)
        fleet_commander = EveCharacter.objects.get(character_id=character_id)
        fleet_id = fleet_result.get("fleet_id")

        fleet, created = Fleet.objects.get_or_create(
            fleet_id=fleet_id,
            defaults={
                "created_at": timezone.now(),
                # "motd": motd,
                "is_free_move": free_move,
                "fleet_commander": fleet_commander,
                "name": name,
            },
        )

        if not created:
            fleet.is_free_move = free_move
            fleet.name = name
            fleet.save()

        fleet.groups.set(groups)

        esi.client.Fleets.put_fleets_fleet_id(
            fleet_id=fleet_id,
            token=token.valid_access_token(),
            # new_settings={"is_free_move": free_move, "motd": motd},
            new_settings={"is_free_move": free_move},
        ).result()

    if request.method != "POST":
        return redirect("fleetfinder:dashboard")

    # Extract form data
    form_data = {
        "character_id": int(request.POST["character_id"]),
        "free_move": request.POST.get("free_move") == "on",
        # "motd": request.POST.get("motd", ""),
        "name": request.POST.get("name", ""),
        "groups": request.POST.getlist("groups", []),
    }

    logger.debug(f"Form data for fleet creation: {form_data}")

    try:
        _edit_or_create_fleet(**form_data)
    except HTTPNotFound as ex:
        logger.debug(f"ESI returned 404 for fleet creation: {ex}", exc_info=True)

        esi_error = ex.swagger_result.get("error", "Unknown error")
        error_message = _(
            f"<h4>Error!</h4><p>ESI returned the following error: {esi_error}</p>"
        )

        messages.error(request, mark_safe(error_message))
    except ValueError as ex:
        logger.debug(f"Value error during fleet creation: {ex}", exc_info=True)

        error_message = _(
            f"<h4>Error!</h4><p>There was an error creating the fleet: {ex}</p>"
        )

        messages.error(request, mark_safe(error_message))

    return redirect("fleetfinder:dashboard")


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def fleet_details(request, fleet_id):
    """
    Fleet details view

    :param request:
    :param fleet_id:
    :return:
    """

    context = {"fleet_id": fleet_id}

    logger.info(msg=f"Fleet {fleet_id} details view called by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/fleet-details.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def ajax_fleet_details(
    request,  # pylint: disable=unused-argument
    fleet_id,
) -> JsonResponse:
    """
    Ajax :: Fleet Details

    :param request:
    :param fleet_id:
    """

    fleet = get_fleet_composition(fleet_id)

    data = {
        "fleet_member": list(fleet.fleet),
        "fleet_composition": [
            {"ship_type_name": ship, "number": number}
            for ship, number in fleet.aggregate.items()
        ],
    }

    return JsonResponse(data=data, safe=False)
