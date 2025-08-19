from collections.abc import Callable
from functools import wraps
from typing import Any, Literal, TypeVar

from luna_quantum.exceptions.patch_class_field_exists_error import (
    PatchClassFieldExistsError,
)

T = TypeVar("T")  # To represent the return type of the decorated function


def add_to_class(
    class_: type[Any],
    method_type: Literal["normal", "static", "class", "property"] = "normal",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Add a function as a method into a specified class.

    The decorator facilitates adding a function to a class as a method. The
    method can be of type 'normal' (instance method), 'static', 'class', or
    'property'. The function metadata is preserved during this process.

    Parameters
    ----------
    class_ : Type
        The class to which the function will be added.

    method_type : {"normal", "static", "class", "property"}, optional
        The type of method to integrate into the class. Defaults to "normal".
        - "normal": Adds the function as an instance-level method.
        - "static": Adds the function as a static method.
        - "class": Adds the function as a class-level method.
        - "property": Adds the function as a property.

    Returns
    -------
    Callable
        A callable decorator that, when applied to a function, integrates it
        as the specified method type into the class.

    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Preserve function metadata
        @wraps(func)
        def wrapped_func(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)

        # Add the function to the class based on the method type
        if method_type == "static":
            setattr(class_, func.__name__, staticmethod(func))  # Add as static method
        elif method_type == "class":
            setattr(class_, func.__name__, classmethod(func))  # Add as class method
        elif method_type == "property":
            setattr(class_, func.__name__, property(func))  # Add as property
        else:  # Default is normal (instance-level method)
            setattr(class_, func.__name__, func)

        return wrapped_func

    return decorator


def patch_instance(class_: type[Any]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Patch a class with a "normal" method.

    This function acts as a decorator that adds a new method to the given class.
    The newly added method behaves as a standard instance method, meaning it
    has access to the instance (`self`) when called.

    Parameters
    ----------
        class_: The class to which the method will be added.

    Returns
    -------
        A decorator function that takes the method to be added as its argument.
    """
    return add_to_class(class_, "normal")


def patch_static(class_: type[Any]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Patch a class with a "static" method.

    This function acts as a decorator that adds a new static method to the given class.
    The newly added static method does not require an instance of the class to be
    called.

    Parameters
    ----------
        class_: The class to which the static method will be added.

    Returns
    -------
        A decorator function that takes the static method to be added as its argument.
    """
    return add_to_class(class_, "static")


def patch_class(class_: type[Any]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Patch a class with a "class" method.

    This function acts as a decorator that adds a new class method to the given class.
    The newly added method will have access to the class itself (`cls`) when called.

    Parameters
    ----------
        class_: The class to which the class method will be added.

    Returns
    -------
        A decorator function that takes the class method to be added as its argument.
    """
    return add_to_class(class_, "class")


def patch_property(class_: type[Any]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Patch a class with a "property" method.

    This function acts as a decorator that adds a new property to the given class.
    The decorator converts the given method into a readable property.

    Parameters
    ----------
        class_: The class to which the property will be added.

    Returns
    -------
        A decorator function that takes the method to be added as a property.
    """
    return add_to_class(class_, "property")


def patch_field_to_class(
    class_: type[Any],
    field_name: str,
    default_value: Any = None,  # noqa: ANN401 we dont know the type in the decorator
) -> None:
    """
    Add a new field to a class.

    This function allows adding a field with a default value to the given class.
    If the field already exists in the class, a `PatchClassFieldExistsError` is raised.

    Parameters
    ----------
        class_: The class to which the field will be added.
        field_name: The name of the field to be added.
        default_value: The default value to assign to the field (optional).

    Raises
    ------
        PatchClassFieldExistsError
            If the class already has a field with the given name.
    """
    if hasattr(class_, field_name):
        raise PatchClassFieldExistsError(
            class_name=class_.__name__, field_name=field_name
        )
    setattr(class_, field_name, default_value)
