from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn
from rich.theme import Theme

from luna_quantum.config import config

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


P = ParamSpec("P")
T = TypeVar("T")


class Logging:
    """Utilities for configuring and accessing Luna SDK loggers.

    This class provides static methods to:
    - Set and retrieve the global logging level for SDK components
    - Create and configure loggers with Rich formatting
    - Manage consistent logging behavior across the SDK
    """

    @staticmethod
    def is_process_bar_shown() -> bool:
        """
        Return whether to use a process bar for progress bars.

        Returns
        -------
        bool
            Returns whether to use a process bar for progress bars.
        """
        return (
            not config.LUNA_LOG_DISABLE_SPINNER
            and Logging.get_level() != logging.NOTSET
        )

    @staticmethod
    def set_level(log_level: int) -> None:
        """Set the logging level for all SDK loggers.

        Parameters
        ----------
        log_level : int
            Logging level to set (e.g., logging.DEBUG, logging.INFO)
        """
        config.LUNA_LOG_DEFAULT_LEVEL = logging.getLevelName(log_level)

        for logger_name in logging.root.manager.loggerDict:
            if logger_name.startswith("luna_quantum"):  # Only modify SDK loggers
                logging.getLogger(logger_name).setLevel(log_level)

    @staticmethod
    def get_level() -> int:
        """Return the current logging level for the SDK.

        Returns
        -------
        int
            Current logging level as defined in the logging module
            (e.g., logging.DEBUG, logging.INFO, etc.)
        """
        return logging._nameToLevel.get(config.LUNA_LOG_DEFAULT_LEVEL, logging.INFO)  # noqa: SLF001 #No other way to map these log levels.

    @staticmethod
    def get_console() -> Console:
        """Return a Rich console instance for use in logging."""
        custom_theme = Theme(
            {
                "logging.level.debug": "bright_blue",
                "logging.level.info": "bright_green",
                "logging.level.warning": "bold bright_yellow",
                "logging.level.error": "bold bright_red",
                "logging.level.critical": "bold bright_magenta",
            }
        )
        return Console(theme=custom_theme)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name and set up a RichHandler for it.

        Parameters
        ----------
        name : str
            Name of the logger to retrieve or create

        Returns
        -------
        logging.Logger
            Configured logger instance with appropriate handlers
        """
        logger = logging.getLogger(name)
        logger.setLevel(Logging.get_level())
        logger.propagate = False

        if logger.hasHandlers():
            return logger

        handler = RichHandler(
            console=Logging.get_console(),
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=False,
            log_time_format="%Y-%m-%d %H:%M:%S",  # ISO 8601 format
        )

        logger.addHandler(handler)
        return logger


@contextmanager
def progress_bar(
    total: int | None, desc: str = "", unit: str = "steps"
) -> Generator[tuple[Progress, TaskID]]:
    """Create a progress bar using Rich as a context manager.

    Parameters
    ----------
    total: int | None
        Total number of steps in the progress bar
    desc: str
        Description text to display next to the progress bar
    unit: str
        Unit label for the progress steps, by default "steps"

    Yields
    ------
    tuple[Progress, TaskID]
        A tuple containing the Progress object and task ID for updating
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=Console(
            theme=Theme(
                {
                    "bar.back": "blue",
                    "bar.pulse": "bright_blue",
                }
            )
        ),
        transient=True,
        disable=not Logging.is_process_bar_shown(),
    ) as progress:
        task = progress.add_task(f"[blue]{desc}", total=total, unit=unit)
        yield progress, task  # Yield both progress and task for updates


def progress(
    total: int | None,
    desc: str = "",
    unit: str = "steps",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorate a func with a progress-bar.

    Parameters
    ----------
    total: int | None
        Total number of steps in the progress bar
    desc: str
        Description text to display next to the progress bar
    unit: str
        Unit label for the progress steps, by default "steps"

    """

    def decorated_func(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            with progress_bar(total=total, desc=desc, unit=unit):
                return func(*args, **kwargs)

        return decorator

    return decorated_func
