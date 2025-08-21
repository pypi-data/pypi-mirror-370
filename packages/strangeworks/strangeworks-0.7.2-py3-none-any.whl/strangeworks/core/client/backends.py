"""backends.py."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from strangeworks_core.platform.gql import Operation

from strangeworks.platform.gql import SDKAPI


@dataclass
class Backend:
    """Represents a Strangeworks platform Backend."""

    id: str
    data: dict
    data_schema: str
    name: str
    remote_backend_id: str
    remote_status: str
    slug: str

    @staticmethod
    def from_dict(backend: dict) -> Backend:
        """Create backend object from dictionary."""
        id = backend.get("id", "")
        data = backend.get("data", {})
        data_schema = backend.get("dataSchema", "")
        name = backend.get("name", "")
        remote_backend_id = backend.get("remoteBackendId", "")
        remote_status = backend.get("remoteStatus", "")
        slug = backend.get("slug", {})
        return Backend(
            id=id,
            data=data,
            data_schema=data_schema,
            name=name,
            remote_backend_id=remote_backend_id,
            remote_status=remote_status,
            slug=slug,
        )


get_backend_request = Operation(
    query="""
        query backend($slug: String!) {
            backend(slug: $slug) {
                data,
                dataSchema,
                id,
                name,
                remoteBackendId,
                remoteStatus,
                slug,
            }
        }
    """
)


def get_backend(client: SDKAPI, slug: str) -> Backend:
    """Retrieve backend info for a specific backend identified by slug."""
    backend_response = client.execute(op=get_backend_request, **locals())
    return Backend.from_dict(backend_response["backend"])


get_backends_request = Operation(
    query="""
        query backends(
            $product_slugs: [String!]
            $backend_type_slugs: [String!]
            $backend_statuses: [BackendStatus!]
            $backend_tags: [String!]
        ) {
            backends(
                productSlugs: $product_slugs
                backendTypeSlugs: $backend_type_slugs
                backendStatuses: $backend_statuses
                backendTags: $backend_tags
            ) {
                id
                name
                remoteBackendId
                remoteStatus
                slug
            }
        }
    """
)


def get_backends(
    client: SDKAPI,
    product_slugs: List[str] = None,
    backend_type_slugs: List[str] = None,
    backend_statuses: List[str] = None,
    backend_tags: List[str] = None,
) -> List[Backend]:
    """Retrieve a list of available backends.

    Does not fetch data to reduce size of payload.
    """
    backends_response = client.execute(
        op=get_backends_request,
        **locals(),
    )
    res = []
    for b in backends_response["backends"]:
        res.append(Backend.from_dict(b))
    return res
