from __future__ import annotations

import datetime
from collections import deque
from itertools import chain
from random import shuffle
from typing import Any, Generator, Iterable

from advanced_alchemy.exceptions import NotFoundError
from attrs import define, field, validators
from sqlalchemy.exc import NoResultFound
from typing_extensions import TYPE_CHECKING

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.dependency.dependency_registry import LeagueManager

if TYPE_CHECKING:
    from uuid import UUID

    from leaguemanager.models import League, Ruleset, Team, TeamStats


# @define
# class TimeOfDay:
#     hour: int = field(default=0, validator=validators.in_([i for i in range(24)]))
#     minute: int = field(default=0, validator=validators.in_([i for i in range(60)]))
#     twelve_hr_format: str | None = field(
#         converter=lambda x: f"{x.hour % 12 or 12}:{x.minute:02d} {'AM' if x.hour < 12 else 'PM'}"
#     )


@define
class TeamObj:
    team_name: str | None = field(default=None)
    team_id: UUID | None = field(default=None)
    bye_week: bool = field(default=False)


@define
class PhaseObj:
    phase_name: str | None = field(default=None)
    phase_number: int | None = field(default=None)
    phase_length: int = field(default=1)  # Length in days


@define
class EventDays:
    mon: bool = field(default=False)
    tue: bool = field(default=False)
    wed: bool = field(default=False)
    thu: bool = field(default=False)
    fri: bool = field(default=False)
    sat: bool = field(default=False)
    sun: bool = field(default=False)


@define
class EventMatchup:
    home_team: TeamObj | None = field(default=None)
    away_team: TeamObj | None = field(default=None)
    phase_number: int | None = field(default=None)
    venue: str | None = field(default=None)
    start_date: datetime.date | None = field(default=None)


