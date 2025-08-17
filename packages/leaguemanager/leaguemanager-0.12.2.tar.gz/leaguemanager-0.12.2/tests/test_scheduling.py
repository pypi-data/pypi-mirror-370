import pytest
from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound

from leaguemanager import LeagueManager
from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.lib.toolbox import clear_table
# from leaguemanager.domain.competition import Scheduler


# @pytest.fixture(scope="module")
# def base_season(all_data, org_service, league_service, season_service):
#     org = org_service.create(all_data["organization"], auto_commit=True)
#     league = league_service.create(all_data["leagues"][0], auto_commit=True)
#     season = season_service.create(all_data["seasons"][0], auto_commit=True)

#     league.organization_id = org.id
#     season.league_id = league.id

#     league_service.update(league, auto_commit=True)
#     season_service.update(season, auto_commit=True)

#     return season


# def test_season(base_season):
#     assert base_season.name == "Test Season"
#     assert base_season.league.name == "Test League"


# def test_scheduler_properties_no_ruleset(base_season):
#     scheduler = Scheduler(season=base_season)
#     assert scheduler.season == base_season
#     assert scheduler.league == base_season.league

#     with pytest.raises(NotFoundError, match="Ruleset not found"):
#         _ = scheduler.ruleset

#     with pytest.raises(NotFoundError, match="Ruleset not found"):
#         _ = scheduler.total_games

#     with pytest.raises(NotFoundError, match="Ruleset not found"):
#         _ = scheduler.start_date

#     with pytest.raises(NotFoundError, match="Ruleset not found"):
#         _ = scheduler.total_teams


# def test_scheduler_properties_with_ruleset(base_season, season_service):
#     ruleset = m.Ruleset(
#         number_of_games=10,
#         start_date="2025-01-05 08:00:00",
#         schedule_type="ROUNDROBIN",
#         season_id=base_season.id,
#     )

#     base_season.ruleset = ruleset
#     season_service.update(base_season, auto_commit=True)
#     scheduler = Scheduler(season=base_season)

#     assert base_season.ruleset == ruleset
#     assert scheduler.ruleset == ruleset
#     assert scheduler.total_games == 10
#     assert scheduler.start_date == ruleset.start_date


# def test_scheduler_all_teams(session, base_season, season_service, team_service, team_member_service):
#     team_a_member = m.TeamMembership(label="Member A", season_id=base_season.id)
#     team_b_member = m.TeamMembership(label="Member B", season_id=base_season.id)
#     team_c_member = m.TeamMembership(label="Member C", season_id=base_season.id)
#     team_d_member = m.TeamMembership(label="Member B", season_id=base_season.id)

#     team_member_service.create_many([team_a_member, team_b_member, team_c_member, team_d_member], auto_commit=True)

#     _teams = [
#         m.Team(name="Team A", team_membership_id=team_a_member.id),
#         m.Team(name="Team B", team_membership_id=team_b_member.id),
#         m.Team(name="Team C", team_membership_id=team_c_member.id),
#         m.Team(name="Team D", team_membership_id=team_d_member.id),
#     ]

#     teams = team_service.create_many(_teams, auto_commit=True)
#     member = team_member_service.get(team_a_member.id)

#     assert member is not None
#     assert team_a_member.id == teams[0].team_membership_id

#     all_teams = season_service.all_teams(base_season.id)
#     assert len(all_teams) == 4
#     assert all(team.name in [t.name for t in all_teams] for team in teams)
#     assert len(base_season.team_memberships) == 4

#     clear_table(session, m.Team)
#     clear_table(session, m.TeamMembership)


# def test_scheduler_create_dummy_teams_if_none(session, base_season, season_service, team_member_service, team_service):
#     ruleset = m.Ruleset(
#         number_of_games=10,
#         number_of_teams=5,
#         start_date="2025-01-05 08:00:00",
#         schedule_type="ROUNDROBIN",
#         season_id=base_season.id,
#     )

