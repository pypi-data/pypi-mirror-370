from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PrettyBase(BaseModel):
    """Helper class to implement pretty print."""

    def _pretty_print(self, data: dict, indent: int = 0) -> str:  # type: ignore[type-arg]
        """Return nested dictionaries in a readable YAML-inspired format as a string.

        This format enhances human readability by using a YAML-like structured style.

        Parameters
        ----------
        data: dict
        indent: int
        """
        output = ""
        for key, value in data.items():
            output += "    " * indent + str(key) + ":"
            if isinstance(value, dict):
                if value == {}:
                    output += " {}\n"
                else:
                    output += "\n"
                    output += self._pretty_print(value, indent + 1)
            elif isinstance(value, datetime):
                output += f" {value.strftime('%Y-%m-%d %H:%M:%S (%Z)')}\n"
            else:
                output += f" {value}\n"
        return output

    def __str__(self) -> str:
        """Override the default object string representation."""
        data = self.model_dump()

        return self._pretty_print(data)

    @property
    def head(self) -> str:
        """Print a truncated version of the pretty print console representation."""
        limit = 20

        def truncate(data: dict, limit: int) -> tuple[dict, bool]:  # type: ignore[type-arg]
            if data is None:
                return None, False

            if isinstance(data, dict):
                d = {
                    k: truncate(v, limit)[0]
                    for i, (k, v) in enumerate(data.items())
                    if i < limit
                }
                return d, len(data) > limit
            if isinstance(data, list):
                d = data[:limit]
                return d, len(data) > limit
            return data, False

        data = self.model_dump()

        data_truncated, is_truncated = truncate(data, limit)

        return self._pretty_print(data_truncated)
