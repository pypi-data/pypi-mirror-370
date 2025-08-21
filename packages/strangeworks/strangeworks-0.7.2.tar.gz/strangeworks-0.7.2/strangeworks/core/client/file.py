"""file.py."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple

from strangeworks_core.platform.gql import Operation
from strangeworks_core.types.file import File as FileBase

from strangeworks.core.errors.error import StrangeworksError
from strangeworks.platform.gql import SDKAPI


class File(FileBase, arbitrary_types_allowed=True):
    """Class representing files on the platform for SDK users.

    Attributes
    ----------
    content: any | None
        Content of the file. Defaults to None.
    data_schema_slug: str | None
        Optional data schema slug. Defaults to None.
    """

    content: Any = None
    data_schema_slug: str | None = None
    local_path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """Generate File object from dictionary.

        Parameters
        ----------
        data: dict
            File object represented as a dictionary.

        Returns
        -------
        : File
            File object.
        """
        return File(**data)

    @property
    def id(self) -> str:
        """Retrieve File ID.

        This is an internal identifier used by the platform and should only be used for
        debugging, etc.

        Added for backward compatibility.
        """
        return self.file_id


_upload_file_request = Operation(
    query="""
    mutation uploadWorkspaceFile(
        $workspace_slug: String!
        $file_name: String!
        $content_type: String!
        $is_public: Boolean! = false
        $json_schema: String
        $label: String
        $meta_file_create_date: Time
        $meta_file_modified_date: Time
        $meta_file_size: Int
        $meta_file_type: String
    ) {

    workspaceUploadFile(
        input: {
            workspaceSlug: $workspace_slug
            fileName: $file_name
            contentType: $content_type
            isPublic: $is_public
            jsonSchema: $json_schema
            label: $label
            metaFileCreateDate: $meta_file_create_date
            metaFileModifiedDate: $meta_file_modified_date
            metaFileSize: $meta_file_size
            metaFileType: $meta_file_type
        }
    ) {
        signedURL
        file {
            id
            slug
            label
            fileName
            url
        }
    }
}
    """,
)


def upload(
    client: SDKAPI,
    workspace_slug: str,
    path: str,
    is_public: bool = False,
    name: Optional[str] = None,
    json_schema: Optional[str] = None,
    label: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Tuple[File, str]:
    """Upload a file to the associated workspace.

    Parameters
    ----------
    client: StrangeworksGQLClient
        client to access the platform api.
    workspace_slug: str
        identifies which workspace the file is associated with.
    path: str
        fully qualified path to the file.
    is_public: bool
        if True, this file may be accessed by the URL with no authentication. In
        general, most files should NOT be public.
    name: Optional[str]
        file name. Optional as we look at the path for the file name.
    json_schema: Optional[str]
        if the file contains json, this is an identifier or link to a json schema which
        corresponds to the file contents. If
        the file contents adhere to a schema, it is highly recommended that this field
        is populated.
    label: Optional[str]
        An optional label that will be displayed to users in the portal instead of the
        file name. Used by the platform
        portal.
    content_type: Optional[str]
        The content_type of the file. Defaults to application/x-www-form-urlencoded.
        Once you `PUT` to the signed url, the content-type header must match this value.

    Return
    ------
    File
        Object with information about the file that was uploaded.
    Str
        A signed url to PUT the file.
    """
    p = Path(path)
    stats = p.stat()
    meta_size = stats.st_size
    meta_create_date = datetime.fromtimestamp(
        stats.st_ctime, tz=timezone.utc
    ).isoformat()
    meta_modified_date = datetime.fromtimestamp(
        stats.st_mtime, tz=timezone.utc
    ).isoformat()
    meta_type = p.suffix[1:]  # suffix without the .
    if meta_type == "" and name:
        # maybe the user provided file name has the correct extension
        _, ext = os.path.splitext(name)
        meta_type = ext[1:]  # again, without the .
    file_name = name or p.name
    ct = content_type or "application/x-www-form-urlencoded"
    res = client.execute(
        op=_upload_file_request,
        workspace_slug=workspace_slug,
        file_name=file_name,
        content_type=ct,
        is_public=is_public,
        json_schema=json_schema,
        label=label,
        meta_file_create_date=meta_create_date,
        meta_file_modified_date=meta_modified_date,
        meta_file_size=meta_size,
        meta_file_type=meta_type,
    ).get("workspaceUploadFile")
    if not res:
        raise StrangeworksError(message="unable to get valid response from platform")

    if "error" in res:
        raise StrangeworksError(message=res.get("error"))

    f = res.get("file")
    url = res.get("signedURL")
    if not f or not url:
        raise StrangeworksError(
            message="unable to obtain file details or a place to upload the file"
        )
    return (File.from_dict(f), url)
