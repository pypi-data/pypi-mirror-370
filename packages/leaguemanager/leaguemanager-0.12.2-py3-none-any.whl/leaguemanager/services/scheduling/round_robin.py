from __future__ import annotations

from collections import deque
from datetime import date, datetime, timedelta
from itertools import chain
from random import shuffle
from typing import TYPE_CHECKING, Generator, Iterable
from uuid import UUID

from attr import define, field

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.schema import Day, GameTime, Matchup, Month, Weekday, Year

if TYPE_CHECKING:
    from leaguemanager.dependency import LeagueManager

__all__ = ["RoundRobinSchedule"]


@define
class RoundRobinSchedule:
    """Service for generating and managing round-robin schedules."""

    league_manager_registry: LeagueManager | None = field(default=None)
    _season: m.Season = field(default=None)

    def generate_schedule(self, shuffle_order: bool = True, phase_identifier: str = "Matchday") -> None:
        """Generate the round-robin schedule."""
        if len(self.teams) < 2:
            raise ValueError("At least two teams are required to generate a round-robin schedule.")

        # Calculate full number of rounds, and remaining phases (if any)
        rounds, remaining = divmod(self.ruleset.number_of_phases, self.ruleset.number_of_teams - 1)

        if rounds == 0:
            raise ValueError("Not enough phases to create a round-robin schedule.")

        phases = self.get_or_create_phases(phase_identifier=phase_identifier)
        season_matchups = self.create_season_matchups(shuffle_order, phases)
        fixtures = self.save_matchups_to_db(season_matchups)

        return fixtures

    def get_schedule(self) -> None:
        """Get the generated round-robin schedule."""
        # Implementation for retrieving the round-robin schedule
        raise NotImplementedError("Retrieving round-robin schedule not implemented.")

    def update_schedule(self) -> None:
        """Update the existing round-robin schedule."""
        # Implementation for updating the round-robin schedule
        raise NotImplementedError("Updating round-robin schedule not implemented.")

    def get_or_create_phases(self, phase_identifier: str = "Matchday") -> None:
        """Creates phases if they do not exist in the database."""

        if not self.ruleset.number_of_phases:
            raise ValueError("Number of phases is not set in the ruleset.")

        if not self.season.phases:
            phases = []
            for phase_number in range(1, self.ruleset.number_of_phases + 1):
                phase = m.Phase(
                    label=f"{phase_identifier} {phase_number}",
                    season_id=self.season.id,
                )
                phase = self.phase_service.create(phase, auto_commit=True)
                phases.append(phase)
        return self.season.phases

    def save_matchups_to_db(
        self,
        matchups: Iterable[Matchup],
    ) -> list[m.Fixture]:
        """Save matchups to the database as Fixtures and TeamStats."""
        if not self.league_manager_registry:
            raise ValueError("LeagueManager registry is not set.")
        fixtures = []
        for matchup in matchups:
            fixture = m.Fixture(
                season_id=self.season.id,
                phase_id=matchup.phase_id,
                label=f"{matchup.home_team.name} vs {matchup.away_team.name}",
                site_venue=f"Venue {matchup.venue_number}",
            )
            team_stat_a = m.TeamStats(
                season_id=self.season.id,
                fixture_id=fixture.id,
                label=f"{matchup.home_team.name} Stats",
            )
            team_stat_b = m.TeamStats(
                season_id=self.season.id,
                fixture_id=fixture.id,
                label=f"{matchup.away_team.name} Stats",
            )
            matchup.home_team.team_stats_id = team_stat_a.id
            matchup.away_team.team_stats_id = team_stat_b.id
            fixture = self.fixture_service.create(fixture, auto_commit=True)
            _ = self.team_service.update(matchup.home_team, auto_commit=True)
            _ = self.team_service.update(matchup.away_team, auto_commit=True)
            fixtures.append(fixture)

        return fixtures

    @property
    def registry(self) -> LeagueManager:
        """Get the LeagueManager registry."""
        if self.league_manager_registry is None:
            raise ValueError("LeagueManager registry is not set.")
        return self.league_manager_registry

    @property
    def season_service(self) -> s.SeasonService:
        """Get the SeasonService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.SeasonService)

    @property
    def ruleset_service(self) -> s.RulesetService:
        """Get the RulesetService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.RulesetService)

    @property
    def phase_service(self) -> s.PhaseService:
        """Get the PhaseService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.PhaseService)

    @property
    def fixture_service(self) -> s.FixtureService:
        """Get the FixtureService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.FixtureService)

    @property
    def team_stats_service(self) -> s.TeamStatsService:
        """Get the TeamStatsService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.TeamStatsService)

    @property
    def team_service(self) -> s.TeamService:
        """Get the TeamService from the LeagueManager registry."""
        return self.registry.provide_db_service(service_type=s.TeamService)

    @property
    def season(self) -> m.Season:
        """Get the current season."""
        try:
            return self.season_service.get(self._season.id)
        except ValueError as e:
            raise ValueError(f"Season with ID {self._season.id} does not exist in the registry.") from e

    @property
    def ruleset(self) -> m.Ruleset:
        """Get the current ruleset."""
        if _ruleset := self.season.ruleset:
            return _ruleset
        raise ValueError(
            f"Ruleset for season {self.season.name} (ID: {self.season.id}) does not exist in the registry."
        )

    @property
    def teams(self) -> list[m.Team]:
        """Get the teams participating in the current season."""
        if _teams := self.season_service.all_teams(self.season.id):
            return _teams
        return [m.Team(name=f"Team {i + 1}") for i in range(self.ruleset.number_of_teams)]

    def create_season_matchups(self, shuffle_order: bool = True, phases: list[m.Phase] = None) -> list[Matchup]:
        """Generate matchups for the entire season."""

        if shuffle_order:
            shuffle(self.teams)

        all_matchups = []
        for phase, count in enumerate(phases, start=1):
            round_number = (count - 1) // (self.ruleset.number_of_teams - 1) + 1
            phase_matchups = self.phase_matchups(phase, count, round_number)
            all_matchups.extend(phase_matchups)

        return all_matchups

    def phase_matchups(self, phase: m.Phase, count: int, round_number: int) -> list[Matchup]:
        """Create events/matchups for a specific phase.

        See: https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method for
        details on round-robin scheduling. Splitting teams creates "bye week" team to
        ensure even matchups, and the phase number is used to rotate the teams for
        each phase of the round-robin schedule.
        """

        if len(self.teams) < 2:
            raise ValueError("At least two teams are required to create matchups.")

        home, away = self.split_teams(self.teams)

        # Create matchup by zipping home and away teams
        _matchups = list(zip(home, away, strict=False))

        # Anchor one team and rotate the rest based on phase
        if not count == 1:
            _teams = deque(chain(*_matchups))
            anchor = _teams.popleft()
            _teams.rotate(count)
            _teams.appendleft(anchor)
            home, away = self.split_teams([*_teams])
            _matchups = list(zip(home, away, strict=False))

        # Create Matchup objects for each matchup
        matchups = self.create_matchups(_matchups, phase, count, round_number)

        return matchups

    def create_matchups(
        self,
        matchups: Iterable[tuple[m.Team, m.Team]],
        phase: m.Phase,
        count: int,
        round_number: int,
    ) -> Generator[Matchup, None, None]:
        """Create Matchup objects from the list of team matchups."""
        for match_number, matchup_teams in enumerate(matchups, start=1):
            if round_number % 2 == 0:
                home, away = matchup_teams
            else:
                home, away = matchup_teams[::-1]

            yield Matchup(
                home_team=home,
                away_team=away,
                phase_id=phase.id,
                venue_number=self.generate_venue_number(match_number),
                game_time=self.generate_game_time(match_number, count, round_number),
            )

    def split_teams(self, team_obj: Iterable[m.Team]) -> tuple[list[m.Team], list[m.Team]]:
        """Split a list of teams in half, creating "bye week" team if number of teams is odd."""

        if len(team_obj) % 2 != 0:
            self.teams.append(m.Team(name="_bye"))

        return (
            team_obj[: len(team_obj) // 2],
            team_obj[len(team_obj) // 2 :],
        )

    def generate_venue_number(self, match_number: int) -> int:
        """Generates a venue number based on match_number and venue count set in the Ruleset.

        If there is only one venue, it always returns 1. If there are 3 venues and the match number is 1, it returns 1. If the match number is 2, it returns 2.
        If the match number is 3, it returns 3. If the match number is 4, it wraps around and returns 1.
        """

        venue_number = match_number % self.ruleset.venue_count
        return venue_number if venue_number != 0 else self.ruleset.venue_count

    def generate_game_time(self, match_number: int, phase: int) -> GameTime:
        """Generates a GameTime object based on when the match should be played.

        The date can be derived by incrementing the start date of the season by the product of
        the phase and number of days to increment between phases (i.e., 7 days for weekly matches).
        The match start time is determined by how many matches can be played concurrently (venue_count),
        the match number for that phase, as well as the game length and time between matches set in the Ruleset.
        """

        increment_by = self._increment_days()
        start_date = self.ruleset.start_date

        if not start_date:
            raise ValueError("Season start date is not set in the ruleset.")
        if not isinstance(start_date, (datetime, date)):
            raise TypeError("Season start date must be a datetime or date object.")

        # Note: This currently works for weekly scheduling only.
        match_date = start_date + timedelta(days=increment_by[0] * phase)
        game_time = self._increment_time(match_number, match_date)
        return game_time

    def _list_of_days(self) -> list[str]:
        """Return a list of days when fixtures can be scheduled based on the ruleset."""
        days = []
        if self.ruleset.mon_fixtures:
            days.append(Weekday.MONDAY)
        if self.ruleset.tue_fixtures:
            days.append(Weekday.TUESDAY)
        if self.ruleset.wed_fixtures:
            days.append(Weekday.WEDNESDAY)
        if self.ruleset.thu_fixtures:
            days.append(Weekday.THURSDAY)
        if self.ruleset.fri_fixtures:
            days.append(Weekday.FRIDAY)
        if self.ruleset.sat_fixtures:
            days.append(Weekday.SATURDAY)
        if self.ruleset.sun_fixtures:
            days.append(Weekday.SUNDAY)
        return days

    def _increment_days(self) -> list[int]:
        """Return a list of days to increment based on the ruleset."""

        days = self._list_of_days()
        if not days:
            raise ValueError("No days available for scheduling fixtures based on the ruleset.")
        if len(days) >= 1:
            raise NotImplementedError("Currently only supports weekly scheduling.")
        return [7]  # Default to weekly increment

    def _increment_time(self, match_count: int, match_date: datetime) -> GameTime:
        """Return the time increment between matches based on the ruleset."""

        if self.ruleset.game_length is None or self.ruleset.time_between is None:
            raise ValueError("Game length and time between matches must be set in the ruleset.")

        increment = timedelta(minutes=self.ruleset.game_length + self.ruleset.time_between)

        if match_count <= self.ruleset.venue_count:
            hour, minute = match_date.hour, match_date.minute
        else:
            # convert time delta into hours, minutes
            multiplier, _ = divmod((match_count), self.ruleset.venue_count)
            if match_count % self.ruleset.venue_count == 0:
                multiplier -= 1
            hour, minute = self._convert_to_hours_and_minutes(increment, multiplier)
            hour += match_date.hour

        return GameTime(
            month=Month(match_date.month),
            day=Day(match_date.day),
            year=Year(match_date.year),
            hour=hour,
            minute=minute,
            total_duration_in_minutes=self.ruleset.game_length + self.ruleset.time_between,
        )

    def _convert_to_hours_and_minutes(self, td: timedelta, multiplier: int) -> tuple[int, int]:
        """Convert a timedelta to (hours, minutes)."""

        _minutes = int(td.total_seconds() // 60)
        total_minutes = _minutes * multiplier
        hours, minutes = divmod(total_minutes, 60)
        return hours, minutes
