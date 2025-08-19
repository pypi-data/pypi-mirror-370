from luna_quantum.solve.interfaces.backend_i import IBackend


class DWave(IBackend):
    """Configuration class for the DWave backend."""

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "dwave"
