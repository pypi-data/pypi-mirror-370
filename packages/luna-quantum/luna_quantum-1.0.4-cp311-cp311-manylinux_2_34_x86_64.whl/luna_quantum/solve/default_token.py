from typing import ClassVar

from luna_quantum.client.schemas import QpuToken, QpuTokenSource


class DefaultToken:
    """
    Set default tokens for various quantum computing providers.

    This class is used to set, retrieve, and remove the default QPU tokens for different
    quantum computing providers. It supports providers such as D-Wave, IBM,
    Fujitsu, Q-CTRL, and AWS. The purpose is to centralize token management
    for seamless integration with quantum computing platforms.
    """

    _dwave: ClassVar[QpuToken | None] = None
    _ibm: ClassVar[QpuToken | None] = None
    _fujitsu: ClassVar[QpuToken | None] = None
    _qctrl: ClassVar[QpuToken | None] = None
    _aws_access_key: ClassVar[QpuToken | None] = None
    _aws_secret_access_key: ClassVar[QpuToken | None] = None
    _aws_session_token: ClassVar[QpuToken | None] = None

    @classmethod
    def set_token(cls, provider: str, token: QpuToken | str) -> None:
        """
        Set the token for a specific provider.

        This method associates a token with a given provider, allowing for
        authenticated interactions with the provider's services.

        Parameters
        ----------
        provider : str
            The name or identifier of the provider.
        token : Union[QpuToken, str]
            The token object or string to authenticate with the provider.
        """
        if isinstance(token, str):
            token = QpuToken(token=token, source=QpuTokenSource.INLINE)
        cls._set_token(provider, token)

    @classmethod
    def set_dwave_token(cls, token: QpuToken | str) -> None:
        """
        Set the token for the D-Wave platform.

        Allow users to set a default token for accessing the D-Wave platform by
        specifying it as a parameter.

        Parameters
        ----------
        token : Union[QpuToken, str]
            The token to use for D-Wave access.

        Returns
        -------
        None

        """
        cls.set_token("dwave", token)

    @classmethod
    def set_ibm_token(cls, token: QpuToken | str) -> None:
        """
        Set the token for the IBM platform.

        Allow users to set a default token for accessing the IBM platform by
        specifying it as a parameter.

        Parameters
        ----------
        token : Union[QpuToken, str]
            The token to use for IBM access.

        Returns
        -------
        None

        """
        cls.set_token("ibm", token)

    @classmethod
    def set_fujitsu_token(cls, token: QpuToken | str) -> None:
        """
        Set the token for the Fujitsu platform.

        Allow users to set a default token for accessing the Fujitsu platform by
        specifying it as a parameter.

        Parameters
        ----------
        token : Union[QpuToken, str]
            The token to use for Fujitsu access.

        Returns
        -------
        None

        """
        cls.set_token("fujitsu", token)

    @classmethod
    def set_qctrl_token(cls, token: QpuToken | str) -> None:
        """
        Set the token for the QCTRL platform.

        Allow users to set a default token for accessing the QCTRL platform by
        specifying it as a parameter.

        Parameters
        ----------
        token : Union[QpuToken, str]
            The token to use for QCTRL access.

        Returns
        -------
        None

        """
        cls.set_token("qctrl", token)

    @classmethod
    def set_aws_access_token(
        cls,
        access_key: QpuToken | str,
        secret_access_key: QpuToken | str,
        aws_session_token: QpuToken | str,
    ) -> None:
        """
        Set the tokens for the AWS platform.

        Allow users to set a default token for accessing the AWS platform by
        specifying it as a parameter.

        Parameters
        ----------
        access_key : Union[QpuToken, str]
            The access key to use for AWS.
        secret_access_key : Union[QpuToken, str]
            The secret access key to use for AWS.

        Returns
        -------
        None

        """
        cls.set_token("aws_access_key", access_key)
        cls.set_token("aws_secret_access_key", secret_access_key)
        cls.set_token("aws_session_token", aws_session_token)

    @classmethod
    def remove_token(cls, provider: str) -> None:
        """
        Remove a token for a specific provider.

        This method removes the token associated with a particular provider by setting
        its value to None.

        Parameters
        ----------
        provider : str
            The identifier for the provider whose token is to be removed.

        Returns
        -------
        None
            This method does not return a value.
        """
        cls._set_token(provider, None)

    @classmethod
    def remove_dwave_token(cls) -> None:
        """
        Remove the D-Wave token from the default token provider.

        Returns
        -------
        None
            This method does not return anything.
        """
        cls.remove_token("dwave")

    @classmethod
    def remove_ibm_token(cls) -> None:
        """
        Remove the IBM token from the default token provider.

        Returns
        -------
        None
            This method does not return anything.
        """
        cls.remove_token("ibm")

    @classmethod
    def remove_fujitsu_token(cls) -> None:
        """
        Remove the Fujitsu token from the default token provider.

        Returns
        -------
        None
            This method does not return anything.
        """
        cls.remove_token("fujitsu")

    @classmethod
    def remove_qctrl_token(cls) -> None:
        """
        Remove the QCTRl token from the default token provider.

        Returns
        -------
        None
            This method does not return anything.
        """
        cls.remove_token("qctrl")

    @classmethod
    def remove_aws_token(cls) -> None:
        """
        Remove the AWS tokens from the default token provider.

        Returns
        -------
        None
            This method does not return anything.
        """
        cls.remove_token("aws_access_key")
        cls.remove_token("aws_secret_access_key")
        cls.remove_token("aws_session_token")

    @classmethod
    def get_token(cls, provider: str) -> QpuToken | None:
        """
        Get the token for a specified quantum computing provider.

        This method returns the token associated with the given provider name. If the
        provider is not recognized, it returns None.

        Parameters
        ----------
        provider : str
            The name of the quantum computing provider.

        Returns
        -------
        Union[QpuToken, None]
            The token associated with the specified provider, or None if the provider is
        """
        to_return: QpuToken | None = None
        if provider == "dwave":
            to_return = cls._dwave
        elif provider == "ibm":
            to_return = cls._ibm
        elif provider == "fujitsu":
            to_return = cls._fujitsu
        elif provider == "qctrl":
            to_return = cls._qctrl
        elif provider == "aws_access_key":
            to_return = cls._aws_access_key
        elif provider == "aws_secret_access_key":
            to_return = cls._aws_secret_access_key
        elif provider == "aws_session_token":
            to_return = cls._aws_session_token
        else:
            to_return = None
        return to_return

    @classmethod
    def _set_token(cls, provider: str, token: QpuToken | None) -> None:
        """
        Set token for the specified quantum provider.

        The method updates the corresponding class-level attribute for the given
        quantum provider with the token provided.

        Parameters
        ----------
        provider : str
            The name of the quantum provider to set the token for.
        token : Union[QpuToken, None]
            The token to associate with the given provider.

        Raises
        ------
        KeyError
            If the provider name does not match any supported providers.
        """
        if provider == "dwave":
            cls._dwave = token
        elif provider == "ibm":
            cls._ibm = token
        elif provider == "fujitsu":
            cls._fujitsu = token
        elif provider == "qctrl":
            cls._qctrl = token
        elif provider == "aws_access_key":
            cls._aws_access_key = token
        elif provider == "aws_secret_access_key":
            cls._aws_secret_access_key = token
        elif provider == "aws_session_token":
            cls._aws_session_token = token
