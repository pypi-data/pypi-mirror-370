import pytest

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.lib.toolbox import clear_table

team_data = [
    {"name": "Loro"},
    {"name": "June"},
    {"name": "Tripoli"},
    {"name": "Tres", "active": False},
]

athletes_data = [
    {"first_name": "Rob", "last_name": "Crow", "label": "Ace", "team": "Loro"},
    {"first_name": "Armistead", "last_name": "Smith IV", "label": "Bingo", "team": "Loro"},
    {"first_name": "Chris", "last_name": "Prescott", "label": "Rembrandt", "team": "Loro"},
]


@pytest.fixture(scope="module")
def org(org_service, session):
    clear_table(session, m.Organization)
    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.Ruleset)

    org = m.Organization(name="Test Organization")
    return org_service.create(org, auto_commit=True)


@pytest.fixture(scope="module")
def league(org):
    league = m.League(
        organization_id=org.id,
        name="Test League",
    )
    return league


@pytest.fixture(scope="module")
def properties(league_properties_service):
    properties = m.LeagueProperties(
        sport="Basketweaving",
        category="MEN",
        division="A",
    )

    return league_properties_service.create(properties, auto_commit=True)


@pytest.fixture(scope="module")
def ruleset(ruleset_service):
    ruleset = m.Ruleset(
        name="Test Ruleset",
        description="Ruleset for testing",
        number_of_games=5,
        sun_fixtures=True,
    )
    return ruleset_service.create(ruleset, auto_commit=True)


@pytest.fixture(scope="module")
def season():
    return m.Season(
        name="Season Test",
        description="Burndt",
        projected_start_date="2022-01-01",
    )


@pytest.fixture(scope="module")
def teams():
    return [m.Team(**data) for data in team_data]


def test_season_with_teams_active(
    session, season_service, league_service, team_member_service, team_service, org, league, season, teams
) -> None:
    print(org.id)

    # _ = league_service.create(league, auto_commit=True)

    new_season = season_service.create(season, auto_commit=True)

    for team in teams:
        _team_memb = team_member_service.create(
            {"label": f"{team.name} member", "season_id": new_season.id}, auto_commit=True
        )
        team.team_membership_id = _team_memb.id
        _ = team_service.create(team, auto_commit=True)

    teams_in_season = season_service.all_teams(new_season.id)
    assert new_season.name == "Season Test"
    assert len(new_season.team_memberships) == len(teams)
    assert len(teams_in_season) == 3

    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.TeamMembership)


def test_season_with_teams_incl_inactive(
    session, season_service, league_service, team_member_service, team_service, org, league, season, teams
) -> None:
    league.organization_id = org.id
    new_league = league_service.create(league, auto_commit=True)
    season.league_id = new_league.id
    new_season = season_service.create(season, auto_commit=True)

    for team in teams:
        _team_memb = team_member_service.create(
            {"label": f"{team.name} member", "season_id": new_season.id}, auto_commit=True
        )
        team.team_membership_id = _team_memb.id
        _ = team_service.create(team, auto_commit=True)

    teams_in_season = season_service.all_teams(new_season.id, active=False)
    assert new_season.name == "Season Test"
    assert len(new_season.team_memberships) == len(teams)
    assert len(teams_in_season) == 4

    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.TeamMembership)


def test_season_all_athletes(
    session,
    season_service,
    league_service,
    team_member_service,
    team_service,
    athlete_service,
    individual_membership_service,
    org,
    league,
    season,
    teams,
) -> None:
    league.organization_id = org.id
    new_league = league_service.create(league, auto_commit=True)
    season.league_id = new_league.id
    new_season = season_service.create(season, auto_commit=True)

    athlete_service.create_many(athletes_data, auto_commit=True)

    rob = athlete_service.get_one_or_none(label="Ace")
    armistead = athlete_service.get_one_or_none(label="Bingo")
    chris = athlete_service.get_one_or_none(label="Rembrandt")

    for team in teams:
        _team_memb = team_member_service.create(
            {"label": f"{team.name} member", "season_id": new_season.id}, auto_commit=True
        )
        team.team_membership_id = _team_memb.id
        _ = team_service.create(team, auto_commit=True)

    loro_team = team_service.get_one_or_none(name="Loro")
    tres_team = team_service.get_one_or_none(name="Tres")

    individual_membership_service.create_many(
        [
            {"athlete_id": rob.id, "team_id": loro_team.id},
            {"athlete_id": armistead.id, "team_id": loro_team.id},
            {"athlete_id": chris.id, "team_id": tres_team.id},
        ],
        auto_commit=True,
    )

    athletes = season_service.all_athletes(new_season.id)

    assert new_season.name == "Season Test"
    assert len(new_season.team_memberships) == len(teams)
    assert len(teams) == 4
    assert len(athletes) == 2

    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.TeamMembership)
    clear_table(session, m.Athlete)
    clear_table(session, m.IndividualMembership)


def test_season_all_athletes_incl_inactive_team(
    session,
    season_service,
    league_service,
    team_member_service,
    team_service,
    athlete_service,
    individual_membership_service,
    org,
    league,
    season,
    teams,
) -> None:
    """Test that all athletes are returned, including those on inactive teams."""
    league.organization_id = org.id
    new_league = league_service.create(league, auto_commit=True)
    season.league_id = new_league.id
    new_season = season_service.create(season, auto_commit=True)

    athlete_service.create_many(athletes_data, auto_commit=True)

    rob = athlete_service.get_one_or_none(label="Ace")
    armistead = athlete_service.get_one_or_none(label="Bingo")
    chris = athlete_service.get_one_or_none(label="Rembrandt")

    for team in teams:
        _team_memb = team_member_service.create(
            {"label": f"{team.name} member", "season_id": new_season.id}, auto_commit=True
        )
        team.team_membership_id = _team_memb.id
        _ = team_service.create(team, auto_commit=True)

    loro_team = team_service.get_one_or_none(name="Loro")
    tres_team = team_service.get_one_or_none(name="Tres")

    individual_membership_service.create_many(
        [
            {"athlete_id": rob.id, "team_id": loro_team.id},
            {"athlete_id": armistead.id, "team_id": loro_team.id},
            {"athlete_id": chris.id, "team_id": tres_team.id},
        ],
        auto_commit=True,
    )

    athletes = season_service.all_athletes(new_season.id, incl_inactive_team=True)

    assert new_season.name == "Season Test"
    assert len(new_season.team_memberships) == len(teams)
    assert len(teams) == 4
    assert len(athletes) == 3

    clear_table(session, m.League)
    clear_table(session, m.Season)
    clear_table(session, m.Team)
    clear_table(session, m.TeamMembership)
    clear_table(session, m.Athlete)
    clear_table(session, m.IndividualMembership)
