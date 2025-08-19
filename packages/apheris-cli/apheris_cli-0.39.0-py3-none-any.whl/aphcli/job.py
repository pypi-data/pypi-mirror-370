import json
from ast import literal_eval
from pathlib import Path
from typing import Callable, Optional
from uuid import UUID
from warnings import warn

import typer
from typing_extensions import Annotated

from aphcli.api import job as job_api
from aphcli.api.compute import COMPUTE_SPEC_ACTIVATION_TIMEOUT, Resources
from aphcli.api.utils import prettytable_helpers
from aphcli.api.utils.comms import RequestError
from aphcli.utils import get_job_id, load_cached_compute_spec_id

from .utils import exception_handled_call_404, validate_is_logged_in

app = typer.Typer(no_args_is_help=True)


def _exception_handled_call(func: Callable):
    """
    This is a wrapper for api-request containing functions.
    Behavior:
        - RequestError with 404 --> "Job not found. [...]"
        - other RequestError and JobsException --> print as is
    """

    err_msg = (
        "Job not found. Please check if the `job_id` and `compute_spec_id` are correct."
    )

    return exception_handled_call_404(func, job_api.JobsException, err_msg)


def _load_job_payload(payload: str):
    if len(payload) <= 255 and Path(payload).is_file():
        with open(payload, "rt") as f:
            return json.load(f)
    else:
        try:
            return literal_eval(payload)
        except ValueError:
            print(
                "The `payload` that you provided does not refer to an existing file. We "
                "tried to interpret it as a JSON object but weren't "
                "successful. Please check your `payload` argument."
            )
            raise typer.Exit(2)


