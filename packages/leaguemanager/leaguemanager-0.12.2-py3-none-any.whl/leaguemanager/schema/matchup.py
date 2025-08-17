from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from leaguemanager import models as m

if TYPE_CHECKING:
    from .safe_date import GameTime


@define
class Matchup:
    """Represents a matchup between two teams in a league.

    Attributes:
        home_team (Team): The home team in the matchup.
        away_team (Team): The away team in the matchup.
        phase_id (int): The phase id of the matchup.
        venue_number (int): The venue number for the matchup.
        game_time (GameTime): The scheduled game time for the matchup, if available.
    """

    home_team: m.Team
    away_team: m.Team
    phase_id: int = field(default=1)
    venue_number: int = field(default=1)
    game_time: GameTime | None = field(default=None)