#     base_season.ruleset = ruleset
#     season_service.update(base_season, auto_commit=True)
#     scheduler = Scheduler(
#         season=base_season,
#         season_service=season_service,
#         team_member_service=team_member_service,
#         team_service=team_service,
#     )

#     # Since no teams currently present, the `total_teams` property creates placeholder teams
#     assert scheduler.total_teams == 5

#     teams = scheduler.teams
#     assert sorted(team.name for team in teams) == sorted(["Team 1", "Team 2", "Team 3", "Team 4", "Team 5"])

#     clear_table(session, m.Team)
#     clear_table(session, m.TeamMembership)


# def test_scheduler_from_season(base_season):
#     scheduler = Scheduler().from_season(base_season)

#     assert scheduler.season is base_season


# def test_scheduler_from_season_with_wrong_type():
#     with pytest.raises(TypeError, match="Expected a Season object"):
#         Scheduler.from_season("not_a_season")


# def test_scheduler_split_teams(session, base_season, season_service, team_service, team_member_service):
#     # Create teams for the season
#     team_a = m.Team(name="Team A")
#     team_b = m.Team(name="Team B")
#     team_c = m.Team(name="Team C")
#     team_d = m.Team(name="Team D")

#     teams = team_service.create_many([team_a, team_b, team_c, team_d], auto_commit=True)

#     scheduler = Scheduler(
#         season=base_season,
#     )

#     split_teams = scheduler.split_teams(teams)

#     assert len(split_teams) == 2
#     assert len(split_teams[0]) == 2
#     assert len(split_teams[1]) == 2

#     team_e = m.Team(name="Team E")
#     teams.append(team_service.create(team_e, auto_commit=True))

#     with pytest.raises(ValueError, match="List length must be even."):
#         scheduler.split_teams(teams)

#     clear_table(session, m.Team)


# @pytest.fixture(scope="module")
# def sunday_schedule(season, league):
#     schedule = Schedule(
#         league_id=league.id,
#         season_id=season.id,
#         name="Schedule for Test Scheduler",
#         total_games=10,
#         start_date="2025-1-05 08:00:00",
#         concurrent_games=2,
#     )

#     return schedule


# @pytest.fixture(scope="module")
# def scheduler(session, sunday_schedule) -> Scheduler:
#     scheduler = Scheduler(session=session, schedule=sunday_schedule)
#     return scheduler


# def test_generator_split_teams_even(scheduler, teams):
#     split_teams = scheduler.generator.split_teams(teams)

#     assert split_teams == (teams[:4], teams[4:])


# def test_generator_split_teams_odd(scheduler, teams):
#     temp_remove_team = teams.pop()

#     assert len(teams) == 7

#     with pytest.raises(ValueError):
#         _ = scheduler.generator.split_teams(teams)

#     teams.append(temp_remove_team)


# @pytest.mark.parametrize("matchday", [1, 2, 3])
# def test_generator_create_matchups_first_matchday(scheduler, matchday, teams):
#     matchups = scheduler.generator.create_matchups(matchday=matchday, teams=teams)
#     assert len(matchups) == 4


# def test_increment_matchday(scheduler):
#     matchday_1_start_time = scheduler.generator.increment_matchday(matchday=1)
#     matchday_2_start_time = scheduler.generator.increment_matchday(matchday=2)

#     assert matchday_1_start_time == datetime(2025, 1, 5, 8, 0)
#     assert matchday_2_start_time == datetime(2025, 1, 12, 8, 0)


# @pytest.mark.parametrize(
#     "count, concurrent, expected",
#     [(1, 2, "A"), (2, 2, "B"), (3, 4, "C"), (4, 4, "D"), (2, 1, "A"), (3, 1, "A")],
# )
# def test_determine_field(scheduler, count, concurrent, expected):
#     field = scheduler.generator.determine_field(count, concurrent)
#     assert field == expected


# def test_home_or_away_even_round(scheduler, all_teams):
#     fake_match = (all_teams[0], all_teams[1])

#     home, away = scheduler.generator.home_or_away(round_number=2, match=fake_match)
#     assert home == all_teams[0]
#     assert away == all_teams[1]


