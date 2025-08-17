import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.db import register_sqlite
from leaguemanager.models.base import metadata

pytest_plugins = ["tests.data_fixtures"]

register_sqlite()


@pytest.fixture(scope="session")
def db_dir(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db_test")
    return db_dir


# Sync DB fixtures


@pytest.fixture(scope="session")
def engine(db_dir):
    uri = f"sqlite:///{db_dir / 'lmgr_db.db'}"
    engine = create_engine(uri, echo=False)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=True, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def session(session_factory, all_data):
    session_ = session_factory()
    yield session_
    session_.rollback()
    session_.close()


@pytest.fixture(scope="session")
def org_service(session):
    return s.OrganizationService(session=session)


@pytest.fixture(scope="session")
def league_service(session):
    return s.LeagueService(session=session)


@pytest.fixture(scope="session")
def league_properties_service(session):
    return s.LeaguePropertiesService(session=session)


@pytest.fixture(scope="session")
def season_service(session):
    return s.SeasonService(session=session)


@pytest.fixture(scope="session")
def ruleset_service(session):
    return s.RulesetService(session=session)


@pytest.fixture(scope="session")
def phase_service(session):
    return s.PhaseService(session=session)


@pytest.fixture(scope="session")
def fixture_service(session):
    return s.FixtureService(session=session)


@pytest.fixture(scope="session")
def team_service(session):
    return s.TeamService(session=session)


@pytest.fixture(scope="session")
def team_member_service(session):
    return s.TeamMembershipService(session=session)


@pytest.fixture(scope="session")
def athlete_service(session):
    return s.AthleteService(session=session)


@pytest.fixture(scope="session")
def individual_membership_service(session):
    return s.IndividualMembershipService(session=session)
