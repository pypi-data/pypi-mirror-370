from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class JobShopScheduling(UseCase):
    r"""
    # Job Shop Scheduling.

    Description
    -----------

    Consider a number of jobs, each of which consists of a number of operations which
    have to be processed in a specific order. Each operation has a specific machine that
    it needs to be processed on and only one operation in a job can be processed at a
    given time. Also, each machine can only execute one job at a time. The objective of
    the Job Shop Scheduling problem is to schedule all operations in a valid sequence
    while minimizing the makespan of the jobs, i.e. the completion time of the last
    running job.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Job-shop_scheduling)

    [Transformation](https://arxiv.org/pdf/1506.08479.pdf)

    Attributes
    ----------
    ### jobs: Dict[int, List[Tuple[int, int]]]
        \n A dictionary containing all jobs. Each job is a list of operations and each
        operation is tuple containing the machine and the processing time.

    ### T: int
        \n Strict upper bound when all jobs should be finished.
    """

    name: Literal["JSS"] = "JSS"
    jobs: dict[int, list[tuple[int, int]]] = Field(name="dict")  # type: ignore[call-overload]
    T: int = 0
