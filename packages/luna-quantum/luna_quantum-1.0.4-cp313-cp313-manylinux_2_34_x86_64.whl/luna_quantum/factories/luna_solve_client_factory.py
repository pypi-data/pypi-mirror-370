from typing import ClassVar

from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class LunaSolveClientFactory:
    """
    Factory class for managing ILunaSolve client instances.

    This class provides methods to retrieve and manage ILunaSolve client instances
    based on class configurations and input specifications.
    """

    _client_class: ClassVar[type[ILunaSolve]]

    @staticmethod
    def get_client(client: ILunaSolve | str | None) -> ILunaSolve:
        """
        Get a client based on the input or create a default one.

        This method retrieves an ILunaSolve client based on the provided input.
        If a client is not given or if the input is invalid,
        a default ILunaSolve client is instantiated and returned.

        Parameters
        ----------
        client : Optional[Union[ILunaSolve, str]]
            The input client. It can either be an instance of ILunaSolve, a string
            representation of the client, or None.

        Returns
        -------
        ILunaSolve
            An ILunaSolve client instance.
        """
        if isinstance(client, ILunaSolve):
            return client
        if isinstance(client, str):
            return LunaSolveClientFactory.get_client_class()(client)
        return LunaSolveClientFactory.get_client_class()()

    @staticmethod
    def get_client_class() -> type[ILunaSolve]:
        """
        Return the class type for the client.

        Retrieve the class type associated with the client from the client factory.

        Returns
        -------
        Type[ILunaSolve]
            The class type of the client.
        """
        return LunaSolveClientFactory._client_class

    @staticmethod
    def set_client_class(client_class: type[ILunaSolve]) -> None:
        """
        Set the client class for the ClientFactory.

        This method assigns a specific implementation class of ILunaSolve to the
        ClientFactory for creating client instances. This allows the factory to use
        the specified class when creating its objects.

        Parameters
        ----------
        client_class : Type[ILunaSolve]
            The class implementing the ILunaSolve interface to be used by the factory.

        Returns
        -------
        None

        """
        LunaSolveClientFactory._client_class = client_class
