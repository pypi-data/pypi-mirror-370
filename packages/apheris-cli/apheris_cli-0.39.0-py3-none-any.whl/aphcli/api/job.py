import datetime
import json
import os
import tarfile
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple, Union
from uuid import UUID
from warnings import warn

import requests
from apheris_auth.config import settings
from pydantic import BaseModel, Field, ValidationError
from requests_oauthlib import OAuth2Session

from aphcli.utils import (
    cache_compute_spec_id,
    cache_job_id,
    get_job_id,
    get_oauth_session,
    load_cached_compute_spec_id,
    validate_is_logged_in,
)

from .compute import (
    ComputeSpec,
    Resources,
    activate,
    create,
    list_compute_specs,
    match,
    wait_until_running,
)
from .models import Model
from .utils.comms import (
    DEFAULT_TIMEOUT,
    exception_handled_request,
    override_request_timeout,
    request_timeout_is_set,
    unset_request_timeout,
)


class Job(BaseModel):

    duration: str
    id: UUID
    status: str
    created_at: datetime.datetime = Field(alias="createdAt")
    compute_spec_id: UUID = Field(alias="computeSpecId")

    def __str__(self):
        return (
            "Job:\n"
            f"\tduration: \t\t{self.duration}\n"
            f"\tid: \t\t\t{self.id}\n"
            f"\tstatus: \t\t{self.status}\n"
            f"\tcreated_at: \t\t{self.created_at}\n"
            f"\tcompute_spec_id: \t{self.compute_spec_id}\n"
        )


class JobsException(Exception):
    pass


def _get_job_api_url(compute_spec_id: UUID) -> str:
    subdomain = settings.API_JOBS_SUBDOMAIN

    if not subdomain:
        raise RuntimeError(
            "Could not get the Jobs subdomain from the environment. "
            "Please ensure APH_API_JOBS_SUBDOMAIN is set."
        )

    base_url = f"https://jobs-{compute_spec_id}{subdomain}"

    return f"{base_url}/api/v1/jobs"


def _command_preamble(
    compute_spec_id: Optional[UUID] = None,
) -> Tuple[UUID, Optional[OAuth2Session]]:
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)
    else:
        cache_compute_spec_id(compute_spec_id)

    session = get_oauth_session()
    return compute_spec_id, session


def list_jobs(compute_spec_id: Optional[UUID] = None) -> List[Job]:
    """
    List all jobs of a certain Compute Spec, or for the current user if no Compute Spec ID
    is provided.

    Arguments:
        compute_spec_id: The ID of the Compute Spec. If `None`, show all jobs for the
            current user.
    Returns:
        list: List of all jobs on the specified Compute Spec (or for the provided user if
            no Compute Spec ID is provided).
    """
    url = f"{settings.API_ORCHESTRATOR_BASE_URL}/jobs"
    if compute_spec_id:
        url += f"?computespecID={compute_spec_id}"

    response = exception_handled_request(get_oauth_session(), url, "get")

    payload = response.json()
    try:
        return [Job(**item) for item in payload]
    except ValidationError as exc:
        raise JobsException(
            f"Could not interpret the server response. Errors: {exc.errors()}"
        )
    except TypeError as exc:
        raise JobsException(f"Could not interpret the server response. Error: {exc}")


def get(job_id: Union[str, UUID, None] = None, verbose: bool = True) -> Job:
    """
    Get details on a job

    Arguments:
        job_id: The ID of the job whose details shall be fetched
        verbose: If `True`, provide more detailed information.
    Returns:
        dict: A dictionary with information on the job
    """
    job_id = get_job_id(job_id, verbose=verbose)

    response = exception_handled_request(
        get_oauth_session(),
        f"{settings.API_ORCHESTRATOR_BASE_URL}/jobs/{job_id}",
        "get",
    )

    payload = response.json()
    try:
        return Job(**payload)
    except (ValidationError, TypeError):
        raise JobsException("Could not interpret the server response.")


def status(job_id: Optional[UUID] = None, verbose: bool = True) -> str:
    """
    Get the status of a job

    Arguments:
        job_id: The ID of the job whose status shall be fetched
        verbose: If `True`, provide more detailed information.
    Returns:
        str: A string with details on the job's status
    """
    return get(job_id, verbose=verbose).status


