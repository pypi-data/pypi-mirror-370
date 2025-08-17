from pathlib import Path

import pytest

from leaguemanager.dependency.loader import DynamicObjectLoader
from leaguemanager.lib.settings import get_settings

settings = get_settings()


@pytest.fixture(scope="module")
def loader() -> DynamicObjectLoader:
    """Fixture to provide a DynamicObjectLoader instance."""
    loader = DynamicObjectLoader()

    return loader


def test_get_importers(loader: DynamicObjectLoader) -> None:
    """Test that the loader can retrieve Importer classes."""
    importers = loader.get_importer_services(search_dir=settings.template_loader_dir)
    assert len(importers) == 5, "Expected 5 importers to be found"


def test_get_schedule_services(loader: DynamicObjectLoader) -> None:
    """Test that the loader can retrieve ScheduleServiceBase classes."""
    sched_services = loader.get_schedule_services(search_dir=settings.schedule_loader_dir)
    assert len(sched_services) == 4, "Expected 4 schedule services to be found"