# def test_home_or_away_odd_round(scheduler, all_teams):
#     fake_match = (all_teams[0], all_teams[1])

#     home, away = scheduler.generator.home_or_away(round_number=1, match=fake_match)
#     assert home == all_teams[1]
#     assert away == all_teams[0]


# @pytest.mark.parametrize(
#     "_concurrent, _matchday, _match_count, expected",
#     [
#         (1, 1, 1, datetime(2025, 1, 5, 8, 0)),
#         (1, 1, 2, datetime(2025, 1, 5, 10, 0)),
#         (1, 1, 3, datetime(2025, 1, 5, 12, 0)),
#         (1, 1, 4, datetime(2025, 1, 5, 14, 0)),
#         (1, 1, 5, datetime(2025, 1, 5, 16, 0)),
#         (1, 2, 1, datetime(2025, 1, 12, 8, 0)),
#         (1, 2, 3, datetime(2025, 1, 12, 12, 0)),
#         (1, 2, 5, datetime(2025, 1, 12, 16, 0)),
#         (2, 1, 1, datetime(2025, 1, 5, 8, 0)),
#         (2, 1, 2, datetime(2025, 1, 5, 8, 0)),
#         (2, 1, 3, datetime(2025, 1, 5, 10, 0)),
#         (2, 1, 4, datetime(2025, 1, 5, 10, 0)),
#         (2, 1, 5, datetime(2025, 1, 5, 12, 0)),
#         (2, 1, 6, datetime(2025, 1, 5, 12, 0)),
#         (3, 2, 1, datetime(2025, 1, 12, 8, 0)),
#         (3, 3, 2, datetime(2025, 1, 19, 8, 0)),
#         (3, 4, 3, datetime(2025, 1, 26, 8, 0)),
#         (3, 5, 4, datetime(2025, 2, 2, 10, 0)),
#         (3, 6, 7, datetime(2025, 2, 9, 12, 0)),
#         (4, 1, 1, datetime(2025, 1, 5, 8, 0)),
#         (4, 1, 4, datetime(2025, 1, 5, 8, 0)),
#     ],
# )
# def test_determine_start_time_third_matchday(
#     scheduler, sunday_schedule, _concurrent, _matchday, _match_count, expected
# ):
#     sunday_schedule.concurrent_games = _concurrent
#     start_time = scheduler.generator.determine_start_time(matchday=_matchday, match_count=_match_count)
#     assert start_time == expected


# def test_create_matchday_fixtures(scheduler, teams):
#     fixtures = scheduler.generator.create_matchday_fixtures(matchday=1, round_number=1, teams=teams)
#     assert len(fixtures) == 4


# @pytest.mark.parametrize(["total_games", "expected"], [(8, 32), (10, 32), (15, 32), (16, 64), (20, 64), (24, 96)])
# def test_generate_fixtures_eight_teams(scheduler, total_games, expected, teams):
#     scheduler.generator.schedule.total_games = total_games
#     fixtures = scheduler.generator.generate_fixtures(teams=teams)
#     assert len(fixtures) == expected

#     fixtures = scheduler.generator.generate_fixtures(shuffle_order=False, teams=teams)
#     assert len(fixtures) == expected
#     fixtures.clear()


# @pytest.mark.parametrize(["total_games", "expected"], [(4, 8), (8, 16), (10, 16)])
# def test_generate_fixtures_four_teams(scheduler, total_games, expected, teams):
#     teams = teams[:4]

#     scheduler.generator.schedule.total_games = total_games
#     fixtures = scheduler.generator.generate_fixtures(teams=teams)
#     assert len(fixtures) == expected

#     fixtures = scheduler.generator.generate_fixtures(shuffle_order=False, teams=teams)
#     assert len(fixtures) == expected
#     fixtures.clear()


# def test_generate_season_fixtures_too_few_teams(scheduler, session, teams):
#     scheduler.generator.schedule.total_games = 3
#     with pytest.raises(ValueError):
#         scheduler.generate_fixtures(teams=teams)
#     scheduler.generator.schedule.total_games = 10