def run(
    datasets: List[str],
    payload: dict,
    model: str,
    version: str,
    resources: Resources = Resources(),
    num_clients_per_gateway: Optional[int] = None,
) -> Job:
    """
    Runs a job on given datasets, resources can be optionally specified

    Args:
        datasets: List of dataset IDs.
        payload: Dictionary containing the job arguments.
        model: Model ID.
        version: Model version.
        resources: Resources required for the job.

    Returns:
        Job: The submitted job.
    """
    computespec = ComputeSpec(
        datasets,
        resources.client_n_cpu,
        resources.client_n_gpu,
        resources.client_memory,
        resources.server_n_cpu,
        resources.server_n_gpu,
        resources.server_memory,
        Model(id=model, version=version),
        num_clients_per_gateway=num_clients_per_gateway,
    )

    # Exising compute specs can have resource limits that are outside the recommended
    # range. Validating them would result in an exception.
    computespecs = [
        (ComputeSpec.from_dict(cs, skip_validation=True), cs["status"]["detail"])
        for cs in list_compute_specs(limit=None)
        if cs["status"]["detail"] not in ["deleting", "invalid", "failed"]
    ]

    matching_computespecs = [
        (cs, status) for cs, status in computespecs if match(cs, computespec)
    ]
    running_computespecs = [
        (cs, status) for cs, status in matching_computespecs if status == "running"
    ]

    cs_id = get_or_create_compute_spec(
        running_computespecs, matching_computespecs, computespec
    )

    # Even if there's an existing compute spec, it might be in "creating" state so we need
    # to wait until it's running. If it's already running, this will be a no-op.
    wait_until_running(cs_id)

    # It can happen that the server is not ready to receive jobs (503 or other) this is a guard against it
    time.sleep(2)

    job_id = submit(payload, cs_id)

    return Job(
        id=job_id,
        computeSpecId=cs_id,
        status="submitted",
        duration="0:00:00",
        createdAt=datetime.datetime.now(),
    )


def get_or_create_compute_spec(
    running_computespecs: List[Tuple[ComputeSpec, str]],
    matching_computespecs: List[Tuple[ComputeSpec, str]],
    computespec: ComputeSpec,
) -> UUID:

    cs_id: UUID

    if len(running_computespecs) >= 1:
        if len(running_computespecs) > 1:
            warn(
                "Multiple running Compute Specs found for the same user/datasets/model/resources"
            )
        cs, _ = running_computespecs[0]
        cs_id = cs._id
        return cs_id

    if len(matching_computespecs) >= 1:
        if len(matching_computespecs) > 1:
            warn(
                "Multiple matching Compute Specs found for the same user/datasets/model/resources"
            )
        cs, _ = matching_computespecs[0]
        cs_id = cs._id
        return cs_id

    cs_id = create(computespec)
    activate(cs_id)
    return cs_id


def submit(
    job_args: dict, compute_spec_id: Optional[UUID] = None, verbose: bool = False
) -> UUID:
    """
    Submit a job

    Arguments:
        job_args: Arguments for the job that you want to submit.
        compute_spec_id: The ID of the Compute Spec. If `None`, use the most recently
            used Compute Spec id.
        verbose: If `True`, provide more detailed information.
    Returns:
        UUID: This UUID is your reference to the submitted job
    """
    compute_spec_id, session = _command_preamble(compute_spec_id)

    job_uri = _get_job_api_url(compute_spec_id)

    # Check that the payload can be serialised to JSON before trying to send it
    try:
        json.dumps(job_args)
    except json.decoder.JSONDecodeError:
        raise JobsException(
            "The payload could not be serialised to JSON. Please provide "
            "a JSON serializable dictionary."
        )

    response = exception_handled_request(session, job_uri, "post", json=job_args)

    try:
        data = response.json()
        id = data["job_id"]
    except (requests.exceptions.JSONDecodeError, KeyError):
        raise JobsException(
            "Could not decode response from the submission request. Note that your "
            "job may have been created successfully; please check the raw error for more "
            f"details: \n{response.text}."
        )

    if verbose:
        print("\nWe successfully submitted the job. Please note the ID {id}")

    cache_job_id(id)
    return UUID(id)


def abort(job_id: Optional[UUID] = None, compute_spec_id: Optional[UUID] = None):
    """
    Abort a job

    Arguments:
        job_id: The ID of the job that shall be aborted
        compute_spec_id: The ID of the Compute Spec. If `None`, use the most recently
            used Compute Spec id.
    """
    compute_spec_id, session = _command_preamble(compute_spec_id)
    job_id = get_job_id(job_id, verbose=False)

    job_uri = f"{_get_job_api_url(compute_spec_id)}/{job_id}/abort"

    exception_handled_request(session, job_uri, "post")


