from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from advanced_alchemy.filters import CollectionFilter, OnBeforeAfter
from sqlalchemy.exc import NoResultFound

from leaguemanager.lib.toolbox import clear_table
from leaguemanager.models import Fixture, Team
from leaguemanager.services import (
    FixtureService,
    LeagueService,
    SeasonService,
    TeamService,
)


@pytest.fixture(scope="module")
def season(season_service) -> SeasonService:
    season = season_service.create(
        data={"name": "SZNZ", "description": "Winter", "projected_start_date": "2022-01-01"}, auto_commit=True
    )
    return season


@pytest.fixture(scope="module")
def league(league_service, season) -> LeagueService:
    league = league_service.create(data={"name": "Men's 7v7", "category": "MEN", "division": "A", "match_day": "SUN"})
    league.season = season
    league = league_service.update(league, auto_commit=True)
    return league


@pytest.fixture(scope="module")
def teams(team_service, league_service, league) -> TeamService:
    teams = team_service.create_many(
        [
            {"name": "Team 1", "league_id": league.id},
            {"name": "Team 2", "league_id": league.id},
            {"name": "Team 3", "league_id": league.id},
            {"name": "Team 4", "league_id": league.id},
        ]
    )
    league.teams = teams
    league_service.update(league, auto_commit=True)
    return teams


# @pytest.fixture(scope="module")
# def schedule(schedule_service, league, season, teams) -> ScheduleService:
#     _schedule = {
#         "name": "I Want A Dog",
#         "total_games": 10,
#         "game_length": 45,
#         "time_between_games": 15,
#         "start_date": "2025-1-05 16:00:00",
#         "season_id": season.id,
#         "league_id": league.id,
#         "teams": teams,
#     }

#     schedule = schedule_service.create(_schedule)
#     return schedule


# @pytest.fixture(scope="module")
# def scheduler(session, schedule) -> Scheduler:
#     scheduler = Scheduler(session=session, schedule=schedule)
#     return scheduler


# @pytest.fixture(scope="module")
# def league_fixtures(fixture_service, scheduler) -> FixtureService:
#     fixtures = scheduler.generate_fixtures(shuffle_teams=False)
#     fixture_service.create_many(fixtures, auto_commit=True)
#     return fixtures


# @pytest.fixture(scope="module")
# def standings_table(session, schedule):
#     standings_table = StandingsTable(
#         session=session,
#         schedule=schedule,
#     )

#     return standings_table


# def test_standings_table_properties(schedule, standings_table):
#     assert standings_table.schedule == schedule
#     assert standings_table.schedule.season == schedule.season
#     assert standings_table.schedule.season.name == "SZNZ"


# def test_get_or_create_standings(standings_table, standings_service):
#     standings = standings_table.get_or_create_current_standings()
#     assert len(standings) == 4

#     for standing in standings:
#         standing.games_played = 1
#         standings_service.update(standing, auto_commit=True)

#     new_standings = standings_table.get_or_create_current_standings()
#     assert len(new_standings) == 4
#     assert new_standings[0].games_played == 1
#     assert new_standings[1].games_played == 1
#     assert new_standings[2].games_played == 1
#     assert new_standings[3].games_played == 1


# def test_past_fixtures_all_unplayed(standings_table, league_fixtures, fixture_service):
#     fixtures = standings_table.past_fixtures
#     assert len(fixtures) == 0

#     _fixture = league_fixtures[0]
#     _fixture.status = "P"
#     fixture_service.update(_fixture, auto_commit=True)

#     fixtures = standings_table.past_fixtures
#     assert len(fixtures) == 1
#     _fixture = league_fixtures[0]
#     _fixture.status = "U"
#     fixture_service.update(_fixture, auto_commit=True)


# def test_remaining_fixtures_all_unplayed(standings_table, league_fixtures, fixture_service):
#     fixtures = standings_table.remaining_fixtures
#     assert len(fixtures) == 16

#     _fixture = league_fixtures[0]
#     _fixture.status = "P"
#     fixture_service.update(_fixture, auto_commit=True)

#     fixtures = standings_table.remaining_fixtures
#     assert len(fixtures) == 15
#     _fixture = league_fixtures[0]
#     _fixture.status = "U"
#     fixture_service.update(_fixture, auto_commit=True)


