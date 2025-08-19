from luna_quantum.solve.interfaces.backend_i import IBackend


class ZIB(IBackend):
    """Configuration class for the ZIB backend."""

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "zib"
