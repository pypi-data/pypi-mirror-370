from luna_quantum.exceptions.base_luna_quantum_error import BaseLunaQuantumError


class PatchClassFieldExistsError(BaseLunaQuantumError, AttributeError):
    """Raised when a field is already present in a class."""

    def __init__(self, class_name: str, field_name: str) -> None:
        super().__init__(
            f"The class {class_name} already has a field named '{field_name}'"
        )