# def test_sort_fixtures_by_date(session, scheduler, season, league, teams):
#     _schedule = Schedule(**schedule_data, season_id=season.id, league_id=league.id)
#     scheduler = Scheduler(session=session, schedule=_schedule)

#     fixtures = scheduler.generate_fixtures(teams=teams)
#     _schedule.fixtures = fixtures

#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)

#     sorted_fixtures = scheduler.sort_fixtures(order_by_field="date", sort_order="desc")

#     assert sorted_fixtures[0].date == datetime(2025, 2, 23, 10, 0)
#     assert sorted_fixtures[-1].date == datetime(2025, 1, 5, 8, 0)


# def test_push_fixture_to_end_of_schedule(session, scheduler, league, season, teams):
#     clear_table(session, Fixture)

#     _schedule = Schedule(
#         league_id=league.id,
#         season_id=season.id,
#         name="Test Schedule",
#         total_games=10,
#         start_date="2025-1-05 08:00:00",
#     )
#     scheduler = Scheduler(session=session, schedule=_schedule)
#     _fixtures = scheduler.generator.generate_fixtures(teams=teams)
#     _schedule.fixtures = _fixtures

#     fixtures = scheduler.schedule.fixtures

#     assert len(fixtures) == 32
#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)

#     scheduler.push_fixture_to_end_of_schedule(fixtures[0])

#     assert len(fixtures) == 32
#     assert fixtures[0].date == datetime(2025, 3, 2, 8, 0)
#     assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)


# def test_push_matchday_to_end_of_schedule(session, scheduler, season, league, teams):
#     _schedule = Schedule(
#         league_id=league.id,
#         season_id=season.id,
#         name="Test Schedule",
#         total_games=10,
#         start_date="2025-1-05 08:00:00",
#     )

#     fixtures = scheduler.generator.generate_fixtures(teams=teams[:4])
#     _schedule.fixtures = fixtures
#     scheduler = Scheduler(session=session, schedule=_schedule)

#     scheduler.sort_fixtures()

#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[2].date == datetime(2025, 1, 12, 8, 0)
#     assert fixtures[3].date == datetime(2025, 1, 12, 8, 0)
#     assert fixtures[4].date == datetime(2025, 1, 19, 8, 0)
#     assert fixtures[5].date == datetime(2025, 1, 19, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 2, 23, 8, 0)

#     scheduler.push_matchday_to_end_of_schedule(2)

#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[2].date == datetime(2025, 3, 2, 8, 0)
#     assert fixtures[3].date == datetime(2025, 3, 2, 8, 0)
#     assert fixtures[4].date == datetime(2025, 1, 19, 8, 0)
#     assert fixtures[5].date == datetime(2025, 1, 19, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 2, 23, 8, 0)


# def test_push_all_fixtures_by_one_week(session, scheduler, league, season, teams):
#     _schedule = Schedule(
#         league_id=league.id,
#         season_id=season.id,
#         name="Test Schedule",
#         total_games=10,
#         start_date="2025-1-05 08:00:00",
#     )

#     fixtures = scheduler.generator.generate_fixtures(teams=teams[:4])
#     _schedule.fixtures = fixtures
#     scheduler = Scheduler(session, schedule=_schedule)

#     fixture = fixtures[4]  # Contains matchday 3 (1/19/2025)
#     scheduler.push_all_fixtures_by_one_week(fixture)
#     assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
#     assert fixtures[2].date == datetime(2025, 1, 12, 8, 0)
#     assert fixtures[3].date == datetime(2025, 1, 12, 8, 0)
#     assert fixtures[4].date == datetime(2025, 1, 26, 8, 0)
#     assert fixtures[5].date == datetime(2025, 1, 26, 8, 0)
#     assert fixtures[6].date == datetime(2025, 2, 2, 8, 0)
#     assert fixtures[7].date == datetime(2025, 2, 2, 8, 0)
#     assert fixtures[-1].date == datetime(2025, 3, 2, 8, 0)
