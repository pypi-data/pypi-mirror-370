from typing import Literal

from pydantic import BaseModel, Field


class Decomposer(BaseModel):
    """
    Configuration for breaking down larger problems into subproblems for DWave QPUs.

    Attributes
    ----------
    size: int, default=10
        Nominal number of variables in each subproblem. The actual subproblem can be
        smaller depending on other parameters (e.g., `min_gain`).

    min_gain: Optional[float], default=None
        Minimum required energy reduction threshold for including a variable in the
        subproblem. A variable is included only if flipping its value reduces the
        BQM energy by at least this amount. If None, no minimum gain is required.

    rolling: bool, default=True
        Controls variable selection strategy for successive calls on the same
        problem:

        - True: Produces subproblems on different variables by rolling down the list
          of all variables sorted by decreasing impact
        - False: Always selects variables with the highest impact

    rolling_history: float, default=1.0
        Fraction of the problem size (range 0.0 to 1.0) that participates in the
        rolling selection. Once this fraction of variables has been processed,
        subproblem unrolling is reset. Min: 0.0, Max: 1.0

    silent_rewind: bool, default=True
        Controls behavior when resetting/rewinding the subproblem generator:

        - True: Silently rewind when the reset condition is met
        - False: Raises EndOfStream exception when rewinding

    traversal: Literal["energy", "bfs", "pfs"], default="energy"
        Algorithm used to select a subproblem of `size` variables:

        - "energy": Selects the next `size` variables ordered by descending energy
          impact
        - "bfs": Uses breadth-first traversal seeded by the next variable in the
          energy impact list
        - "pfs": Uses priority-first traversal seeded by variables from the energy
          impact list, proceeding with the variable on the search boundary having
          the highest energy impact
    """

    size: int = 10
    min_gain: float | None = None
    rolling: bool = True
    rolling_history: float = Field(default=1.0, ge=0.0, le=1.0)
    silent_rewind: bool = True
    traversal: Literal["energy", "bfs", "pfs"] = "energy"
