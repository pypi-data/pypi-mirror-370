from typing import Any, Literal

CreateMode = Literal["error", "open"]
"""
Mode for creating a resource.

**Options:**

- `"error"`: raise an error if a resource with the same name already exists
- `"open"`: open the resource with the same name if it exists
"""

DropMode = Literal["error", "ignore"]
"""
Mode for deleting a resource.

**Options:**

- `"error"`: raise an error if the resource does not exist
- `"ignore"`: do nothing if the resource does not exist
"""


class _UnsetSentinel:
    """See corresponding class in orcalib.pydantic_utils"""

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "UNSET"


UNSET: Any = _UnsetSentinel()
"""
Default value to indicate that no update should be applied to a field and it should not be set to None
"""
