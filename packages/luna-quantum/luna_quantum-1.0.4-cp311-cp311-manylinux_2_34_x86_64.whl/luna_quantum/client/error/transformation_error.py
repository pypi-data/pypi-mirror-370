from luna_quantum.client.error.luna_error import LunaError


class TransformationError(LunaError):
    """Luna transformation error."""

    def __str__(self) -> str:  # noqa: D105
        return (
            "An unexpected error occurred during transformation,"
            " please contact support or open an issue."
        )


class WeightedConstraintError(LunaError):
    """Error if weighted constraints provided in CQM."""

    def __str__(self) -> str:  # noqa: D105
        return "Weighted constraints for CQM are not supported"
