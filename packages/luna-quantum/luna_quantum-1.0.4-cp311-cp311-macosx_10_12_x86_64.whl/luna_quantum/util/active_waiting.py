import logging
from collections.abc import Callable
from time import sleep
from typing import ClassVar

from luna_quantum.util.log_utils import Logging


class ActiveWaiting:
    """
    Provides active waiting functionality using a customizable loop.

    The `ActiveWaiting` class offers a static method to perform a loop with
    a sleep interval that increases iteratively, allowing the user to
    regularly check a condition and optionally perform an additional action.
    """

    _logger: ClassVar[logging.Logger] = Logging.get_logger(__name__)

    @staticmethod
    def run(
        loop_check: Callable[[], bool],
        loop_call: Callable[[], None] | None = None,
        sleep_time_max: float = 60.0,
        sleep_time_increment: float = 5.0,
        sleep_time_initial: float = 5.0,
    ) -> None:
        """
        Execute a loop that checks a condition and optionally performs an action.

        This function executes a loop that repeatedly checks a condition using a
        callback function. If provided, it will also execute another callback after
        each sleep period. The sleep time increases incrementally up to a maximum
        value, starting from an initial sleep time.

        Parameters
        ----------
        loop_check : Callable[[], bool]
            A callable function that returns a boolean. The loop will continue as
            long as this callable returns True.
        loop_call : Optional[Callable[[], None]]
            An optional callable function to be executed after each sleep period.
            Defaults to None.
        sleep_time_max : float
            The maximum sleep time between condition checks. Defaults to 60.0 seconds.
        sleep_time_increment : float
            The amount of time to increment the sleep period after each iteration.
            Defaults to 5.0 seconds.
        sleep_time_initial : float
            The initial sleep time before the first condition check. Defaults to
            5.0 seconds. If invalid (< 0.0), it will be adjusted to the default.

        Raises
        ------
        ValueError
            If `sleep_time_initial`, `sleep_time_increment`, or `sleep_time_max` are
            non-positive values where a positive value is required.
        """
        cur_sleep_time: float

        if sleep_time_initial > 0.0:
            cur_sleep_time = sleep_time_initial
        else:
            cur_sleep_time = 5.0
            ActiveWaiting._logger.warning(
                f"Invalid sleep_time_initial: {sleep_time_initial},"
                f" setting it to default value {cur_sleep_time}"
            )

        while loop_check():
            ActiveWaiting._logger.info(
                f"Sleeping for {cur_sleep_time} seconds. "
                f"Waiting and checking a function in a loop."
            )
            sleep(cur_sleep_time)
            cur_sleep_time += sleep_time_increment
            cur_sleep_time = min(cur_sleep_time, sleep_time_max)
            if loop_call:
                loop_call()
