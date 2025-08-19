from typing import Any

from pydantic import BaseModel, Field

from luna_quantum.client.schemas import QpuToken, QpuTokenSource, TokenProvider
from luna_quantum.solve.domain.abstract import QpuTokenBackend


class Qctrl(QpuTokenBackend):
    """
    Configuration parameters for Q-CTRL`s Fire Opal Backend.

    QAOA (Quantum Approximate Optimization Algorithm) is a quantum algorithm designed
    for combinatorial optimization problems. This implementation leverages Q-CTRL's
    Fire Opal framework, which optimizes QAOA execution on quantum hardware to reduce
    errors and improve solution quality.

    Fire Opal's hardware-tailored optimizations enable solving larger problems with
    better convergence in fewer iterations, reducing overall execution time on real
    quantum devices.

    Attributes
    ----------
    organization_slug: str | None, default=None
        Organization identifier from your Q-CTRL account. Required only if you belong
        to multiple organizations. This can be retrieved from your Q-CTRL account
        settings or dashboard.

    backend_name: str | None, default=None
        The IBM Quantum backend to use for computations:
        - Specific backend: e.g., 'ibm_fez', 'ibm_marrakesh'
        - 'least_busy': Automatically selects the least busy available backend
        - 'basic_simulator': Uses the basic simulator (default if None)
        Check your IBM Quantum account for available backends.

    ibm_credentials: IBMQ | IBMCloud
        The IBM backend credentials, i.e. how to access the IBM service. Q-Ctrl
        currently supports two mehtods, via the old IBMQ pattern or the new IBMCloud
        pattern. Default is Qctrl.IBMQ()

    token: QpuToken | str | None, default=None
        The Q-Ctrl API token.


    Notes
    -----
    For detailed information about Fire Opal's QAOA solver and its capabilities,
    see [Q-CTRL's documentation](
    https://docs.q-ctrl.com/fire-opal/topics/fire-opals-qaoa-solver)
    """

    class IBMCloud(BaseModel):
        """
        Configuration parameters for the IBM Cloud backend.

        Attributes
        ----------
        instance: str
            The Qiskit runtime instance CRN (Cloud Resource Name).

        token: Union[str, None, QpuToken], default=None
            The IBM API token.
        """

        instance: str = ""

        token: str | QpuToken | None = Field(repr=False, exclude=True, default=None)

    organization_slug: Any = None
    backend_name: str | None = None

    ibm_credentials: IBMCloud = Field(default=IBMCloud())

    token: str | QpuToken | None = Field(repr=False, exclude=True, default=None)

    def _get_token(self) -> TokenProvider | None:
        if self.token is None or self.ibm_credentials.token is None:
            return None
        qctrl_token = (
            self.token
            if isinstance(self.token, QpuToken)
            else QpuToken(source=QpuTokenSource.INLINE, token=self.token)
        )
        ibm_token = (
            self.ibm_credentials.token
            if isinstance(self.ibm_credentials.token, QpuToken)
            else QpuToken(
                source=QpuTokenSource.INLINE, token=self.ibm_credentials.token
            )
        )
        return TokenProvider(qctrl=qctrl_token, ibm=ibm_token)

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "qctrl"