@app.command(help="Submit a job to run it.")
def run(
    payload: Annotated[
        str,
        typer.Option(
            "--payload",
            help=(
                "Arguments to provide to the job. You can either provide the filepath "
                "to a JSON file, or a string that contains a JSON compatible dictionary."
            ),
        ),
    ] = None,
    compute_spec_id: Annotated[
        UUID,
        typer.Option(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask if user is certain.")
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show more detailed information."),
    ] = False,
):
    validate_is_logged_in()

    if payload is None:
        warn("You did not provide a payload. So an empty payload will be submitted.")
        payload = "{}"
    payload = _load_job_payload(payload)

    if not force:
        print("About to submit job with parameters: ")
        print(payload)
        if not typer.confirm("\nDo you want to proceed? (y/N)\n:"):
            print("\nCancelling run job.")
            return

    try:
        job_id = job_api.submit(payload, compute_spec_id, verbose)
        print(f"\nThe job was submitted! The job ID is {job_id}")
    except RequestError as err:
        if err.status_code == 404:
            print("Compute Spec not found.")
            raise typer.Exit(1)
        else:
            print("Something went wrong. The job could not be submitted.")
            print(err)
            raise typer.Exit(1)
    except job_api.JobsException as err:
        # JobsException already contain an easy-to-understand message
        print(str(err))
        raise typer.Exit(1)


@app.command(help="Schedule a job with specified datasets, model, and resources.")
def schedule(
    dataset_ids: Annotated[
        str,
        typer.Option(
            "--dataset_ids",
            help="Comma-separated dataset IDs, e.g. `id1,id2,id3`",
        ),
    ],
    model_id: Annotated[
        str,
        typer.Option(
            "--model_id",
            help="A model ID, e.g. statistics",
        ),
    ],
    model_version: Annotated[
        str,
        typer.Option(
            "--model_version",
            help="The version of the model to use, e.g. 0.0.5",
        ),
    ],
    payload: Annotated[
        str,
        typer.Option(
            "--payload",
            help="Arguments to provide to the job. You can either provide the filepath "
            "to a JSON file, or a string that contains a JSON compatible dictionary",
        ),
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask if user is certain.")
    ] = False,
    client_n_cpu: Annotated[
        Optional[float],
        typer.Option("--client_n_cpu", help="number of vCPUs of Compute Clients"),
    ] = None,
    client_n_gpu: Annotated[
        Optional[int],
        typer.Option("--client_n_gpu", help="number of GPUs of Compute Clients"),
    ] = None,
    client_memory: Annotated[
        Optional[int],
        typer.Option("--client_memory", help="memory of Compute Clients [MByte]"),
    ] = None,
    server_n_cpu: Annotated[
        Optional[float],
        typer.Option("--server_n_cpu", help="number of vCPUs of Compute Aggregators"),
    ] = None,
    server_n_gpu: Annotated[
        Optional[int],
        typer.Option("--server_n_gpu", help="number of GPUs of Compute Aggregators"),
    ] = None,
    server_memory: Annotated[
        Optional[int],
        typer.Option("--server_memory", help="memory of Compute Aggregators [MByte]"),
    ] = None,
    num_clients_per_gateway: Annotated[
        Optional[int],
        typer.Option(
            "--num_clients_per_gateway",
            help="Number of compute clients to spawn (optional)",
        ),
    ] = None,
):
    validate_is_logged_in()

    if payload is None:
        warn("You did not provide a payload. So an empty payload will be submitted.")
        payload = "{}"
    payload = _load_job_payload(payload)

    args = {
        "client_n_cpu": client_n_cpu,
        "client_n_gpu": client_n_gpu,
        "client_memory": client_memory,
        "server_n_cpu": server_n_cpu,
        "server_n_gpu": server_n_gpu,
        "server_memory": server_memory,
    }
    args = {k: v for k, v in args.items() if v is not None}
    resources = Resources(**args)

    if not force:
        msg = f"""
        About to schedule job with parameters:
        Dataset IDs: {dataset_ids}
        Model: {model_id}:{model_version}
        Payload: {payload}
        Resources:
        Client: {resources.client_n_cpu} CPU, {resources.client_n_gpu} GPU, {resources.client_memory} MB memory
        Server: {resources.server_n_cpu} CPU, {resources.server_n_gpu} GPU, {resources.server_memory} MB memory
        """

        if num_clients_per_gateway is not None:
            msg += f"Number of Clients: {num_clients_per_gateway}\n"

        print(msg)

        if not typer.confirm("\nDo you want to proceed? (y/N)\n:"):
            print("\nCancelling schedule job.")
            return

    try:
        job = job_api.run(
            dataset_ids.split(","),
            payload,
            model_id,
            model_version,
            resources,
            num_clients_per_gateway,
        )
        print(f"\nThe job was submitted! The job ID is {job.id}")
    except RequestError as err:
        if err.status_code == 404:
            print("Compute Spec not found.")
        else:
            print(f"Something went wrong. The job could not be submitted.\n{str(err)}")
        raise typer.Exit(1)
    except TimeoutError:
        minutes = COMPUTE_SPEC_ACTIVATION_TIMEOUT // 60
        print(
            f"""
        Error: The compute specification is not running after {minutes} minutes of waiting.

        Possible reasons:
        - The requested resources may not be available in your environment
        - There might be an issue with the specified model version
        - The system might be experiencing high load or maintenance

        Suggested actions:
        - Try reducing the resource requirements (CPU, memory)
        - Check if the model version is correct
        - Try again later when the system might have more resources available
        - Use the compute spec commands for more detailed status information
        """
        )
        raise typer.Exit(1)
    except job_api.JobsException as err:
        # JobsException already contain an easy-to-understand message
        print(str(err))
        raise typer.Exit(1)
    except Exception as err:
        if "Multiple running Compute Specs found for" in str(err):
            print(f"Something went wrong. The job could not be submitted.\n{str(err)}")
            raise typer.Exit(1)
        else:
            raise


@app.command(help="List jobs.")
def list(
    compute_spec_id: Annotated[
        UUID, typer.Option(help="The ID of the Compute Spec. If `None`, returns all jobs")
    ] = None,
):
    validate_is_logged_in()
    try:
        jobs = job_api.list_jobs(compute_spec_id)

        if len(jobs) > 0:
            table = prettytable_helpers.table_from_collection_of_base_models(
                jobs,
                index_column="id",
                field_names=["duration", "id", "status", "created_at"],
            )

            table.align.update(
                {"duration": "r", "id": "l", "status": "l", "created_at": "l"}
            )
            print(f"\n{table}")
        else:
            print("\nNo jobs found.")
    except job_api.JobsException as err:
        # JobsException already contain an easy-to-understand message
        print(str(err))
        raise typer.Exit(1)

    except RequestError as err:
        if err.status_code == 404:
            print("Compute Spec not found.")
            raise typer.Exit(1)
        else:
            print("Something went wrong. The Compute Spec jobs were not found.")
            print(err)
            raise typer.Exit(1)


# ToDo: Remove `compute_spec_id` argument after deprecation phase
@app.command(help="Get the status and details of a job.")
def status(
    job_id: Annotated[
        UUID,
        typer.Option(
            "--job-id",
            help="The ID of the job. If `None`, use the most recently used job ID.",
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show more detailed information.")
    ] = False,
):
    validate_is_logged_in()

    # We do not propagate `verbose` into `job_api.get` to show information on the used
    # `job_id` in case we use a cached one.
    job_data = _exception_handled_call(job_api.get)(job_id)
    if verbose:
        print(f"\n{job_data}")
    else:
        print(f"\nstatus: {job_data.status}")


@app.command(help="Abort a currently running job.")
def abort(
    job_id: Annotated[
        UUID,
        typer.Option(
            "--job-id",
            help="The ID of the job. If `None`, use the most recently used job ID.",
        ),
    ] = None,
    compute_spec_id: Annotated[
        UUID,
        typer.Option(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask if user is certain.")
    ] = False,
):
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)

    if not job_id:
        job_id = get_job_id(job_id)

    if not force:
        if not typer.confirm("\nDo you want to proceed? (y/N)\n:"):
            print("\nCancelling abort job.")
            return

    _exception_handled_call(job_api.abort)(job_id, compute_spec_id)
    print("Job aborted.")


@app.command(help="Download the results of a job.")
def download_results(
    download_path: Annotated[
        Path,
        typer.Argument(
            help="Directory to store the downloaded results",
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
    job_id: Annotated[
        UUID,
        typer.Option(
            "--job-id",
            help="The ID of the job. If `None`, use the most recently used job ID.",
        ),
    ] = None,
    compute_spec_id: Annotated[
        UUID,
        typer.Option(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
):
    if download_path is None:
        if job_id:
            jstr = f"{job_id}_"
        else:
            jstr = ""
        download_path = Path(f"job_{jstr}results")

    _exception_handled_call(job_api.download_results)(
        download_path, job_id, compute_spec_id
    )
    print(f"\nSuccessfully downloaded job outputs to {download_path.absolute()}")


@app.command(
    help="Download the logs for a job, which can be optionally written to a file."
)
def logs(
    storage_path: Annotated[
        Path,
        typer.Option(
            help="File in which to store logs (plaintext)",
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
    job_id: Annotated[
        UUID,
        typer.Option(
            "--job-id",
            help="The ID of the job. If `None`, use the most recently used job ID.",
        ),
    ] = None,
    compute_spec_id: Annotated[
        UUID,
        typer.Option(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
):
    log_text = _exception_handled_call(job_api.logs)(job_id, compute_spec_id)

    if storage_path:
        print(f"Writing logs to {storage_path}")
        try:
            storage_path.write_text(log_text)
        except OSError:
            print(f"Could not write the logs to {storage_path}. Is the path writeable?")
            raise typer.Exit(1)
    else:
        print(log_text)
