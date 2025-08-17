from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound

from leaguemanager import LeagueManager
from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.lib.toolbox import clear_table
from leaguemanager.schema import Day, GameTime, Month, Year
from leaguemanager.services import RoundRobinSchedule

org_data = {
    "name": "Test Organization",
}

league_data = {
    "name": "Test League",
}


season_data = {
    "name": "Season Test",
    "description": "Burndt",
    "projected_start_date": "2022-03-05:13:00:00",
}


team_data = [
    {"name": "Loro"},
    {"name": "June"},
    {"name": "Tripoli"},
    {"name": "Tres"},
]

ruleset_data = {
    "game_length": 45,
    "time_between": 15,
    "number_of_teams": 4,
    "number_of_phases": 10,
    "venue_count": 1,
}


@pytest.fixture(scope="module")
def _setup_db(
    org_service,
    league_service,
    season_service,
    team_service,
    team_member_service,
    ruleset_service,
    session,
):
    """Fixture to set up the database with test data."""
    # Clear existing data
    clear_table(session, m.Organization)
    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.Ruleset)

    # Create organization
    org = org_service.create(org_data, auto_commit=True)

    # Create League linked to the organization
    league_data["organization_id"] = org.id
    league = league_service.create(league_data, auto_commit=True)

    # Create Season linked to the league
    season_data["league_id"] = league.id
    season = season_service.create(season_data, auto_commit=True)

    # Create TeamMembership objects for each team
    for team in team_data:
        team_membership = team_member_service.create(
            {
                "season_id": season.id,
                "label": f"{team['name']} - Season: {season.name}",
                "auto_commit": True,
            }
        )
        team["team_membership_id"] = team_membership.id
        team_service.create(team, auto_commit=True)

    # Create Ruleset linked to the season
    ruleset_data["season_id"] = season.id
    _ = ruleset_service.create(ruleset_data, auto_commit=True)


@pytest.fixture(scope="module")
def season(_setup_db, season_service):
    """Fixture to provide the current season."""
    try:
        return season_service.get(id_attribute="name", item_id=season_data["name"])
    except NotFoundError as e:
        raise ValueError(f"Season with name {season_data['name']} does not exist in the database.") from e


@pytest.fixture(scope="module")
def scheduler(
    season,
    season_service,
    ruleset_service,
    phase_service,
    fixture_service,
    team_service,
):
    """Fixture to provide a RoundRobinSchedule instance."""
    mock_lm = MagicMock(spec=LeagueManager)
    scheduler = RoundRobinSchedule(mock_lm, season)

    # Patch the season_service and ruleset_service into RoundRobinSchedule properties
    mock_lm.provide_db_service.side_effect = lambda service_type: {
        s.SeasonService: season_service,
        s.RulesetService: ruleset_service,
        s.PhaseService: phase_service,
        s.FixtureService: fixture_service,
        s.TeamService: team_service,
    }.get(service_type, None)

    return scheduler


def test_round_robin_schedule_initialization(scheduler, season):
    """Test the initialization of the RoundRobinSchedule service."""

    assert isinstance(scheduler, RoundRobinSchedule)
    assert scheduler.season == season
    assert len(scheduler.teams) == 4


def test_round_robin_split_teams(scheduler):
    """Test the splitting of teams into fixtures."""
    teams_a, teams_b = scheduler.split_teams(scheduler.teams)

    assert len(teams_a) == 2
    assert len(teams_b) == 2


@pytest.mark.parametrize(
    "venue_count, match_number, expected_venue",
    [
        (1, 1, 1),
        (1, 2, 1),
        (3, 3, 3),
        (3, 4, 1),
        (2, 2, 2),
        (2, 3, 1),
        (2, 6, 2),
        (4, 10, 2),
    ],
)
def test_round_robin_generate_venue(scheduler, venue_count, match_number, expected_venue):
    """Test the generation of venues for the round-robin schedule."""
    scheduler.ruleset.venue_count = venue_count
    venue = scheduler.generate_venue_number(match_number)
    assert venue == expected_venue


@pytest.mark.parametrize(
    "td_minutes, multiplier, expected_hrs, expected_mins",
    [
        (35, 1, 0, 35),
        (75, 1, 1, 15),
        (125, 1, 2, 5),
        (60, 1, 1, 0),
        (45, 2, 1, 30),
        (35, 5, 2, 55),
    ],
)
def test_round_robin_convert_to_hrs_mins(scheduler, td_minutes, expected_hrs, expected_mins, multiplier):
    td = timedelta(minutes=td_minutes)
    hours, minutes = scheduler._convert_to_hours_and_minutes(td, multiplier)
    assert hours == expected_hrs
    assert minutes == expected_mins


@pytest.mark.parametrize(
    "game_length, time_between, match_count, venue_count, expected_hour, expected_minute",
    [
        (45, 15, 1, 1, 13, 0),
        (30, 10, 2, 1, 13, 40),
        (60, 0, 2, 1, 14, 0),
        (45, 20, 4, 2, 14, 5),
        (40, 5, 11, 3, 15, 15),
        (50, 10, 6, 2, 15, 0),
        (25, 0, 9, 1, 16, 20),  # 25 mins * 8 = 200 mins, 3 hrs 20 mins
    ],
)
def test_round_robin_increment_time(
    scheduler,
    game_length,
    time_between,
    venue_count,
    match_count,
    expected_hour,
    expected_minute,
):
    """Test the time increment logic in the round-robin schedule."""
    scheduler.ruleset.game_length = game_length
    scheduler.ruleset.time_between = time_between
    scheduler.ruleset.venue_count = venue_count
    match_count = match_count

    match_date = scheduler.season.projected_start_date

    gametime = scheduler._increment_time(match_count, match_date)

    expected = GameTime(
        year=Year(match_date.year),
        month=Month(match_date.month),
        day=Day(match_date.day),
        hour=expected_hour,
        minute=expected_minute,
        total_duration_in_minutes=scheduler.ruleset.game_length + scheduler.ruleset.time_between,
    )

    assert expected == gametime


def test_round_robin_get_or_create_phases(
    scheduler,
    season,
    season_service,
    ruleset_service,
    phase_service,
):
    """Test the get_or_create_phases method."""
    phases = scheduler.season.phases
    assert len(phases) == 0  # Initially, there should be no phases

    _ = scheduler.get_or_create_phases("GameWeek")
    phases = scheduler.season.phases
    assert len(phases) == 10  # Assuming 10 phases as per ruleset


def test_round_robin_create_matchups(scheduler):
    """Test the create_matchups method."""
    ...
