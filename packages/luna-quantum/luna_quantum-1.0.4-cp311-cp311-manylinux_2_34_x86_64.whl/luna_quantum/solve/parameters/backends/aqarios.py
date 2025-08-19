from luna_quantum.solve.interfaces.backend_i import IBackend


class Aqarios(IBackend):
    """Configuration class for the Aqarios backend."""

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "aqarios"
