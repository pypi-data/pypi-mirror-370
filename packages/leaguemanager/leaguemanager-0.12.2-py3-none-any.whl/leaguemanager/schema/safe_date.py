from datetime import date
from enum import Enum
from typing import Self
from uuid import UUID

from attrs import define, field, validators

__all__ = ["Year", "Month", "Day", "GameTime"]


@define(frozen=True)
class Year:
    year: int

    def __attrs_post_init__(self):
        if not (1999 <= self.year <= 2099):
            raise ValueError(f"Year {self.year} is out of valid range (1999-2099).")


@define(frozen=True)
class MonthValue:
    number: int
    days: int  # Number of days in the month

    def __attrs_post_init__(self) -> None:
        if not 1 <= self.number <= 12:
            raise ValueError(f"Invalid month number: {self.number}")
        if not 1 <= self.days <= 31:
            raise ValueError(f"Invalid days in month: {self.days}")


class Weekday(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value: object) -> Self:
        if not isinstance(value, str):
            raise TypeError("Expected str")
        for day in cls:
            if day.value.lower() == value.lower():
                return day
        raise ValueError(f"No such weekday: {value}")


class Month(Enum):
    JANUARY = MonthValue(1, 31)
    FEBRUARY = MonthValue(2, 28)  # Note: February can have 29 days in leap years
    # For simplicity, assume February has 28 days here.
    # Leap year handling can be added later if needed.
    MARCH = MonthValue(3, 31)
    APRIL = MonthValue(4, 30)
    MAY = MonthValue(5, 31)
    JUNE = MonthValue(6, 30)
    JULY = MonthValue(7, 31)
    AUGUST = MonthValue(8, 31)
    SEPTEMBER = MonthValue(9, 30)
    OCTOBER = MonthValue(10, 31)
    NOVEMBER = MonthValue(11, 30)
    DECEMBER = MonthValue(12, 31)

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.value.number

    def valid_day(self, day: int) -> None:
        if not 1 <= day <= self.value.days:
            raise ValueError(f"Invalid day {day} for {self}")

    @classmethod
    def _missing_(cls, value: object) -> Self:
        if not isinstance(value, int):
            raise TypeError("Expected int")
        for m in cls:
            if m.value.number == value:
                return m
        raise ValueError(f"No such month: {value}")


@define(frozen=True)
class Day:
    value: int

    def __attrs_post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"Invalid day: {self.value}")

    @classmethod
    def of(cls, month: Month, day: int) -> Self:
        # Ensure day is within Month's range:
        month.valid_day(day)
        return cls(day)


@define
class GameTime:
    month: Month
    day: Day
    year: Year
    hour: int = field(default=0, validator=[validators.lt(25), validators.ge(0)])
    minute: int = field(default=0, validator=[validators.lt(61), validators.ge(0)])
    total_duration_in_minutes: int = field(default=0, validator=[validators.ge(0)])

    def __str__(self) -> str:
        return f"{self.hour:02}:{self.minute:02}"
