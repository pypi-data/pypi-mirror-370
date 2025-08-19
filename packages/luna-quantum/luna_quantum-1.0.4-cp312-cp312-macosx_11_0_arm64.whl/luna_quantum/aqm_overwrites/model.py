from luna_quantum._core import Model, Solution
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.factories.luna_solve_client_factory import LunaSolveClientFactory
from luna_quantum.factories.usecase_factory import UseCaseFactory
from luna_quantum.solve.domain.model_metadata import ModelMetadata
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.util.class_patcher import (
    patch_instance,
    patch_property,
    patch_static,
)


@patch_property(Model)
def metadata(self: Model) -> ModelMetadata | None:
    """
    Return metadata for the current Model instance.

    If metadata is cached and corresponds to the current hash, returns the cached
    metadata. Otherwise, retrieves metadata via a client and updates the cache.

    Parameters
    ----------
    self
        Instance of Model.

    Returns
    -------
    Optional[ModelMetadata]
        Metadata for the current Model instance, or None if an error occurs or
        metadata cannot be retrieved.
    """
    _hash = self.__hash__()
    if (
        "metadata" in self._metadata  # type: ignore[attr-defined]
        and "hash" in self._metadata  # type: ignore[attr-defined]
        and self._metadata["hash"] == _hash  # type: ignore[attr-defined]
    ):
        return self._metadata["metadata"]  # type: ignore  # noqa: PGH003 # Patched Model
    client = LunaSolveClientFactory.get_client(
        None
    )  # TODO(Llewellyn): is there a way to let the user overwrite # noqa: FIX002
    #  set the client here
    try:
        _metadata = UseCaseFactory.model_load_metadata_by_hash(client=client).__call__(
            model_hash=_hash
        )
    except Exception:
        _metadata = None
    self._metadata["metadata"] = _metadata  # type: ignore  # noqa: PGH003 # Patched Model
    self._metadata["hash"] = _hash  # type: ignore  # noqa: PGH003 # Patched Model

    return _metadata


@patch_static(Model)
def load_luna(model_id: str, client: ILunaSolve | str | None = None) -> Model:
    """
    Load an AQ model using a specific model ID.

    This function retrieves an AQ model from a client obj. The client can either be
    provided directly or created dynamically if not specified.

    Parameters
    ----------
    model_id : str
        The identifier of the model that needs to be loaded.
    client : Optional[Union[ILunaSolve, str]]
        The client to use for loading the model. If not provided, a client
        will be created automatically.

    Returns
    -------
    Model
        The AQ model that was successfully loaded.
    """
    client = LunaSolveClientFactory.get_client(client=client)
    return UseCaseFactory.model_load_by_id(client=client).__call__(model_id=model_id)


@patch_instance(Model)
def save_luna(self: Model, client: ILunaSolve | str | None = None) -> None:
    """
    Save the model and update its metadata and hash.

    This function saves the current state of the model using the provided client or
    default client obtained from `ClientFactory`. It also updates the local `metadata`
    attributes of the model after saving.

    Parameters
    ----------
    self : Model
        The instance of the Model class.
    client : Optional[Union[ILunaSolve, str]], default=None
        The client to facilitate saving the model. Can be an instance of `ILunaSolve`,
        a string representing the client, or left as None to use the default client.

    Returns
    -------
    None
        This function does not return any values.

    """
    client = LunaSolveClientFactory.get_client(client=client)
    self._metadata["metadata"] = UseCaseFactory.model_save(client=client).__call__(self)  # type: ignore  # noqa: PGH003 # Patched Model
    self._metadata["hash"] = self.__hash__()  # type: ignore[attr-defined]


@patch_instance(Model)
def delete_luna(self: Model, client: ILunaSolve | str | None = None) -> None:
    """
    Delete the Luna instance of the Model.

    Ensure the Model instance is removed properly using the provided client or the
    default client.

    Parameters
    ----------
    self : Model
        The instance of the model to be deleted.
    client : Optional[Union[ILunaSolve, str]], optional
        The client used to connect to the service. If not provided, the default
        client is used.

    Returns
    -------
    None
    """
    client = LunaSolveClientFactory.get_client(client=client)
    UseCaseFactory.model_delete(client=client).__call__(self)


@patch_instance(Model)
def load_solutions(
    self: Model, client: ILunaSolve | str | None = None
) -> list[Solution]:
    """
    Load solutions for an Model.

    Fetch and return the list of all solutions for the patched Model
    using the provided client or the default client.

    Parameters
    ----------
    self : Model
        The Model for which solutions are to be loaded.
    client : Optional[Union[ILunaSolve, str]], optional
        The client used to interact and retrieve model solutions. If not provided,
        a default client will be created using the `ClientFactory`.

    Returns
    -------
    List[IAqSolution]
        A list of IAqSolution instances containing the solutions.

    """
    client = LunaSolveClientFactory.get_client(client=client)
    return UseCaseFactory.model_get_solution(client=client).__call__(self)


@patch_instance(Model)
def load_solve_jobs(
    self: Model, client: ILunaSolve | str | None = None
) -> list[SolveJob]:
    """
    Load and return a list of SolveJob objects for the Model instance.

    Parameters
    ----------
    self : Model
        The instance of the Model for which solve jobs need to be loaded.
    client : Optional[Union[ILunaSolve, str]], optional
        The client object or client type for fetching solve jobs, by default None.

    Returns
    -------
    List[SolveJob]
        A list of SolveJob objects related to the Model instance.
    """
    client = LunaSolveClientFactory.get_client(client=client)
    return UseCaseFactory.model_get_solve_job(client=client).__call__(self)


__all__ = ["Model"]
