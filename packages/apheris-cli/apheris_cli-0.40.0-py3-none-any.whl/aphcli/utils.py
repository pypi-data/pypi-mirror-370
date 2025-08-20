import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Type, Union
from uuid import UUID

import typer
from requests_oauthlib import OAuth2Session

from aphcli.api.utils.comms import RequestError

COMPUTE_SPEC_ID_CACHE = Path.home() / ".apheris" / "cli" / "compute_spec_id.json"


def get_oauth_session() -> OAuth2Session:
    from apheris_auth.core.api import ApherisAPI
    from apheris_auth.core.exceptions import Unauthorized

    try:
        api = ApherisAPI()
        session = api._session
    except Unauthorized:
        print("You are not logged in. Please login.")
        raise typer.Exit(1)
    return session


def validate_is_logged_in() -> None:
    from apheris_auth.core.auth import is_logged_in

    if is_logged_in():
        return
    else:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)


def load_cached_compute_spec_id(force=False) -> UUID:
    if COMPUTE_SPEC_ID_CACHE.is_file():
        data = json.loads(COMPUTE_SPEC_ID_CACHE.read_text())
        compute_spec_id = UUID(data["compute_spec_id"])
        date_str = data["date_str"]

        if force:
            is_confirmed = True
        else:
            print(
                f"\nOn {date_str} you have used the `compute_spec_id` "
                f"{str(compute_spec_id)}."
            )

            answer = input("Do you want to use it? (y/N)\n:")
            is_confirmed = answer in ["y", "Y"]
        if is_confirmed:
            print(
                f"Using the cached `compute_spec_id` {str(compute_spec_id)} [stored {date_str}]."
            )
            return compute_spec_id
        else:
            pass
    else:
        pass
    print("No `compute_spec_id` provided. Please provide one as command line argument.")
    raise typer.Exit(2)


def cache_compute_spec_id(compute_spec_id: UUID) -> None:
    if not COMPUTE_SPEC_ID_CACHE.parent.is_dir():
        os.makedirs(COMPUTE_SPEC_ID_CACHE.parent)
    data = {
        "compute_spec_id": str(compute_spec_id),
        "date_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    COMPUTE_SPEC_ID_CACHE.write_text(json.dumps(data))


JOB_ID_CACHE = Path.home() / ".apheris" / "cli" / "job_id.json"


def _load_cached_job_id(force: bool = False) -> str:
    if JOB_ID_CACHE.is_file():
        data = json.loads(JOB_ID_CACHE.read_text())
        job_id = data["job_id"]
        date_str = data["date_str"]

        if force:
            is_confirmed = True
        else:
            print(f"\nOn {date_str} you have used the job ID `{job_id}`.")
            answer = input("Do you want to use it? (y/N)\n:")
            is_confirmed = answer in ["y", "Y"]
        if is_confirmed:
            print(f"Using the cached `job_id` {job_id} [stored {date_str}].")
            return job_id
        else:
            raise RuntimeError("Loading of cached job ID aborted.")
    else:
        pass

    raise ValueError("Could not find a cached Job ID, please provide using --job-id")


def cache_job_id(job_id):
    JOB_ID_CACHE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "job_id": str(job_id),
        "date_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    JOB_ID_CACHE.write_text(json.dumps(data))


def get_job_id(job_id: Union[str, UUID, None], force: bool = True, verbose=True) -> str:
    if job_id is None:
        job_id = _load_cached_job_id(force=force)
    else:
        if verbose:
            print(f"You provided the job ID {job_id}.")
        cache_job_id(job_id)
    return str(job_id)


def get_login_status() -> tuple:
    from apheris_auth.core.auth import is_logged_in as auth_is_logged_in
    from apheris_auth.core.auth_helpers import get_login_information
    from apheris_auth.core.exceptions import Unauthorized

    is_logged_in = auth_is_logged_in()
    claims = {}
    if is_logged_in:
        try:
            claims = get_login_information()
        except Unauthorized:
            pass
    email = claims.get("email", "")
    organization = claims.get("organization", "")
    env = claims.get("env", "")
    return is_logged_in, email, organization, env


def exception_handled_call_404(func: Callable, exception_class: Type, error_msg_404: str):
    """
    This is a wrapper for api-request containing functions.
    Behavior:
        - RequestError with 404 --> "error_msg_404."
        - other RequestError and ComputeSpecException --> print as is
    """

    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestError as err:
            if err.status_code == 404:
                print(error_msg_404)
                raise typer.Exit(1)
            else:
                print(str(err))
                raise typer.Exit(1)
        except exception_class as err:
            # ComputeSpecException already contains an easy-to-understand message
            print(str(err))
            raise typer.Exit(1)

    return wrapped_func
