"""
Tests for the fleetfinder.tasks module.
"""

# Standard Library
from unittest import TestCase
from unittest.mock import Mock, patch

# AA Fleet Finder
from fleetfinder.tasks import (
    _get_fleet_aggregate,
    check_fleet_adverts,
)


class TestGetFleetAggregate(TestCase):
    """
    Tests for the _get_fleet_aggregate function.
    """

    def test_returns_correct_counts_for_valid_fleet_infos(self):
        """
        Test that _get_fleet_aggregate returns correct counts for valid fleet_infos.

        :return:
        :rtype:
        """

        fleet_infos = [
            {"ship_type_name": "Cruiser"},
            {"ship_type_name": "Cruiser"},
            {"ship_type_name": "Battleship"},
        ]

        result = _get_fleet_aggregate(fleet_infos)

        assert result == {"Cruiser": 2, "Battleship": 1}

    def test_returns_empty_dict_for_empty_fleet_infos(self):
        """
        Test that _get_fleet_aggregate returns an empty dictionary for empty fleet_infos.

        :return:
        :rtype:
        """

        fleet_infos = []

        result = _get_fleet_aggregate(fleet_infos)

        assert result == {}

    def test_returns_only_valid_ship_type_names(self):
        """
        Test that _get_fleet_aggregate returns only valid ship type names.

        :return:
        :rtype:
        """

        fleet_infos = [
            {"ship_type_name": "Cruiser"},
            {},
            {"ship_type_name": None},
            {"ship_type_name": "Battleship"},
            {"other_key": "Frigate"},
        ]

        result = _get_fleet_aggregate(fleet_infos)

        assert result == {"Cruiser": 1, "Battleship": 1}


class TestCheckFleetAdvert(TestCase):
    """
    Tests for the check_fleet_adverts function.
    """

    @patch("fleetfinder.models.Fleet.objects.all")
    @patch("fleetfinder.tasks.fetch_esi_status")
    def test_processes_registered_fleets_when_available(
        self, mock_fetch_esi_status, mock_fleet_objects
    ):
        """
        Test that check_fleet_adverts processes registered fleets when ESI is available.

        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :param mock_fleet_objects:
        :type mock_fleet_objects:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = True
        mock_fleet_objects.return_value.exists.return_value = True
        mock_fleet_objects.return_value.count.return_value = 2
        mock_fleet_objects.return_value.__iter__.return_value = iter([Mock(), Mock()])

        check_fleet_adverts()

        mock_fleet_objects.return_value.__iter__.assert_called_once()
        mock_fetch_esi_status.assert_called_once()

    @patch("fleetfinder.models.Fleet.objects.all")
    @patch("fleetfinder.tasks.fetch_esi_status")
    def test_logs_no_registered_fleets_when_none_exist(
        self, mock_fetch_esi_status, mock_fleet_objects
    ):
        """
        Test that check_fleet_adverts logs a message when no registered fleets exist.

        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :param mock_fleet_objects:
        :type mock_fleet_objects:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = True
        mock_fleet_objects.return_value.exists.return_value = False

        check_fleet_adverts()

        mock_fleet_objects.return_value.exists.assert_called_once()
        mock_fetch_esi_status.assert_not_called()

    @patch("fleetfinder.models.Fleet.objects.all")
    @patch("fleetfinder.tasks.fetch_esi_status")
    def test_aborts_processing_when_esi_is_unavailable(
        self, mock_fetch_esi_status, mock_fleet_objects
    ):
        mock_fetch_esi_status.return_value.is_ok = False
        mock_fleet_objects.return_value.exists.return_value = True

        check_fleet_adverts()

        mock_fetch_esi_status.assert_called_once()
        mock_fleet_objects.return_value.__iter__.assert_not_called()
