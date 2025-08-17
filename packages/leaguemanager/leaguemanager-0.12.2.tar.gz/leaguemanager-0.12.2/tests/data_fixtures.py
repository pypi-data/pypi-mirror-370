import json
from typing import Any

import pytest

from leaguemanager.lib import get_settings

settings = get_settings()


@pytest.fixture(name="all_data", autouse=True, scope="session")
def fx_all_data() -> dict[str, Any]:
    with open(settings.synth_data_dir / "example_data.json") as _data:
        data = json.load(_data)
    return data


@pytest.fixture(name="all_teams", autouse=True, scope="session")
def fx_all_teams(all_data) -> dict[str, Any]:
    return all_data["teams"]


@pytest.fixture(name="all_leagues", autouse=True, scope="session")
def fx_all_leagues(all_data) -> dict[str, Any]:
    return all_data["leagues"]


@pytest.fixture(name="all_seasons", autouse=True, scope="session")
def fx_all_seasons(all_data) -> dict[str, Any]:
    return all_data["seasons"]
