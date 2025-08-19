from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from luna_quantum.client.schemas import QpuToken, QpuTokenSource, TokenProvider
from luna_quantum.solve.domain.abstract.qpu_token_backend import QpuTokenBackend
from luna_quantum.solve.parameters.backends.dwave import DWave


class DWaveQpu(DWave, QpuTokenBackend):
    """
    Configuration for D-Wave quantum processing backends.

    This class provides settings for problem decomposition and embedding when using
    D-Wave quantum processors. It can be configured to use either manual embedding
    parameters or automatic embedding based on problem characteristics.

    Attributes
    ----------
    embedding_parameters: Embedding | AutoEmbedding | None
        Detailed configuration for manual embedding when not using auto-embedding.
        If None and decomposer is also None, default embedding parameters will be used.
        Ignored if decomposer is set to AutoEmbedding. Default is None.
    qpu_backend: str
        Specific D-Wave quantum processing unit (QPU) for your optimization
    """

    class Embedding(BaseModel):
        """
        Configuration parameters for embedding problems onto D-Wave QPUs.

        Embedding maps logical variables from a problem to physical qubits on the QPU,
        with chains of qubits representing individual variables.

        Attributes
        ----------
        max_no_improvement: int, default=10
            Maximum number of consecutive failed iterations to improve the current
            solution before giving up. Each iteration attempts to find an embedding for
            each variable such that it is adjacent to all its neighbors.

        random_seed: Optional[int], default=None
            Seed for the random number generator. If None, seed is set by
            `os.urandom()`.

        timeout: int, default=1000
            Maximum time in seconds before the algorithm gives up.

        max_beta: Optional[float], default=None
            Controls qubit weight assignment using formula (beta^n) where n is the
            number of chains containing that qubit. Must be greater than 1 if specified.
             If None, `max_beta` is effectively infinite.

        tries: int, default=10
            Number of restart attempts before the algorithm stops. On D-Wave 2000Q, a
            typical restart takes between 1 and 60 seconds.

        inner_rounds: Optional[int], default=None
            Maximum iterations between restart attempts. Restart attempts are typically
            terminated due to `max_no_improvement`. If None, effectively infinite.

        chainlength_patience: int, default=10
            Maximum number of consecutive failed iterations to improve chain lengths
            before moving on. Each iteration attempts to find more efficient embeddings.

        max_fill: Optional[int], default=None
            Restricts the number of chains that can simultaneously use the same qubit
            during search. Values above 63 are treated as 63. If None, effectively
            infinite.

        threads: int, default=1
            Maximum number of threads to use. Parallelization is only advantageous when
            the expected variable degree significantly exceeds the thread count. Min: 1.

        return_overlap: bool, default=False
            Controls return value format:

            - True: Returns (embedding, validity_flag) tuple
            - False: Returns only the embedding

            This function returns an embedding regardless of whether qubits are used by
            multiple variables.

        skip_initialization: bool, default=False
            If True, skips the initialization pass. Only works with semi-valid
            embeddings provided through `initial_chains` and `fixed_chains`.
            A semi-valid embedding has chains where every adjacent variable pair (u,v)
            has a coupler (p,q) in the hardware with p in chain(u) and q in chain(v).

        initial_chains: Any, default=()
            Initial chains inserted before `fixed_chains` and before initialization.
            Can be used to restart algorithm from a previous state. Missing or empty
            entries are ignored. Each value is a list of qubit labels.

        fixed_chains: Any, default=()
            Fixed chains that cannot change during the algorithm. Qubits in these chains
            are not used by other chains. Missing or empty entries are ignored.
            Each value is a list of qubit labels.

        restrict_chains: Any, default=()
            Restricts each chain[i] to be a subset of `restrict_chains[i]` throughout
            the algorithm. Missing or empty entries are ignored. Each value is a list
            of qubit labels.

        suspend_chains: Any, default=()
            A metafeature only implemented in the Python interface. For each suspended
            variable i, `suspend_chains[i]` is an iterable of iterables (blobs).
            For each blob in a suspension, at least one qubit from that blob must be
            in the chain for variable i.
        """

        max_no_improvement: int = 10
        random_seed: int | None = None
        timeout: int = 1_000
        max_beta: float | None = None
        tries: int = 10
        inner_rounds: int | None = None
        chainlength_patience: int = 10
        max_fill: int | None = None
        threads: int = Field(default=1, ge=1)
        return_overlap: bool = False
        skip_initialization: bool = False
        initial_chains: dict = Field(default_factory=dict)  # type: ignore[type-arg]
        fixed_chains: dict = Field(default_factory=dict)  # type: ignore[type-arg]
        restrict_chains: dict = Field(default_factory=dict)  # type: ignore[type-arg]
        suspend_chains: dict = Field(default_factory=dict)  # type: ignore[type-arg]

    class AutoEmbedding(BaseModel):
        """
        Configuration for automatic embedding of problems onto D-Wave hardware.

        This class provides a simpler interface to configure the embedding process
        when the details of the underlying hardware are not known or when optimal
        embedding parameters should be determined automatically.

        Attributes
        ----------
        embedding_parameters: EmbeddingParameters, default=EmbeddingParameters()
            Detailed configuration parameters for the embedding algorithm.
            See EmbeddingParameters documentation for details on specific settings.
        """

        embedding_parameters: DWaveQpu.Embedding = Field(
            default_factory=lambda: DWaveQpu.Embedding()
        )

    embedding_parameters: Embedding | AutoEmbedding | None = None
    qpu_backend: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ] = "default"

    token: str | QpuToken | None = Field(repr=False, exclude=True, default=None)

    def _get_token(self) -> TokenProvider | None:
        if self.token is None:
            return None
        if isinstance(self.token, QpuToken):
            return TokenProvider(dwave=self.token)
        return TokenProvider(
            dwave=QpuToken(
                source=QpuTokenSource.INLINE,
                token=self.token,
            )
        )
