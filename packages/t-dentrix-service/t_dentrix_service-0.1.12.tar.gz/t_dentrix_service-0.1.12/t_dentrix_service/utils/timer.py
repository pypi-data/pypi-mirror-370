"""Module that contains Timer object."""

import time


class Timer:
    """Timer object."""

    def __init__(self, duration: int | float = 10) -> None:
        """Timer class initializing function."""
        self.duration = float(duration)
        self.start = time.perf_counter()

    def reset(self) -> None:
        """Resets the elapsed time."""
        self.start = time.perf_counter()

    def increment(self, increment: int = 0) -> None:
        """Increments duration.

        Args:
            increment (int): The increment value.
        """
        self.duration += increment

    @property
    def expired(self) -> bool:
        """Checks if timer is expired.

        Returns:
            bool: True if timer is expired, False otherwise.
        """
        return time.perf_counter() - self.start > self.duration

    @property
    def not_expired(self) -> bool:
        """Checks if timer is not expired.

        Returns:
            bool: True if timer is not expired, False otherwise.
        """
        return not self.expired

    @property
    def at(self) -> float:
        """Returns elapsed time.

        Returns:
            float: The elapsed time.
        """
        return time.perf_counter() - self.start
