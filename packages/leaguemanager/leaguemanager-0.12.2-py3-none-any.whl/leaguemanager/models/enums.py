from enum import StrEnum


class FixtureStatus(StrEnum):
    P = "Played"
    U = "Unplayed"
    F = "Forfeit"
    A = "Abandoned"
    D = "Postponed"


class FixtureResult(StrEnum):
    W = "Win"
    D = "Draw"
    L = "Loss"
    F = "Forfeit"
    S = "Suspended"
    N = "None"


class Category(StrEnum):
    """League categories."""

    MEN = "men"
    WOMEN = "women"
    COED = "coed"


class Division(StrEnum):
    """League divisions."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"


class MatchDay(StrEnum):
    """Day of week."""

    MON = "Monday"
    TUE = "Tuesday"
    WED = "Wednesday"
    THU = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"
    SUN = "Sunday"


class Gender(StrEnum):
    """Gender."""

    M = "Male"
    F = "Female"
    NB = "Non-Binary"
    T = "Transgender"
    O = "Other"  # noqa: E741
    P = "Prefer not to say"
    N = "N/A"


class Field(StrEnum):
    """Field of play."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"  # noqa: E741
    J = "J"
    K = "K"
    L = "L"


class ScheduleType(StrEnum):
    ROUNDROBIN = "Round Robin"
    ROUNDROBIN_PLAYOFF = "Round Robin Playoff"
    TOURNAMENT = "Tournament"
    BRACKET = "Bracket"
    LADDER = "Ladder"


class GroupRole(StrEnum):
    """Valid values for Group roles."""

    ADMIN = "Admin"
    MEMBER = "Member"
    GUEST = "Guest"
