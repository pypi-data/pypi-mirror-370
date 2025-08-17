import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.lib.toolbox import clear_table

org_data = {
    "name": "Test Organization",
}

league_data = {
    "name": "Test League",
}


season_data = {
    "name": "Season Test",
    "description": "Burndt",
    "projected_start_date": "2022-01-01",
}


team_data = [
    {"name": "Loro"},
    {"name": "June"},
    {"name": "Tripoli"},
    {"name": "Tres", "active": False},
]


@pytest.fixture(scope="module")
def org(org_service):
    return org_service.create(
        {
            "name": "Test Organization",
        },
        auto_commit=True,
    )


@pytest.fixture(scope="module")
def league():
    return m.League(**league_data)


@pytest.fixture(scope="module")
def properties(league_properties_service):
    return league_properties_service.create(
        {"sport": "Tiddlywinks", "category": "COED", "division": "A"},
        auto_commit=True,
    )


@pytest.fixture(scope="module")
def ruleset(ruleset_service):
    return ruleset_service.create(
        {
            "number_of_phases": 10,
            "sun_fixtures": True,
        },
        auto_commit=True,
    )


@pytest.fixture(scope="module")
def season():
    return m.Season(**season_data)


@pytest.fixture(scope="module")
def teams():
    return [m.Team(**data) for data in team_data]


def test_create_many_leagues(session, league_service) -> None:
    new_leagues_data = [
        {
            "name": "Test Create League",
            "description": "Test Description",
            "sport": "Football",
        },
        {
            "name": "Test Create League 2",
            "description": "Test Description 2",
            "sport": "Football",
        },
    ]

    _ = league_service.create_many(new_leagues_data)

    assert league_service.count() == 2
    clear_table(session, m.League)


def test_delete_league(league_service) -> None:
    new_league = m.League(name="Test Delete League 2", description="Hi")
    test_league = league_service.create(new_league)
    league_service.delete(test_league.id)
    assert league_service.get_one_or_none(name="Test Delete League 2") is None


def test_org_with_league(session, league_service, season_service, org) -> None:
    new_league = m.League(name="Test Create League", description="boo", organization_id=org.id)
    temp_league = league_service.create(new_league, auto_commit=True)

    assert temp_league.name == "Test Create League"
    assert temp_league.organization_id == org.id

    clear_table(session, m.League)


def test_league_with_properties(session, league_service, league_properties_service, league, properties) -> None:
    new_league = league_service.create(league, auto_commit=True)
    properties.league_id = new_league.id
    league_properties_service.update(properties, auto_commit=True)

    _properties = new_league.league_properties

    assert new_league.name == "Test League"
    assert _properties.sport == "Tiddlywinks"

    clear_table(session, m.League)
    clear_table(session, m.LeagueProperties)


def test_league_with_season(session, league_service, season_service, org, league, season) -> None:
    new_league = league_service.create(league, auto_commit=True)
    new_league.organization_id = org.id
    new_season = season_service.create(season, auto_commit=True)
    new_season.league_id = new_league.id
    new_league.seasons.append(new_season)

    assert new_league.name == "Test League"
    assert new_season.name == "Season Test"

    clear_table(session, m.League)
    clear_table(session, m.Season)


def test_append_league_to_season(session, season_service, league_service) -> None:
    league_data = {
        "name": "Songs 2",
        "description": "I do a sport",
        "sport": "Music",
    }
    season_data = {
        "name": "SZNZ 2",
        "description": "I Want A Dog",
        "projected_start_date": "2025-01-01",
    }

    league = league_service.create(data=league_data, auto_commit=True)
    season = season_service.create(data=season_data, auto_commit=True)

    league.seasons.append(season)

    assert league_service.get_one_or_none(name="Songs 2").seasons[0].name == "SZNZ 2"
    assert season_service.get_one_or_none(name="SZNZ 2").league.name == "Songs 2"

    clear_table(session, m.League)
    clear_table(session, m.Season)


def test_season_with_ruleset(session, season_service, league_service, org, league, season, ruleset) -> None:
    new_league = league_service.create(league, auto_commit=True)
    new_league.organization_id = org.id
    new_season = season_service.create(season, auto_commit=True)
    new_season.league_id = new_league.id

    new_season.ruleset = ruleset

    assert new_season.ruleset.number_of_phases == 10
    assert new_season.ruleset.sun_fixtures is True

    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Ruleset)