@define
class Scheduler:
    type: str = field(default="ROUNDROBIN")
    number_of_teams: int = field(default=0)
    teams: list[m.Team | TeamObj] = field(default=field(factory=list))
    number_of_phases: int = field(default=1)
    venue_count: int = field(default=1)
    start_date_and_time: datetime.date | None = field(default=None)
    game_length: int = field(default=60)
    time_between_games: int = field(default=15)
    event_days: EventDays = field(default=EventDays())

    @classmethod
    def from_season(cls, season: m.Season) -> Scheduler:
        """Create a Scheduler instance from a Season object.

        This presumes that the Season has a valid Ruleset associated with it, and that
        Teams have already been associated through TeamMembership model associations.
        """
        lm = LeagueManager()
        season_service = lm.provide_db_service(s.SeasonService)

        if not season.ruleset:
            raise NotFoundError("Ruleset not found for the given season.")

        r: m.Ruleset = season.ruleset
        teams = season_service.all_teams(season.id)

        if len(teams) == 0:
            raise NotFoundError("No teams found for the given season.")
        if r.number_of_teams != len(teams):
            raise ValueError(
                f"Number of teams in the ruleset ({r.number_of_teams}) does not match the number of teams in the season ({len(teams)})."
            )

        return cls(
            type=r.schedule_type,
            number_of_teams=r.number_of_teams or 0,
            teams=teams,
            number_of_phases=r.number_of_phases or 0,
            venue_count=r.venue_count or 1,
            start_date_and_time=season.projected_start_date,
            game_length=r.game_length or 60,
            time_between_games=r.time_between or 15,
            event_days=EventDays(
                mon=r.mon_fixtures,
                tue=r.tue_fixtures,
                wed=r.wed_fixtures,
                thu=r.thu_fixtures,
                fri=r.fri_fixtures,
                sat=r.sat_fixtures,
                sun=r.sun_fixtures,
            ),
        )

    @classmethod
    def from_ruleset(cls, ruleset: m.Ruleset) -> Scheduler:
        """Create a Scheduler instance from a Ruleset object."""

        return cls(
            type=ruleset.schedule_type,
            number_of_teams=ruleset.number_of_teams or 0,
            teams=[],
            number_of_phases=ruleset.number_of_phases or 1,
            venue_count=ruleset.venue_count or 1,
            start_date_and_time=ruleset.start_date,
            game_length=ruleset.game_length or 60,
            time_between_games=ruleset.time_between or 15,
            event_days=EventDays(
                mon=ruleset.mon_fixtures,
                tue=ruleset.tue_fixtures,
                wed=ruleset.wed_fixtures,
                thu=ruleset.thu_fixtures,
                fri=ruleset.fri_fixtures,
                sat=ruleset.sat_fixtures,
                sun=ruleset.sun_fixtures,
            ),
        )

    @property
    def team_objs(self) -> list[TeamObj]:
        """Return a list of TeamObj instances for each team in the league."""
        if not self.teams:
            return [TeamObj(team_name=f"Team {i + 1}") for i in range(self.number_of_teams)]
        team_objs = []
        for team in self.teams:
            if isinstance(team, m.Team):
                team_objs.append(TeamObj(team_name=team.name, team_id=team.id))
            elif isinstance(team, TeamObj):
                team_objs.append(team)
            else:
                raise TypeError(f"Unexpected type {type(team)} in teams list.")
        return team_objs

    def create_events(self) -> list[EventMatchup]:
        """Create events based on the scheduling type."""
        if self.type == "ROUNDROBIN":
            return self.generate_round_robin_events()
        else:
            raise ValueError(f"Unsupported schedule type: {self.type}")

    def generate_round_robin_events(self, shuffle_order: bool = True) -> list[EventMatchup]:
        """Create events for a round-robin schedule."""

        if len(self.team_objs) < 2:
            raise ValueError("Not enough teams to create a round-robin schedule.")

        # Calculate full number of rounds, and remaining phases (if any)
        rounds, remaining = divmod(self.number_of_phases, self.number_of_teams - 1)

        if rounds == 0:
            raise ValueError("Not enough phases to create a round-robin schedule.")

        all_events = []
        if shuffle_order:
            shuffle(self.team_objs)

        for phase in range(self.number_of_phases - remaining):
            phase = +1
            round_number = phase // (len(self.team_objs))
            round_number += 1
            phase_events = self.phase_matchups(phase, round_number)
            all_events.extend(phase_events)

        # Handle remaining phases
        if remaining > 0:
            # create events for the remaining phases with generic teams
            # TODO: Implement logic to handle remaining phases
            pass
        return all_events

    def phase_matchups(self, phase: int, round_number: int) -> Generator[EventMatchup, None, None]:
        """Create events/matchups for a specific phase.

        See: https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method for
        details on round-robin scheduling. Splitting teams creates "bye week" team to
        ensure even matchups, and the phase number is used to rotate the teams for
        each phase of the round-robin schedule.
        """
        team_objs = self.team_objs
        if len(team_objs) < 2:
            raise ValueError("Not enough teams to create events.")

        # Split teams into two halves
        home, away = self._split_teams(team_objs)

        # Create matchup by zipping home and away teams
        matchups = list(zip(home, away, strict=False))

        # Anchor one team and rotate the rest based on phase
        if not phase == 1:
            _teams = deque(chain(*matchups))
            anchor = _teams.popleft()
            _teams.rotate(phase)
            _teams.appendleft(anchor)
            home, away = self._split_teams([*_teams])
            matchups = list(zip(home, away, strict=False))

        _event_matchups = self._create_matchups(matchups, phase, round_number)

        event_matchups = self._schedule_events(_event_matchups, phase, round_number)

        return event_matchups

    def _create_matchups(
        self, matchups: Iterable[tuple[TeamObj, TeamObj]], phase: int, round_number: int
    ) -> Generator[EventMatchup, None, None]:
        """Create EventMatchup instances from the matchups."""

        for match_number, team_pair in enumerate(matchups, start=1):
            if round_number % 2 == 0:
                home, away = team_pair
            else:
                home, away = team_pair[::-1]

            yield EventMatchup(
                home_team=home,
                away_team=away,
                phase_number=phase,
                venue=f"Venue {match_number % self.venue_count + 1}",
            )

    def _schedule_events(self, matchups: Iterable[EventMatchup], phase: int, round_number: int) -> list[EventMatchup]:
        """Schedule events based on the matchups and the start date/time."""

        if not self.start_date_and_time:
            raise ValueError("Start date and time must be set to schedule events.")

        scheduled_events = []
        current_date = self.start_date_and_time

        for matchup in matchups:
            matchup.start_date = current_date.date()
            matchup.venue = f"Venue {matchup.venue or 1}"

            # Check if concurrent games are allowed
            # Schedule games at same time based on how many concurrent games are allowed
            if self.venue_count > 1:
                matchup.start_date = current_date + datetime.timedelta(minutes=(matchup.venue or 1) * self.game_length)
            else:
                matchup.start_date = current_date

            # Increment the time for the next event
            current_date += datetime.timedelta(minutes=self.game_length + self.time_between_games)

            # Check if the event day is valid
            if not self._is_valid_event_day(current_date):
                continue

            scheduled_events.append(matchup)

        return scheduled_events

    def _is_valid_event_day(self, date: datetime.date) -> bool:
        """Check if the given date is a valid event day based on the event_days settings."""
        if self.event_days.mon and date.weekday() == 0:
            return True
        if self.event_days.tue and date.weekday() == 1:
            return True
        if self.event_days.wed and date.weekday() == 2:
            return True
        if self.event_days.thu and date.weekday() == 3:
            return True
        if self.event_days.fri and date.weekday() == 4:
            return True
        if self.event_days.sat and date.weekday() == 5:
            return True
        if self.event_days.sun and date.weekday() == 6:
            return True
        return False

    def _split_teams(self, team_obj: Iterable[TeamObj]) -> tuple[list[TeamObj], list[TeamObj]]:
        """Split a list of teams in half, creating "bye week" team if number of teams is odd."""

        if len(team_obj) % 2 != 0:
            self.teams.append(TeamObj(bye_week=True))

        return (
            team_obj[: len(team_obj) // 2],
            team_obj[len(team_obj) // 2 :],
        )
