"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA Fleet Finder
from fleetfinder import __version__


class FleetFinderConfig(AppConfig):
    """
    Application config
    """

    name = "fleetfinder"
    label = "fleetfinder"
    # Translators: This is the app name and version, which will appear in the Django Backend
    verbose_name = _(f"Fleet Finder v{__version__}")
