"""workspace.py."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from strangeworks_core.platform.gql import Operation

from strangeworks.platform.gql import SDKAPI


@dataclass
class Workspace:
    """Represents a Strangeworks user workspace."""

    slug: str
    is_disabled: bool
    id: Optional[str]
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Dict[str, Any]):
        """Generate a Workspace object from dictionary."""
        return Workspace(
            slug=obj.get("slug"),
            id=obj.get("id"),
            is_disabled=obj.get("isDisabled"),
            name=obj.get("name"),
        )


_get_op = Operation(
    query="""
        query getWorkspace {
            workspace  {
                id
                slug
                isDisabled
                name
            }
        }
    """
)


def get(
    client: SDKAPI,
) -> Workspace:
    """Return Workspace object."""
    result = client.execute(op=_get_op)
    return Workspace.from_dict(result.get("workspace"))
