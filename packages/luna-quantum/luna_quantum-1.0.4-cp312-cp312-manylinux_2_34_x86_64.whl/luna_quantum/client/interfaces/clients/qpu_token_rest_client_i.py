from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from datetime import datetime

    from luna_quantum.client.schemas import QpuTokenOut
    from luna_quantum.client.schemas.enums.qpu_token_type import QpuTokenTypeEnum
    from luna_quantum.client.schemas.qpu_token.qpu_token_time_quota import (
        QpuTokenTimeQuotaOut,
    )


class IQpuTokenRestClient(IRestClient, ABC):
    """Inteface of a solve job REST client."""

    @abstractmethod
    def create(
        self,
        name: str,
        provider: str,
        token: str,
        token_type: QpuTokenTypeEnum,
        **kwargs: dict[str, Any],
    ) -> QpuTokenOut:
        """
        Create QPU token.

        Parameters
        ----------
        name: str
            Name of the QPU token
        provider: str
            Name of provider
        token: str
            Token
        token_type: QpuTokenTypeEnum
            There are two types of QPU tokens: PERSONAL and GROUP.
            All users of a group can use group QPU tokens.
            User QPU tokens can only be used by the user who created them.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        QpuTokenOut
            QpuToken instances.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        filter_provider: str | None = None,
        token_type: QpuTokenTypeEnum | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: dict[str, Any],
    ) -> dict[QpuTokenTypeEnum, list[QpuTokenOut]]:
        """
        Retrieve a list of QPU tokens.

        Parameters
        ----------
        filter_provider: Optional[str]
            The provider for which qpu tokens should be retrieved
        token_type: Optional[QpuTokenTypeEnum]
            If you want to retrieve only user or group QPU tokens
            otherwise all QPU tokens will be retrieved
        limit: Optional[int]
            Number of items to fetch. Default is 10.
        offset: Optional[int]
            Optional. Number of items to skip. Default is 0.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        Dict[QpuTokenTypeEnum, List[QpuTokenOut]]
            List of QpuTokenOut instances.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self, name: str, token_type: QpuTokenTypeEnum, **kwargs: dict[str, Any]
    ) -> QpuTokenOut:
        """
        Retrieve user QPU token by id.

        Parameters
        ----------
        name: str
            Name of the QPU token that should be retrieved
        token_type: QpuTokenTypeEnum
            There are two types of QPU tokens: PERSONAL and GROUP.
            All users of a group can use group QPU tokens.
            User QPU tokens can only be used by the user who created them.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        QpuTokenOut
            QpuToken instance.
        """
        raise NotImplementedError

    @abstractmethod
    def rename(
        self,
        name: str,
        new_name: str,
        token_type: QpuTokenTypeEnum,
        **kwargs: dict[str, Any],
    ) -> QpuTokenOut:
        """
        Update QPU token by id.

        Parameters
        ----------
        name: str
            Current name of the QPU token that should be updated
        new_name: str
            The new name
        token_type: QpuTokenTypeEnum
            There are two types of QPU tokens: PERSONAL and GROUP.
            All users of a group can use group QPU tokens.
            User QPU tokens can only be used by the user who created them.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        QpuTokenOut
            QpuToken instance.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self, name: str, token_type: QpuTokenTypeEnum, **kwargs: dict[str, Any]
    ) -> None:
        """
        Delete QPU token by name.

        Parameters
        ----------
        name: str
            Name of the QPU token that should be deleted
        token_type: QpuTokenTypeEnum
            There are two types of QPU tokens: PERSONAL and GROUP.
            All users of a group can use organization QPU tokens.
            User QPU tokens can only be used by the user who created them.
        **kwargs
            Parameters to pass to `httpx.request`.
        """
        raise NotImplementedError

    @abstractmethod
    def create_group_time_quota(
        self,
        qpu_token_name: str,
        quota: int,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Create a time quota policy for a shared QPU token.

        This affects every user of the group.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token. Currently, only DWave tokens are supported.
        quota : int
        quota : int
            The amount of quota to add. For DWave Quantum Annealing, which is currently
            the only algorithm that supports time quota, this is the qpu access time in
            nanoseconds.
        start : Optional[datetime], optional
            The date and time from which the policy is active. If None, the current date
            and time will be used. If the policy is currently not effective, the token
            cannot be used at all.
            Default: None
        end : Optional[datetime], optional
            The date and time until which the policy is active. If None, the policy if
            effective until 265 days after the start date. If the policy is currently
            not effective, the token cannot be used at all.
            Default: None
        """
        raise NotImplementedError

    @abstractmethod
    def get_group_time_quota(
        self, qpu_token_name: str, **kwargs: dict[str, Any]
    ) -> QpuTokenTimeQuotaOut | None:
        """Get the group time quota policy for a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.

        Returns
        -------
        Optional[QpuTokenTimeQuotaOut]
            The token policy. None, if no group policy is set on this token.
        """
        raise NotImplementedError

    @abstractmethod
    def update_group_time_quota(
        self,
        qpu_token_name: str,
        quota: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Update the details on a group qpu time quota policy.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        quota : Optional[int], optional
            The amount of quota. For DWave Quantum Annealing, which is currently the
            only supported solver, this is the qpu access time in nanoseconds. If None,
            the available quota won't be updated.
            Default: None
        start : Optional[datetime], optional
            The date and time from which the policy is active. If None, the start date
            won't be updated.
            Default: None
        end : Optional[datetime], optional
            The date and time until which the policy is active. If None, the end date
            won't be updated.
            Default: None
        """
        raise NotImplementedError

    @abstractmethod
    def delete_group_time_quota(
        self, qpu_token_name: str, **kwargs: dict[str, Any]
    ) -> None:
        """Delete the group policy set on a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        """
        raise NotImplementedError

    @abstractmethod
    def create_user_time_quota(
        self,
        qpu_token_name: str,
        user_email: str,
        quota: int,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Create a time quota policy for a shared QPU token.

        This affects a single user of the group.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token. Currently, only DWave tokens are supported.
        user_email : str
            Email of the user for whom to add the policy.
        quota : int
            The amount of quota to add. For DWave Quantum Annealing, which is currently
            the only algorithm that supports time quota, this is the qpu access time in
            nanoseconds.
        start : Optional[datetime], optional
            The date and time from which the policy is active. If None, the current date
            and time will be used. If the policy is currently not effective, the token
            cannot be used at all.
            Default: None
        end : Optional[datetime], optional
            The date and time until which the policy is active. If None, the policy if
            effective until 265 days after the start date. If the policy is currently
            not effective, the token cannot be used at all.
            Default: None
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_time_quota(
        self, qpu_token_name: str, user_email: str, **kwargs: dict[str, Any]
    ) -> QpuTokenTimeQuotaOut | None:
        """Get a user-specific time quota policy for a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        user_email : str
            Email of the user for whom to get the policy.

        Returns
        -------
        Optional[QpuTokenTimeQuotaOut]
            The token policy. None, if no policy is set on this token for the specified
            user.
        """
        raise NotImplementedError

    @abstractmethod
    def update_user_time_quota(
        self,
        qpu_token_name: str,
        user_email: str,
        quota: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Update the details on a user-specific qpu time quota policy.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        user_email : str
            Email of the user for whom to update the policy.
        quota : Optional[int], optional
            The amount of quota. For DWave Quantum Annealing, which is currently the
            only supported solver, this is the qpu access time in nanoseconds. If None,
            the available quota won't be updated.
            Default: None
        start : Optional[datetime], optional
            The date and time from which the policy is active. If None, the start date
            won't be updated.
            Default: None
        end : Optional[datetime], optional
            The date and time until which the policy is active. If None, the end date
            won't be updated.
            Default: None
        """
        raise NotImplementedError

    @abstractmethod
    def delete_user_time_quota(
        self, qpu_token_name: str, user_email: str, **kwargs: dict[str, Any]
    ) -> None:
        """Delete a user-specific policy set on a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        """
        raise NotImplementedError
