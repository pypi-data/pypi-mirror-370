"""jobs.py."""

from typing import List, Optional

from strangeworks_core.platform.gql import Operation
from strangeworks_core.types.job import Job as JobBase

from strangeworks.core.client.file import File
from strangeworks.core.errors.error import StrangeworksError
from strangeworks.platform.gql import SDKAPI


class Job(JobBase):
    """Class for SDK Jobs."""

    files: Optional[List[File]] = None
    child_jobs: Optional[List["Job"]] = None

    def __init__(self, **kwargs):
        """Initialize object."""
        _files = kwargs.pop("files", None)
        _child_jobs = kwargs.pop("childJobs", None) or kwargs.pop("child_jobs", None)
        super().__init__(**kwargs)
        if _files:
            self.files = [File.from_dict(job_file.get("file")) for job_file in _files]
        if _child_jobs:
            self.child_jobs = [Job(**j) for j in _child_jobs]

    def list_files(self, include_child_job_files: bool = False) -> List[File] | None:
        """Return list of files associated with job."""
        if not include_child_job_files:
            return self.files
        retval: List[File] = [f for f in self.files]
        for child in self.child_jobs:
            retval += [f for f in child.files]
        return retval


def tag(
    client: SDKAPI, workspace_slug: str, job_slug: str, tags: List[str]
) -> List[str]:
    """Add tags to a job."""
    response = client.execute(
        op=_tag_request,
        workspace_slug=workspace_slug,
        job_slug=job_slug,
        tags=tags,
    )
    tags = response.get("jobAddTags").get("tags")

    jobs = get(client, job_slug)
    return jobs[0]


_get_jobs = Operation(
    query="""
     query sdk_get_jobs(
        $job_slug: String,
        $resource_slugs: [String!],
        $product_slugs: [String!],
        $statuses: [JobStatus!]
        $tags: [String!],
        $first: Int,
        $after: ID,
    ){
        workspace {
            jobs(
                jobSlug: $job_slug,
                resourceSlugs: $resource_slugs
                productSlugs: $product_slugs
                jobStatuses: $statuses
                jobTags: $tags
                pagination: {
                    after: $after
                    first: $first
                }
            ) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                edges {
                    cursor
                    node {
                        slug
                        childJobs {
                            id
                            slug
                            status
                            resource {
                                slug
                                isDeleted
                                product {
                                    slug
                                    name
                                }
                            }
                            isTerminalState
                            remoteStatus
                            jobDataSchema
                            jobData
                            files {
                                file {
                                    slug
                                    id
                                    label
                                    fileName
                                    url
                                    metaSizeBytes
                                    dateCreated
                                    dateUpdated
                                }
                            }
                        }
                        externalIdentifier
                        status
                        resource {
                            slug
                            isDeleted
                            product {
                                slug
                                name
                            }
                        }
                        files {
                            file {
                                id
                                slug
                                fileName
                                metaSizeBytes
                                url
                            }
                        }
                        dateCreated
                        dateUpdated
                        tags {
                            tag {
                                tag
                            }
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
    job_slug: Optional[str] = None,
    resource_slugs: Optional[List[str]] = None,
    product_slugs: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    batch_size: int = 50,
) -> Optional[List[Job]]:
    """Return list of jobs associated with the current workspace.

    If no parameters (other than client) are specified, the function will return all
    jobs associated with the current workspace account.Caller can filter results
    through specifying parameters. The filters are cumulative, meaning only jobs
    matching all specified criteria will be returned.

    Parameters
    ----------
    client: StrangeworksGQLClient
        client to access the sdk api on the platform.
    job_slub: Optional[str]
        Filter to retrieve only the job whose slug matches. Defaults to None.
    resource_slugs: Optional[List[str]]
        List of resource identifiers. Only jobs with matching resource will be returned.
        Defaults to None.
    product_slugs: Optional[List[str]]
        List of product identifiers called slugs. Only jobs for matching products will
        be retuned. Defaults to None.
    statuses: Optional[List[str]]
        List of job statuses. Only jobs whose statuses match will be returned. Defaults
        to None.
    batch_size: int
        Number of jobs to retrieve with each request. Defaults to 50.
    Return
    ------
    Optional[List[Job]]
        List of Job objects that match the given criteria.
    """
    hasNextPage = True
    cursor: str = None
    jobs = []
    while hasNextPage:
        workspace = client.execute(
            op=_get_jobs,
            job_slug=job_slug,
            resource_slugs=resource_slugs,
            product_slugs=product_slugs,
            statuses=statuses,
            tags=tags,
            first=batch_size,
            after=cursor,
        ).get("workspace")

        if not workspace:
            raise StrangeworksError(
                message="unable to retrieve jobs information (no workspace returned)"
            )
        jobs_as_dict = workspace.get("jobs")
        edges = jobs_as_dict.get("edges") if jobs_as_dict else None

        if edges and len(edges) > 0:
            new_jobs = []
            for edge in edges:
                job_data = edge.get("node", {})
                # Unpack tags
                job_tags = job_data.get("tags", [])
                job_data["tags"] = [
                    tag.get("tag", {}).get("tag") for tag in job_tags if tag.get("tag")
                ]
                new_jobs.append(Job.from_dict(job_data))
            jobs.extend(new_jobs)

        cursor = workspace.get("jobs").get("pageInfo").get("endCursor")
        hasNextPage = workspace.get("jobs").get("pageInfo").get("hasNextPage")
    return jobs


_tag_request = Operation(
    query="""
        mutation jobAddTags(
            $workspace_slug: String!,
            $job_slug: String!,
            $tags: [String!]!,
            ){
            jobAddTags(
                input: {
                    workspaceSlug: $workspace_slug,
                    jobSlug: $job_slug,
                    tags: $tags
                }
            ) {
                tags {
                    tag {
                        tag
                    }
                }
            }
        }
    """
)