# @pytest.mark.parametrize("time_delta_days, expected", [(6, 2), (12, 4), (24, 8)])
# def test_next_scheduled_fixtures(standings_table, league_fixtures, time_delta_days, expected):
#     # Note: league_fixtures needs to be here to generate fixtures for this test
#     # if run individually.
#     all_fixtures = standings_table.all_fixtures
#     assert len(all_fixtures) == 16
#     assert all_fixtures[0].date == datetime(2025, 1, 5, 16, 0)
#     assert all_fixtures[1].date == datetime(2025, 1, 5, 16, 0)

#     filter = OnBeforeAfter(
#         field_name="date",
#         on_or_after=datetime(2025, 1, 4, 16, 0),
#         on_or_before=datetime(2025, 1, 4, 16, 0) + timedelta(days=time_delta_days),
#     )

#     fixtures = standings_table.next_scheduled_fixtures(filter=filter)
#     assert len(fixtures) == expected


# def test_link_teams_to_fixtures(standings_table, league_fixtures):
#     # Note: league_fixtures needs to be here to generate fixtures for this test
#     # if run individually.
#     fixture_teams = standings_table.link_teams_to_fixtures()
#     assert len(fixture_teams) == 32


# def test_link_teams_to_fixtures_when_no_fixtures(session, schedule_service):
#     temp_schedule = Schedule(
#         season_id=uuid4(),
#         league_id=uuid4(),
#         start_date="2021-1-08 18:00:00",
#         end_date="2022-02-01 18:00:00",
#         total_games=0,
#     )
#     temp_standings = StandingsTable(session=session, schedule=temp_schedule)

#     with pytest.raises(NoResultFound):
#         temp_standings.link_teams_to_fixtures()


# def test_team_update_standings(
#     league, session, schedule, standings_service, fixture_team_service, mocker, team_service
# ):
#     mock_home_team = Team(league_id=league.id, name="Mock Home")
#     mock_away_team = Team(league_id=league.id, name="Mock Away")

#     team_service.create(mock_home_team)
#     team_service.create(mock_away_team)

#     fake_fixture = Fixture(
#         home_team_id=mock_home_team.id,
#         away_team_id=mock_away_team.id,
#         schedule_id=uuid4(),
#         status="P",
#         home_goals=3,
#         away_goals=1,
#     )

#     mock_home_stat = FixtureTeam(
#         team_id=mock_home_team.id,
#         fixture_id=fake_fixture.id,
#         is_played=True,
#         points=3,
#         score_for=3,
#         score_against=1,
#         fixture_result="W",
#     )
#     mock_away_stat = FixtureTeam(
#         team_id=mock_away_team.id,
#         fixture_id=fake_fixture.id,
#         is_played=True,
#         points=0,
#         score_for=1,
#         score_against=3,
#         fixture_result="L",
#     )

#     fixture_team_service.create(mock_home_stat)
#     fixture_team_service.create(mock_away_stat)

#     mock_standings = Standings(
#         schedule_id=schedule.id,
#         team_id=mock_home_team.id,
#     )

#     standings_service.create(mock_standings)

#     tabulate_fixture = TabulateFixture(
#         session=session,
#         fixture=fake_fixture,
#     )

#     expected_standings_after_update = Standings(
#         schedule_id=schedule.id,
#         team_id=mock_home_team.id,
#         points=3,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     mocker.patch.object(standings_service, "get", return_value=mock_standings)

#     updated_standings = tabulate_fixture.update_standings(mock_home_team, mock_home_stat)
#     assert updated_standings.points == expected_standings_after_update.points
#     assert updated_standings.score_for == expected_standings_after_update.score_for
#     assert updated_standings.games_played == expected_standings_after_update.games_played

#     team_service.delete(mock_home_team.id)
#     team_service.delete(mock_away_team.id)
#     fixture_team_service.delete(mock_home_stat.id)
#     fixture_team_service.delete(mock_away_stat.id)
#     standings_service.delete(mock_standings.id)


# @pytest.mark.parametrize(["prior_home_points", "expected"], [(0, 3), (1, 4), (6, 9)])
# def test_process_fixture_results(
#     league, schedule, session, standings_service, fixture_team_service, team_service, prior_home_points, expected
# ):
#     mock_home_team = Team(league_id=league.id, name="Mock Home")
#     mock_away_team = Team(league_id=league.id, name="Mock Away")

