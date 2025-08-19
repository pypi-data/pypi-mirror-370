import platform
import sys
from logging import Logger

from rich import box
from rich.table import Table

from luna_quantum._core import __aq_model_version__, __luna_quantum_version__
from luna_quantum.util.log_utils import Logging

_logger: Logger = Logging.get_logger(__name__)
_pkg_list: list[str] = ["numpy", "pydantic"]


def debug_info() -> None:
    """Print debug information."""
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    os_info = f"{platform.system()} {platform.release()}"

    # Get additional system information
    architecture = platform.machine()
    python_implementation = platform.python_implementation()

    table = Table(
        title="Luna Debug Information",
        title_justify="left",
        caption="System and environment details for troubleshooting",
        box=box.MARKDOWN,
    )
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Version", style="green", no_wrap=True)

    # Add rows to the table
    table.add_row("Luna Quantum", f"{__luna_quantum_version__}")
    table.add_row("AqModel", f"{__aq_model_version__}")
    table.add_row("Python", f"{python_version}")
    table.add_row("Python Implementation", f"{python_implementation}")
    table.add_row("Operating System", f"{os_info}")
    table.add_row("Architecture", f"{architecture}")

    for package in _pkg_list:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "pkg found, version unknown")
            table.add_row(package, version)
        except ImportError:
            table.add_row(package, "pkg not found")

    # Print the table to console
    Logging.get_console().print(table)
