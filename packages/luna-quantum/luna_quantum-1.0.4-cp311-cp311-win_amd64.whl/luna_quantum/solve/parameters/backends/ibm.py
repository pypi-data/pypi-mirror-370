from typing import Literal

from pydantic import BaseModel, Field

from luna_quantum.solve.interfaces.backend_i import IBackend


class IBM(IBackend):
    """IBM quantum backend configuration.

    This class provides configuration options for IBM quantum backends, supporting
    both local simulators and fake provider backends for quantum algorithm execution.
    The configuration allows users to specify which type of backend to use without
    requiring an IBM token for simulator-based execution.

    The class supports two main backend types:

    - Simulator backends: Execute quantum algorithms locally using simulators
    - Fake provider backends: Use IBM's fake backends for testing and development

    Attributes
    ----------
    backend : SimulatorBackend | FakeProviderBackend
        The backend configuration, defaults to AER simulator.
    """

    class SimulatorBackend(BaseModel):
        """Qiskit Statevector Simulator.

        Use a simulator as backend. The QAOA is executed completely on our server, and
        no IBM token is required.

        Attributes
        ----------
        backend_name: Literal['aer', 'statevector']
            Which simulator to use. Currently, `AerSimulator` from `qiskit_aer`
            and the statevector simulator from `qiskit.primitives` are available.
        """

        backend_type: Literal["simulator"] = "simulator"
        backend_name: Literal["aer", "statevector"] = "aer"

    class FakeProviderBackend(BaseModel):
        """Simulator with emulated QPU noise model.

        The Qiskit fake provider runs a simulation with a noise model derived from
        an actual QPU hardware implementation.
        See [IBM documentation](
        https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/fake-provider) for
        available “fake” devices.

        Use a V2 fake backend from `qiskit_ibm_runtime.fake_provider`. The QAOA is
        executed entirely on our server, and no IBM token is required.

        Attributes
        ----------
        backend_name: str
            Which backend to use
        """

        backend_type: Literal["fake_provider"] = "fake_provider"
        backend_name: Literal[
            "FakeAlgiers",
            "FakeAlmadenV2",
            "FakeArmonkV2",
            "FakeAthensV2",
            "FakeAuckland",
            "FakeBelemV2",
            "FakeBoeblingenV2",
            "FakeBogotaV2",
            "FakeBrisbane",
            "FakeBrooklynV2",
            "FakeBurlingtonV2",
            "FakeCairoV2",
            "FakeCambridgeV2",
            "FakeCasablancaV2",
            "FakeCusco",
            "FakeEssexV2",
            "FakeFez",
            "FakeFractionalBackend",
            "FakeGeneva",
            "FakeGuadalupeV2",
            "FakeHanoiV2",
            "FakeJakartaV2",
            "FakeJohannesburgV2",
            "FakeKawasaki",
            "FakeKolkataV2",
            "FakeKyiv",
            "FakeKyoto",
            "FakeLagosV2",
            "FakeLimaV2",
            "FakeLondonV2",
            "FakeManhattanV2",
            "FakeManilaV2",
            "FakeMarrakesh",
            "FakeMelbourneV2",
            "FakeMontrealV2",
            "FakeMumbaiV2",
            "FakeNairobiV2",
            "FakeOsaka",
            "FakeOslo",
            "FakeOurenseV2",
            "FakeParisV2",
            "FakePeekskill",
            "FakePerth",
            "FakePrague",
            "FakePoughkeepsieV2",
            "FakeQuebec",
            "FakeQuitoV2",
            "FakeRochesterV2",
            "FakeRomeV2",
            "FakeSantiagoV2",
            "FakeSherbrooke",
            "FakeSingaporeV2",
            "FakeSydneyV2",
            "FakeTorino",
            "FakeTorontoV2",
            "FakeValenciaV2",
            "FakeVigoV2",
            "FakeWashingtonV2",
            "FakeYorktownV2",
        ]

    backend: SimulatorBackend | FakeProviderBackend = Field(
        default=SimulatorBackend(), discriminator="backend_type"
    )

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "ibm"
