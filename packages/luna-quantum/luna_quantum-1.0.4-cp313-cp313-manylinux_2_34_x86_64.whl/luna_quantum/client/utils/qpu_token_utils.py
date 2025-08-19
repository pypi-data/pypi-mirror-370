import os

from luna_quantum.client.schemas.qpu_token.qpu_token import (
    QpuToken,
    QpuTokenSource,
    TokenProvider,
)


class QpuTokenUtils:
    """Utilities for QPU tokens."""

    @staticmethod
    def patch_qpu_tokens_from_env(
        qpu_token: TokenProvider = TokenProvider(),
    ) -> TokenProvider | None:
        """
        Add QPU tokens from environment variables.

        If a token is not found in the environment, it will be set to None.
        If no token-provider is provided, a new one will be created.

        Parameters
        ----------
        qpu_token: TokenProvider
            Token-provider to update. If no token-provider is provided,
            a new one will be created.

        Returns
        -------
        Optional[TokenProvider]
            Returns the updated token-provider. If the token-provider is empty,
            returns None.
        """
        qpu_token.dwave = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.dwave, env_key="LUNA_DWAVE_TOKEN"
        )
        qpu_token.ibm = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.ibm, env_key="LUNA_IBM_TOKEN"
        )
        qpu_token.qctrl = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.qctrl, env_key="LUNA_QCTRL_TOKEN"
        )
        qpu_token.fujitsu = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.fujitsu, env_key="LUNA_FUJITSU_TOKEN"
        )
        qpu_token.aws_access_key = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.aws_access_key, env_key="LUNA_AWS_ACCESS_KEY"
        )
        qpu_token.aws_secret_access_key = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.aws_secret_access_key, env_key="LUNA_AWS_SECRET_ACCESS_KEY"
        )
        qpu_token.aws_session_token = QpuTokenUtils.get_token_from_provider_or_env(
            token=qpu_token.aws_session_token, env_key="LUNA_AWS_SESSION_TOKEN"
        )

        if QpuTokenUtils.is_token_provider_empty(qpu_token):
            return None

        return qpu_token

    @staticmethod
    def is_qpu_token_empty(qpu_token: QpuToken) -> bool:
        """
        Check if the QpuToken object is empty.

        An empty QpuToken is defined as having both its `name` and `token`
        attributes set to `None`.

        Parameters
        ----------
        qpu_token : QpuToken
            The QpuToken object to check for emptiness.

        Returns
        -------
        bool
            True if the QpuToken is empty, otherwise False.

        """
        return qpu_token.name is None and qpu_token.token is None

    @staticmethod
    def is_token_provider_empty(qpu_token: TokenProvider) -> bool:
        """
        Check if the token provider is empty.

        The function checks whether all attributes of the provided token provider are
        None, indicating that it is empty.

        Parameters
        ----------
        qpu_token : TokenProvider
            The token provider object containing various token attributes.

        Returns
        -------
        bool
            True if all token attributes are None, otherwise False.
        """
        if qpu_token is None:
            return True
        for field in [
            qpu_token.dwave,
            qpu_token.ibm,
            qpu_token.qctrl,
            qpu_token.fujitsu,
            qpu_token.aws_access_key,
            qpu_token.aws_secret_access_key,
            qpu_token.aws_session_token,
        ]:
            if field is not None and not QpuTokenUtils.is_qpu_token_empty(field):
                return False
        return True

    @staticmethod
    def get_token_from_provider_or_env(
        token: QpuToken | None, env_key: str
    ) -> QpuToken | None:
        """
        Get token from provider or environment variable.

        If a token is provided and not empty, return it. Otherwise, attempt to retrieve
        a token from the specified environment variable. If no token is found, return
        None.

        Parameters
        ----------
        token : Optional[QpuToken]
            Token provided by the caller.
        env_key : str
            The key for the environment variable to look for a token.

        Returns
        -------
        Optional[QpuToken]
            The token retrieved either from the provided input or the environment.
        """
        if token is None or QpuTokenUtils.is_qpu_token_empty(token):
            env_value = os.environ.get(env_key, None)
            if env_value is not None:
                return QpuToken(
                    source=QpuTokenSource.INLINE,
                    token=env_value,
                )
            return None
        return token
