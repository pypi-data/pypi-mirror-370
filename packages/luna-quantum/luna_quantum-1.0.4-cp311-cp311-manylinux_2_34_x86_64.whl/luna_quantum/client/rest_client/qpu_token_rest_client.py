from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import TypeAdapter

from luna_quantum.client.interfaces.clients.qpu_token_rest_client_i import (
    IQpuTokenRestClient,
)
from luna_quantum.client.schemas import QpuTokenOut
from luna_quantum.client.schemas.create import (
    QpuTokenIn,
    QpuTokenTimeQuotaIn,
    QpuTokenTimeQuotaUpdate,
)
from luna_quantum.client.schemas.enums.qpu_token_type import QpuTokenTypeEnum
from luna_quantum.client.schemas.qpu_token.qpu_token_time_quota import (
    QpuTokenTimeQuotaOut,
)

if TYPE_CHECKING:
    from datetime import datetime

    from httpx import Response

_ORGANIZATION_QPU_TOKENS_BACKEND = "shared"
_PERSONAL_QPU_TOKENS_BACKEND = "private"


class QpuTokenRestClient(IQpuTokenRestClient):
    """Implementation of a solve job REST client."""

    @property
    def _endpoint(self) -> str:
        return "/qpu-tokens"

    def _get_endpoint_by_type(self, token_type: QpuTokenTypeEnum | None = None) -> str:
        if token_type is None:
            return f"{self._endpoint}"
        if token_type == QpuTokenTypeEnum.PERSONAL:
            return f"{self._endpoint}/{_PERSONAL_QPU_TOKENS_BACKEND}"
        return f"{self._endpoint}/{_ORGANIZATION_QPU_TOKENS_BACKEND}"

    def _get_by_name(
        self, name: str, token_type: QpuTokenTypeEnum, **kwargs: Any
    ) -> QpuTokenOut:
        response: Response = self._client.get(
            f"{self._get_endpoint_by_type(token_type)}/{name}", **kwargs
        )
        response.raise_for_status()

        qpu_token_data = response.json()
        qpu_token_data["token_type"] = token_type
        return QpuTokenOut.model_validate(qpu_token_data)

    def create(
        self,
        name: str,
        provider: str,
        token: str,
        token_type: QpuTokenTypeEnum,
        **kwargs: Any,
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
        qpu_token = QpuTokenIn(
            name=name,
            provider=provider,
            token=token,
        )

        response: Response = self._client.post(
            self._get_endpoint_by_type(token_type),
            content=qpu_token.model_dump_json(),
            **kwargs,
        )
        response.raise_for_status()
        qpu_token_data = response.json()
        qpu_token_data["token_type"] = token_type
        return QpuTokenOut.model_validate(qpu_token_data)

    def get_all(
        self,
        filter_provider: str | None = None,
        token_type: QpuTokenTypeEnum | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: Any,
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
        params = {}
        if filter_provider:
            params["filter_provider"] = filter_provider

        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        if token_type == QpuTokenTypeEnum.PERSONAL:
            params["token_type"] = _PERSONAL_QPU_TOKENS_BACKEND
        if token_type == QpuTokenTypeEnum.GROUP:
            params["token_type"] = _ORGANIZATION_QPU_TOKENS_BACKEND

        response = self._client.get(
            self._endpoint,
            params=params,
            **kwargs,
        )
        ta = TypeAdapter(list[QpuTokenOut])
        to_return: dict[QpuTokenTypeEnum, list[QpuTokenOut]] = {}
        resp = response.json()

        shared_tokens = resp.get(_ORGANIZATION_QPU_TOKENS_BACKEND, [])
        for qpu_token in shared_tokens:
            qpu_token["token_type"] = QpuTokenTypeEnum.GROUP
        to_return[QpuTokenTypeEnum.GROUP] = ta.validate_python(shared_tokens)

        personal_tokens = resp.get(_PERSONAL_QPU_TOKENS_BACKEND, [])
        for qpu_token in personal_tokens:
            qpu_token["token_type"] = QpuTokenTypeEnum.PERSONAL
        to_return[QpuTokenTypeEnum.PERSONAL] = ta.validate_python(personal_tokens)

        return to_return

    def get(
        self,
        name: str,
        token_type: QpuTokenTypeEnum = QpuTokenTypeEnum.PERSONAL,
        **kwargs: Any,
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
        qpu_token: QpuTokenOut = self._get_by_name(name, token_type, **kwargs)

        return qpu_token

    def rename(
        self,
        name: str,
        new_name: str,
        token_type: QpuTokenTypeEnum,
        **kwargs: Any,
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
        qpu_token_update_data = {"name": new_name}

        token: QpuTokenOut = self.get(name, token_type)

        response = self._client.patch(
            f"{self._get_endpoint_by_type(token_type)}/{token.name}",
            content=json.dumps(qpu_token_update_data),
            **kwargs,
        )
        response.raise_for_status()

        qpu_token_data = response.json()
        qpu_token_data["token_type"] = token_type
        return QpuTokenOut.model_validate(qpu_token_data)

    def delete(self, name: str, token_type: QpuTokenTypeEnum, **kwargs: Any) -> None:
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
        response = self._client.delete(
            f"{self._get_endpoint_by_type(token_type)}/{name}", **kwargs
        )
        response.raise_for_status()

    def create_group_time_quota(
        self,
        qpu_token_name: str,
        quota: int,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a time quota policy for a shared QPU token for the entire group.

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
        time_quota = QpuTokenTimeQuotaIn(quota=quota, start=start, end=end)

        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.post(
            f"{endpoint}/quota/group/{qpu_token_name}",
            content=time_quota.model_dump_json(),
            **kwargs,
        )
        response.raise_for_status()

    def get_group_time_quota(
        self, qpu_token_name: str, **kwargs: Any
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
        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.get(
            f"{endpoint}/quota/group/{qpu_token_name}", **kwargs
        )
        response.raise_for_status()

        time_quota_data = response.json()

        if time_quota_data is None:
            return None
        return QpuTokenTimeQuotaOut.model_validate(time_quota_data)

    def update_group_time_quota(
        self,
        qpu_token_name: str,
        quota: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: Any,
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
        data = QpuTokenTimeQuotaUpdate(quota=quota, start=start, end=end)

        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.patch(
            f"{endpoint}/quota/group/{qpu_token_name}",
            content=data.model_dump_json(),
            **kwargs,
        )
        response.raise_for_status()

    def delete_group_time_quota(self, qpu_token_name: str, **kwargs: Any) -> None:
        """Delete the group policy set on a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        """
        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.delete(
            f"{endpoint}/quota/group/{qpu_token_name}",
            **kwargs,
        )
        response.raise_for_status()

    def create_user_time_quota(
        self,
        qpu_token_name: str,
        user_email: str,
        quota: int,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a time quota policy for a shared QPU token for a single user.

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
        time_quota = QpuTokenTimeQuotaIn(quota=quota, start=start, end=end)

        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.post(
            f"{endpoint}/quota/user/{qpu_token_name}/{user_email}",
            content=time_quota.model_dump_json(),
            **kwargs,
        )
        response.raise_for_status()

    def get_user_time_quota(
        self, qpu_token_name: str, user_email: str, **kwargs: Any
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
        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.get(
            f"{endpoint}/quota/user/{qpu_token_name}/{user_email}", **kwargs
        )
        response.raise_for_status()

        time_quota_data = response.json()

        if time_quota_data is None:
            return None
        return QpuTokenTimeQuotaOut.model_validate(time_quota_data)

    def update_user_time_quota(
        self,
        qpu_token_name: str,
        user_email: str,
        quota: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        **kwargs: Any,
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
        data = {"quota": quota, "start": start, "end": end}

        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.patch(
            f"{endpoint}/quota/user/{qpu_token_name}/{user_email}",
            content=json.dumps(data),
            **kwargs,
        )
        response.raise_for_status()

    def delete_user_time_quota(
        self, qpu_token_name: str, user_email: str, **kwargs: Any
    ) -> None:
        """Delete a user-specific policy set on a qpu token.

        Parameters
        ----------
        qpu_token_name : str
            The name of the qpu token.
        """
        endpoint = self._get_endpoint_by_type(QpuTokenTypeEnum.GROUP)
        response = self._client.delete(
            f"{endpoint}/quota/user/{qpu_token_name}/{user_email}",
            **kwargs,
        )
        response.raise_for_status()