def download_results(
    download_path: Union[str, Path],
    job_id: Optional[UUID] = None,
    compute_spec_id: Optional[UUID] = None,
):
    """
    Download the results of a job

    Arguments:
        download_path: File path to download the results to
        job_id: The ID of the job
        compute_spec_id: The ID of the Compute Spec. If `None`, use the most recently
            used Compute Spec id.
    """
    compute_spec_id, session = _command_preamble(compute_spec_id)
    job_id = get_job_id(job_id)

    if isinstance(download_path, str):
        download_path = Path(download_path)

    job_uri = f"{_get_job_api_url(compute_spec_id)}/{job_id}/output"

    # Based on testing, large payloads are likely to take around 10s to prepare.
    # Increase the timeout to a larger value for the duration, unless it's already been
    # set.
    timeout_was_set = request_timeout_is_set()
    if not timeout_was_set:
        override_request_timeout(DEFAULT_TIMEOUT * 2)

    response = exception_handled_request(session, job_uri, "get")

    if not timeout_was_set:
        unset_request_timeout()

    try:
        os.makedirs(download_path, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            fpath_tar = Path(temp_dir) / "downloaded_content.tar.gz"
            fpath_tar.write_bytes(response.content)
            with tarfile.open(fpath_tar, mode="r") as tar:
                # tarfile is part of pythons standard library
                # filter argument is not available for all subversions 3.x.y
                try:
                    tar.extractall(download_path, filter="data")
                except TypeError as e:
                    if "unexpected keyword argument 'filter'" in str(e):
                        warn(
                            "The tarfile module does not support the filter argument. "
                            "Please update to a newer version of Python."
                        )
                        tar.extractall(download_path)

    except Exception as err:
        raise JobsException(
            "An unexpected error occurred while downloading the output for the "
            f"job id {job_id}. Please see the full error for more information: "
            f"\n{str(err)}"
        )


def logs(
    job_id: Optional[UUID] = None,
    compute_spec_id: Optional[UUID] = None,
) -> str:
    """
    Get the logs of a job

    Arguments:
        job_id: The ID of the job whose logs shall be fetched
        compute_spec_id: The ID of the Compute Spec. If `None`, use the most recently
            used Compute Spec id.

    Returns:
        str: A string that contains the logs
    """

    compute_spec_id, session = _command_preamble(compute_spec_id)
    job_id = get_job_id(job_id)

    if compute_spec_id is None:
        raise ValueError(
            "Compute Spec ID was empty and no cached value was found. "
            "Please provide as an argument."
        )

    if job_id is None:
        raise ValueError(
            "Job ID was empty and no cached value was found. "
            "Please provide as an argument."
        )

    job_uri = f"{_get_job_api_url(compute_spec_id)}/{job_id}/logs.txt"
    response = exception_handled_request(session, job_uri, "get")

    return response.text


def wait_until_job_finished(
    job_id: Union[UUID, str, None] = None,
    check_interval: Optional[float] = None,
    timeout: Optional[float] = 100,
    warn_time: Optional[float] = None,
):
    """
    Wait until a job is finished

    Arguments:
        job_id: The ID of the job
        check_interval: Interval between http-requests that query the status in seconds.
        timeout: Maximum time to wait in seconds before a TimeoutError is raised.
        warn_time: After this time in seconds, a warning is fired.
    """

    job_id = get_job_id(job_id)

    if check_interval is None:
        check_interval = 3
    elif isinstance(check_interval, UUID) or isinstance(check_interval, str):
        # Check whether the 2nd arg was provided as a UUID, in which case the caller needs
        # to update to remove the compute spec ID argument from their function call.
        # A bit loose with the check here as check_interval should never be a string anyway.
        # We could explicitly check to see if the string is a UUID, but probably overkill.
        raise TypeError(
            "The argument `check_interval` expects an input of float type but "
            f"{type(check_interval).__name__} was provided. Please make sure, you are "
            "not passing the `compute_spec_id` to `wait_until_job_finished`. This is no "
            "longer supported."
        )

    start = time.time()
    is_warned = False
    while True:
        current_status = status(UUID(job_id), verbose=False)
        if "finished" in current_status:
            break
        if (
            not is_warned
            and (warn_time is not None)
            and (time.time() - start >= warn_time)
        ):
            warn(
                f"The computation has been running for more than {warn_time}s. "
                "Performance may be improved by increasing the resources available to "
                "your Compute Spec. You can do this by specifying higher values for "
                "`client_n_cpu`, `client_memory`, `server_n_cpu` and `server_memory`."
            )
            is_warned = True
        if (timeout is not None) and (time.time() - start >= timeout):
            raise TimeoutError(f"Computation did not finish within {timeout}s. ")
        time.sleep(check_interval)
