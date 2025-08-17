from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define, field

from leaguemanager import models as m
from leaguemanager.schema import Day, GameTime, Month, Year

if TYPE_CHECKING:
    from leaguemanager.services import FixtureService, RulesetService, SeasonService

__all__ = ["RoundRobinPlayoffSchedule"]


@define
class RoundRobinPlayoffSchedule:
    """Service for generating and managing round-robin playoff schedules."""

    season_service: SeasonService = field(default=None)
    ruleset_service: RulesetService = field(default=None)
    fixture_service: FixtureService = field(default=None)

    def generate_schedule(self) -> None:
        """Generate the round-robin playoff schedule."""
        # Implementation for generating a round-robin playoff schedule
        raise NotImplementedError("Round-robin playoff schedule generation not implemented.")

    def get_schedule(self) -> None:
        """Get the generated round-robin playoff schedule."""
        # Implementation for retrieving the round-robin playoff schedule
        raise NotImplementedError("Retrieving round-robin playoff schedule not implemented.")

    def update_schedule(self) -> None:
        """Update the existing round-robin playoff schedule."""
        # Implementation for updating the round-robin playoff schedule
        raise NotImplementedError("Updating round-robin playoff schedule not implemented.")

    @property
    def season(self) -> m.Season:
        """Get the current season."""
        if self.season_service is None:
            raise ValueError("SeasonService is not set.")
        return self.season_service.get_current_season()
