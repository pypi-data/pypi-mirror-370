import pytest

from leaguemanager import services as s
from leaguemanager.dependency.dependency_registry import LeagueManager


@pytest.fixture(scope="module")
def lm():
    """Fixture to provide a LeagueManager instance."""
    return LeagueManager()


def test_leaguemanager(lm):
    """Test that the LeagueManager instance is created correctly."""
    assert lm is not None
    assert isinstance(lm, LeagueManager)

    roundrobin = lm.provide_db_service(service_type=s.RoundRobinSchedule)

    assert roundrobin is not None
    assert isinstance(roundrobin, s.RoundRobinSchedule)
