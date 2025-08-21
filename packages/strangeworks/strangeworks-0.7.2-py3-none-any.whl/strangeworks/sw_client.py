"""client.py."""

import importlib.metadata
import os
from enum import Enum
from functools import singledispatchmethod
from typing import Any, Dict, List, Optional, Union

from strangeworks_core.types.resource import Resource

from strangeworks.core.client import auth, file, jobs, resource, workspace
from strangeworks.core.client.backends import Backend, get_backend, get_backends
from strangeworks.core.client.file import File
from strangeworks.core.client.jobs import Job
from strangeworks.core.client.rest_client import StrangeworksRestClient
from strangeworks.core.client.workspace import Workspace
from strangeworks.core.config.base import ConfigSource
from strangeworks.core.errors.error import StrangeworksError
from strangeworks.core.utils import fix_str_attr
from strangeworks.platform.gql import SDKAPI

__version__ = importlib.metadata.version("strangeworks")


class TagOperator(Enum):
    """Logical operators for tags."""

    AND = "AND"
    OR = "OR"


class SWClient:
    """Strangeworks client object."""

    def __init__(
        self,
        cfg: ConfigSource,
        headers: Optional[Dict[str, str]] = None,
        rest_client: Optional[StrangeworksRestClient] = None,
        **kwargs,
    ) -> None:
        """Strangeworks client.

        Implements the Strangeworks API and provides core functionality for cross-vendor
        applications.

        Parameters
        ----------
        cfg: ConfigSource
            Source for retrieving SDK configuration values.
        headers : Optional[Dict[str, str]]
            Headers that are sent as part of the request to Strangeworks.
        rest_client : Optional[StrangeworksRestClient]
        **kwargs
            Other keyword arguments to pass to tools like ``requests``.
        """
        self.cfg = cfg
        self.kwargs = kwargs

        self.headers = (
            os.getenv("STRANGEWORKS_HEADERS", default=None)
            if headers is None
            else headers
        )

        self.rest_client = rest_client
        self._key = cfg.get("api_key")
        self._url = cfg.get("url")

    def authenticate(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        profile: Optional[str] = None,
        store_credentials: bool = True,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        """Authenticate with Strangeworks.

        Obtains an authorization token from the platform using the api_key. The auth
        token is used to make calls to the platform. Access to platform interfaces
        are initialized.

        Parameters
        ----------
        api_key : Optional[str]
            The API key.
        url: Optional[str]
            The base URL to the Strangeworks API.
        profile: Optional[str]
            The profile name to use for configuration.
        store_credentials: bool
            Indicates whether credentials (api key an url)  should be saved. Defaults
            to True.
        overwrite: bool
            Indicates whether to overwrite credentials if they already exist. Defaults
            to False.
        **kwargs
            Additional arguments.
        """
        _key = api_key or (
            self.cfg.get("api_key", profile=profile) if profile else self._key
        )

        if _key is None:
            raise StrangeworksError.authentication_error(
                message=(
                    "Unable to retrieve api key from a previous configuration. "
                    "Please provide your api_key."
                )
            )
        _url = url or (self.cfg.get("url", profile=profile) if profile else self._url)

        _auth_token = auth.get_token(_key, _url)
        # successfully obtained an auth token.
        # first set, url
        self._key = _key
        self._url = _url
        # might as well try to use it.
        self.rest_client = StrangeworksRestClient(
            api_key=_key, host=_url, auth_token=_auth_token
        )

        # get the workspace info
        workspace: Workspace = self.workspace_info()
        self.cfg.set_active_profile(active_profile=workspace.slug)

        # if we made it this far, lets go ahead and try to save the configuration to a
        # file. But only if an api_key was provided.
        if api_key and api_key != self.cfg.get("api_key") and store_credentials:
            self.cfg.set(
                profile=workspace.slug,
                overwrite=overwrite,
                api_key=api_key,
                url=_url,
            )

    def get_sdk_api(self) -> SDKAPI:
        """Return SDK API instance."""
        if not self._key:
            raise StrangeworksError.authentication_error()
        return SDKAPI(
            api_key=self._key,
            base_url=self._url,
        )

    def resources(self, slug: Optional[str] = None) -> Optional[List[Resource]]:
        """Retrieve list of resources that are available for this workspace account.

        Parameters
        ----------
        slug: Optional[str]
            Identifier for a specific resource. Defaults to None.

        Return
        ------
        Optional[List[Resource]]
            List of resources for the current workspace account or None if no resources
            have been created.
        """
        return resource.get(client=self.get_sdk_api(), resource_slug=slug)

    def jobs(
        self,
        slug: Optional[str] = None,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tag_operator: Optional[TagOperator] = None,
    ) -> Optional[List[Job]]:
        """Retrieve list of jobs associated with the current workspace account.

        Parameters
        ----------
        slug : Optional[str] = None
            Identifier for a specific job. Defaults to None.
        resource_slugs: Optional[List[str]]
            List of resource identifiers. Only jobs whose resources match will be
            returned. Defaults to None.
        product_slugs: Optional[List[str]]
            List of product identifiers. Only jobs whose product slugs match will be
            returned. Defaults to None.
        statuses: Optional[List[str]]
            List of job statuses. Only obs whose statuses match will be returned.
            Defaults to None.
        tags: Optional[List[str]]
            List of tags to filter the jobs by. Defaults to None.
        tag_operator: Optional[TagOperator]
            The logical operator to use for the tags. Can be either "AND" or "OR".
            Defaults to None, treating the tags list as an OR operation if
            multiple tags are provided.

        Return
        -------
        : Optional[List[Job]]
            List of jobs or None if there are no jobs that match selection criteria.
        """
        tag_operator = TagOperator(tag_operator) if tag_operator else TagOperator.OR
        if tag_operator == TagOperator.OR:
            return jobs.get(
                client=self.get_sdk_api(),
                job_slug=slug,
                product_slugs=product_slugs or [],
                resource_slugs=resource_slugs or [],
                statuses=statuses or [],
                tags=tags or [],
            )
        elif tag_operator == TagOperator.AND:
            job_list = [self.jobs(tags=t) for t in tags]
            slug_list = [[j.slug for j in jobset] for jobset in job_list]

            commonalities = set(slug_list[0])
            for ii in range(1, len(slug_list)):
                commonalities &= set(slug_list[ii])

            all_jobs_flat = [job for sublist in job_list for job in sublist]
            unique_jobs = {job.slug: job for job in all_jobs_flat}.values()

            return [job for job in unique_jobs if job.slug in commonalities]
        else:
            raise ValueError("tag_operator must be either 'AND' or 'OR'")

    def add_tags(self, job_slug: str, tags: List[str]) -> List[str]:
        """Add tags to a job.

        Parameters
        ----------
        job_slug: str
            The slug of the job.
        tags: List[str]
            The tags to add to the job.

        Returns
        -------
        List[str]
            The tags linked to the job.
        """
        return jobs.tag(
            self.get_sdk_api(), self.cfg.get_active_profile(), job_slug, tags
        )

    def workspace_info(self) -> Workspace:
        """Retrieve information about the current workspace."""
        return workspace.get(self.get_sdk_api())

    def execute(
        self,
        res: Resource,
        payload: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        """Execute a job request.

        Parameters
        ----------
        res: Resource
            the resource that has the function to call.
        payload: Optiona;[Dict[str, Any]]
            the payload to send with the request.
        endpoint:
            additional endpoint to append to the proxy path for the resource.

        """
        if payload:
            return self.rest_client.post(
                url=res.proxy_url(endpoint),
                json=payload,
            )

        return self.rest_client.get(url=res.proxy_url(endpoint))

    def execute_post(
        self,
        product_slug: str,
        payload: Optional[Dict[str, Any]] = None,
        json: Optional[dict] = None,
        data: Optional[any] = None,
        endpoint: Optional[str] = None,
    ):
        """Execute a job request.

        Parameters
        ----------
        product_slug: str
            string used to identify a product entry on the platform.
        payload:
            same as json
        json:
            A JSON serializable Python object to send in the body of the Request.
        data:
            Dictionary, list of tuples, bytes, or file-like object to send in the body
            of the Request. Typically a string.
        endpoint: str | None = None
            additional path that denotes a service/product endpoint.

        Returns
        -------
            Result of the request, typically a dictionary.
        """
        resource = self.get_resource_for_product(product_slug)
        return self.rest_client.post(
            url=resource.proxy_url(path=endpoint), json=payload or json, data=data
        )

    def execute_get(self, product_slug: str, endpoint: Optional[str] = None):
        """Execute GET.

        Parameters
        ----------
        product_slug: str
            string used to identify a product entry on the platform.
        endpoint: str | None = None
            additional path that denotes a service/product endpoint.

        Returns
        -------
            Result of the request, typically a JSON serializable object like a
            dictionary.
        """
        resource = self.get_resource_for_product(product_slug)
        return self.rest_client.get(url=resource.proxy_url(endpoint))

    def get_backends(
        self,
        product_slugs: List[str] = None,
        backend_type_slugs: List[str] = None,
        backend_statuses: List[str] = None,
        backend_tags: List[str] = None,
    ) -> List[Backend]:
        """Return a list of backends available based on the filters provided.

        Replaces the deprecated BackendsService.
        """
        backends: List[Backend] = get_backends(
            client=self.get_sdk_api(),
            product_slugs=product_slugs,
            backend_type_slugs=backend_type_slugs,
            backend_statuses=backend_statuses,
            backend_tags=backend_tags,
        )

        backends = sorted(backends, key=lambda backend: backend.name)
        return backends

    def get_backend(self, backend_slug: str) -> Backend:
        """Return a single backend by the slug.

        Replaces the deprecated BackendsService.
        """
        return get_backend(self.get_sdk_api(), backend_slug)

    def upload_file(self, file_path: str) -> File:
        """Upload a file to strangeworks.

        File.url is how you can download the file.

        raises StrangeworksError if any issues arise while attempting to upload the
        file.
        """
        w = workspace.get(self.get_sdk_api())
        f, signedUrl = file.upload(self.get_sdk_api(), w.slug, file_path)
        try:
            fd = open(file_path, "rb")
        except IOError as e:
            raise StrangeworksError(f"unable to open {file_path}: {str(e)}")
        else:
            with fd:
                if self.rest_client is None:
                    raise StrangeworksError(
                        "REST client is not initialized. Ensure you have authenticated with the correct API Key.",  # noqa
                    )
                self.rest_client.put(signedUrl, data=fd)
        return f

    @singledispatchmethod
    def download_job_files(
        self,
        file_paths: Union[str, list],
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        """Download files associated with a job.

        Parameters
        ----------
        file_paths: Union[str, list]
            either the job slug (str) or a list of URLs associated with a Job object.

        Return
        ------
        A List of File objects.
        """
        raise NotImplementedError("files must either be a string or a List of strings")

    @download_job_files.register
    def _(
        self,
        file_paths: str,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        sw_job = jobs.get(
            client=self.get_sdk_api(),
            job_slug=file_paths,
            product_slugs=product_slugs,
            resource_slugs=resource_slugs,
            statuses=statuses,
        )

        file_paths = [f.url for f in sw_job[0].files]

        files_out = [self.rest_client.get(url=f) for f in file_paths]

        return files_out

    @download_job_files.register
    def _(
        self,
        file_paths: list,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        files_out = [self.rest_client.get(url=f) for f in file_paths]

        return files_out

    def set_resource_for_product(
        self,
        resource_slug: str,
        product_slug: str,
    ) -> None:
        """Set which resource to use for a given product.

        Users can have multiple resources set up for the same product. When this is the
        case, they can set which resource to use with this call.

        Parameters
        ----------
        resource: str
            Resource identifier (currently the slug).
        product_slug:
         str
            product identifier.
        """
        res = self.resources(slug=resource_slug)
        if len(res) == 0:
            raise StrangeworksError(
                message=(
                    f"Unable to retrieve resource (slug: {resource}) "
                    f"for workspace {self.cfg.get_active_profile()}"
                )
            )
        if len(res) > 1:
            raise StrangeworksError(
                message=(
                    f"More than one resource with slug: {resource}"
                    f" for workspace {self.cfg.get_active_profile()}"
                )
            )
        if res[0].product.slug != product_slug:
            raise StrangeworksError(
                message=(
                    f"Resource (slug: {res[0].slug}, product: {res[0].product.slug} is "
                    f"for a different product {product_slug}"
                )
            )
        kwargs = {product_slug: resource_slug}
        self.cfg.set(**kwargs)

    def get_resource_for_product(
        self,
        product_slug: str,
    ) -> Resource:
        """Get resource to use when using product.

        If the user has a resource allready configured and that resource still exists,
        that resource will be returned. If the user-configured resource no longer
        exists, an error will be raised.

        If user does not have a resource identified for the product and there is only
        a single resouce for the product available in the users workspace, that resource
        will be returned.

        If there are multiple resources for the given product slug and the user hasn't
        already selected one, they will be asked to do so.

        If there are no resources configured for the product slug, an error will be
        raised asking the user to create one.

        Parameters
        ----------
        product_slug: str
            product identifier.

        Return
        ------
        : Resource
            a resource object which maps to the product.

        Raises
        ------
        :StrangeworksError
            if no resource is found or there are multiple resource and none selected.
        """
        _product_slug = fix_str_attr(product_slug)
        resources = self.resources()
        resource_slug = self.cfg.get(_product_slug)
        if resource_slug:
            resource_as_list = [res for res in resources if res.slug == resource_slug]
            if len(resource_as_list) != 1:
                raise StrangeworksError(
                    f"Resource (slug: {resource_slug}) no longer exists on the system"
                )
            else:
                return resource_as_list[0]
        # we dont have a resource slug. lets see how many resources we can find in this
        # workspace with matching product slug.
        candidates = [res for res in resources if res.product.slug == _product_slug]
        if len(candidates) > 1:
            resources_list = [
                f"  strangeworks.set_resource_for_product("
                f"resource_slug='{r.slug}', product_slug='{r.product.slug}')"
                for r in candidates
            ]

            resources_string = "\n".join(resources_list)

            raise StrangeworksError(
                message=f"More than one matching resource found for "
                f"{product_slug}. Please select one:\n"
                f"{resources_string}\n"
            )
        if len(candidates) == 0:
            raise StrangeworksError(
                message=f"No matching resource found for {product_slug}. "
                "Please create one."
            )

        return candidates[0]

    def get_error_messages(
        self,
        job_slug: str,
    ) -> Dict[str, List[File]]:
        sw_job = jobs.get(
            client=self.get_sdk_api(),
            job_slug=job_slug,
        )

        if len(sw_job) == 0:
            raise StrangeworksError(f"Job with slug {job_slug} not found in workspace.")
        else:
            sw_job = sw_job[0]

        # Check parent job for error messages
        parent_files = []
        child_files = []
        for f in sw_job.files:
            if "error" in f.file_name:
                parent_files.append(self.rest_client.get(url=f.url))

        # Check child job for error messages
        if sw_job.child_jobs:
            for child_job in sw_job.child_jobs:
                if child_job.files is not None:
                    for f in child_job.files:
                        if "error" in f.file_name:
                            child_files.append(self.rest_client.get(url=f.url))

        # For svc-from-callable jobs, error message is in results file
        for f in sw_job.files:
            if "result" in f.file_name:
                result = self.rest_client.get(url=f.url)
                if isinstance(result, dict) and any(
                    "error" in r for r in result.keys()
                ):
                    parent_files.append(result)

        if sw_job.child_jobs:
            for child_job in sw_job.child_jobs:
                if child_job.files is not None:
                    for f in child_job.files:
                        if "result" in f.file_name:
                            result = self.rest_client.get(url=f.url)
                            if any("error" in r for r in result.keys()):
                                child_files.append(result)

        return {"parent_job": parent_files, "child_jobs": child_files}
