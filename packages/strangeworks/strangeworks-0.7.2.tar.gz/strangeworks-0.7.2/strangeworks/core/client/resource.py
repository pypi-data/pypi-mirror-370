"""resources.py."""

from typing import List, Optional

from strangeworks_core.platform.gql import Operation
from strangeworks_core.types.resource import Resource

from strangeworks.core.errors.error import StrangeworksError
from strangeworks.platform.gql import SDKAPI

_get_op = Operation(
    query="""
        query sdk_get_resources($first: Int, $after: ID) {
        workspace {
            resources(pagination: {after: $after, first: $first}) {
            pageInfo {
                endCursor
                hasNextPage
            }
            edges {
                cursor
                node {
                slug
                isDeleted
                status
                product {
                    slug
                    name
                }
                }
            }
            }
        }
        }
    """
)


def get(
    client: SDKAPI,
    resource_slug: Optional[str] = None,
    batch_size: int = 50,
) -> Optional[List[Resource]]:
    """Retrieve a list of available resources.

    Parameters
    ----------
    client: StrangeworksGQLClient
        client to access the sdk api on the platform.
    resource_slug: Optional[str]
        If supplied, only the resource whose slug matches will be returned. Defaults to
        None.
    batch_size: int
        Number of jobs to retrieve with each request. Defaults to 50.

    Return
    ------
    Optional[List[Resource]]
        List of resources or None if workspace has no resources configured.
    """
    hasNextPage: bool = True
    cursor: str = None
    resources: list[Resource] = []

    while hasNextPage:
        workspace = client.execute(
            op=_get_op,
            first=batch_size,
            after=cursor,
        ).get("workspace")

        if not workspace:
            raise StrangeworksError(
                message="unable to retrieve jobs information (no workspace returned)"
            )

        raw_list = workspace.get("resources", [])

        resources.extend(
            Resource.from_dict(x.get("node")) for x in raw_list.get("edges")
        )
        if resource_slug and resources:
            resources = [res for res in resources if res.slug == resource_slug]

        page_info = workspace.get("resources").get("pageInfo")
        cursor = page_info.get("endCursor")
        hasNextPage = page_info.get("hasNextPage")

    return resources