#     team_service.create(mock_home_team)
#     team_service.create(mock_away_team)

#     fake_fixture = Fixture(
#         home_team_id=mock_home_team.id,
#         away_team_id=mock_away_team.id,
#         schedule_id=uuid4(),
#         status="P",
#         home_goals=3,
#         away_goals=1,
#     )

#     mock_home_stat = FixtureTeam(
#         team_id=mock_home_team.id,
#         fixture_id=fake_fixture.id,
#         is_played=True,
#         points=3,
#         score_for=3,
#         score_against=1,
#         fixture_result="W",
#     )
#     mock_away_stat = FixtureTeam(
#         team_id=mock_away_team.id,
#         fixture_id=fake_fixture.id,
#         is_played=True,
#         points=0,
#         score_for=1,
#         score_against=3,
#         fixture_result="L",
#     )

#     fixture_team_service.create(mock_home_stat)
#     fixture_team_service.create(mock_away_stat)

#     home_standings = Standings(
#         schedule_id=schedule.id,
#         team_id=mock_home_team.id,
#         points=prior_home_points,
#     )

#     away_standings = Standings(
#         schedule_id=schedule.id,
#         team_id=mock_away_team.id,
#     )

#     standings_service.create(home_standings)
#     standings_service.create(away_standings)

#     tabulate_fixture = TabulateFixture(session=session, fixture=fake_fixture)

#     home_standings, away_standings = tabulate_fixture.process_fixture_results()

#     assert home_standings.games_played == 1
#     assert home_standings.games_won == 1
#     assert home_standings.games_drawn == 0
#     assert home_standings.games_lost == 0
#     assert home_standings.score_for == 3
#     assert home_standings.score_against == 1
#     assert home_standings.score_diff == 2
#     assert home_standings.points == expected

#     assert away_standings.games_played == 1
#     assert away_standings.games_won == 0
#     assert away_standings.games_drawn == 0
#     assert away_standings.games_lost == 1
#     assert away_standings.score_for == 1
#     assert away_standings.score_against == 3
#     assert away_standings.score_diff == -2
#     assert away_standings.points == 0

#     team_service.delete(mock_home_team.id)
#     team_service.delete(mock_away_team.id)
#     fixture_team_service.delete(mock_home_stat.id)
#     fixture_team_service.delete(mock_away_stat.id)
#     standings_service.delete(home_standings.id)
#     standings_service.delete(away_standings.id)


# def test_generate_standings_table(schedule, session, standings_service, standings_table):
#     standings_1 = Standings(
#         schedule_id=schedule.id,
#         team_id=standings_table.teams[0].id,
#         points=3,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=-5,
#     )

#     standings_2 = Standings(
#         schedule_id=schedule.id,
#         team_id=standings_table.teams[1].id,
#         points=3,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     standings_3 = Standings(
#         schedule_id=schedule.id,
#         team_id=standings_table.teams[2].id,
#         points=6,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     standings_4 = Standings(
#         schedule_id=schedule.id,
#         team_id=standings_table.teams[3].id,
#         points=12,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     standings_other_schedule = Standings(
#         schedule_id=uuid4(),
#         team_id=standings_table.teams[3].id,
#         points=200,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     standings_other_team = Standings(
#         schedule_id=schedule.id,
#         team_id=uuid4(),
#         points=100,
#         games_played=1,
#         games_won=1,
#         games_drawn=0,
#         games_lost=0,
#         score_for=3,
#         score_against=1,
#         score_diff=2,
#     )

#     clear_table(session, Standings)
#     standings_service.create_many(
#         [standings_1, standings_2, standings_3, standings_4, standings_other_schedule, standings_other_team]
#     )

#     standings = standings_table.generate_standings_table()

#     assert len(standings) == 4
#     assert standings[0].team_id == standings_table.teams[3].id
#     assert standings[0].points == 12
#     assert standings[1].team_id == standings_table.teams[2].id
#     assert standings[2].team_id == standings_table.teams[1].id
#     assert standings[2].points == 3
#     assert standings[2].score_diff == 2
#     assert standings[3].team_id == standings_table.teams[0].id
#     assert standings[3].points == 3
#     assert standings[3].score_diff == -5

#     clear_table(session, Standings)
