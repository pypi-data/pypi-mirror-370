from typing import Protocol, runtime_checkable


@runtime_checkable
class ScheduleServiceBase(Protocol):
    """Protocol for scheduling services.

    This protocol defines the methods that a scheduling service should implement.
    """

    def generate_schedule(self) -> None:
        """Generate the schedule for the competition."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_schedule(self) -> None:
        """Get the generated schedule."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_schedule(self) -> None:
        """Update the existing schedule."""
        raise NotImplementedError("This method should be implemented by subclasses.")
