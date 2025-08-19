import inspect
import json
import warnings
from pathlib import Path
from typing import Callable, List, Optional
from uuid import UUID

import typer
from typing_extensions import Annotated

import aphcli.api.compute as compute_api
from aphcli.api.models import Model
from aphcli.api.utils.comms import RequestError
from aphcli.api.utils.compute_spec_formatting import generate_table
from aphcli.api.utils.interaction import InteractiveInputError, LimitValidationError

from .utils import (
    exception_handled_call_404,
    load_cached_compute_spec_id,
    validate_is_logged_in,
)

app = typer.Typer(no_args_is_help=True)


def _exception_handled_call_404(func: Callable):
    """
    This is a wrapper for api-request containing functions.
    Behavior:
        - RequestError with 404 --> "Compute Spec not found."
        - other RequestError and ComputeSpecException --> print as is
    """
    return exception_handled_call_404(
        func,
        compute_api.ComputeSpecException,
        "Compute Spec not found.",
    )


def _exception_handled_call_print_only(func: Callable):
    """
    This is a wrapper for api-request containing functions.
    Behavior:
        - RequestError and ComputeSpecException --> print as is
    """

    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RequestError, compute_api.ComputeSpecException) as err:
            print(err)
            raise typer.Exit(1)

    return wrapped_func


def _validate_json_args(*args):
    var_names = [k for k in inspect.signature(create).parameters.keys()]
    set_vars = [var_names[k] for k, v in enumerate(args) if v is not None]
    return set_vars


def _create_with_json(
    dataset_ids: Optional[List[str]] = None,
    client_n_cpu: Optional[float] = None,
    client_n_gpu: Optional[int] = None,
    client_memory: Optional[int] = None,
    server_n_cpu: Optional[float] = None,
    server_n_gpu: Optional[int] = None,
    server_memory: Optional[int] = None,
    model_id: Optional[str] = None,
    model_version: Optional[str] = None,
    num_clients_per_gateway: Optional[int] = None,
    json_: Optional[Path] = None,
) -> compute_api.ComputeSpec:
    set_vars = _validate_json_args(
        dataset_ids,
        client_n_cpu,
        client_n_gpu,
        client_memory,
        server_n_cpu,
        server_n_gpu,
        server_memory,
        model_id,
        model_version,
        num_clients_per_gateway,
    )

    if set_vars:
        set_vars_str = ", ".join([f"--{v}" for v in set_vars])
        print(
            "If a Compute Spec is defined via the path to json file, it is not "
            "possible to pass other arguments. This is to avoid clashes.\n"
            "The following arguments were provided and should be removed: \n"
            f"\t{set_vars_str}"
        )
        raise typer.Exit(1)

    try:
        with open(json_, "r") as f:
            payload = json.load(f)
            compute_spec = compute_api.ComputeSpec.from_dict(payload)
    except FileNotFoundError:
        print(f"Could not find the JSON file at path: {json_}")
        raise typer.Exit(1)
    except json.decoder.JSONDecodeError:
        print(
            "Could not decode the JSON file into a Compute Spec, please check your "
            "file is valid."
        )
        raise typer.Exit(1)
    except LimitValidationError as e:
        print(e)
        raise typer.Exit(1)
    except Exception:
        print(
            "Encountered an unexpected error while decoding the Compute Spec from " "JSON"
        )
        raise typer.Exit(1)
    return compute_spec


@app.command(
    help="Create a Compute Spec on the Apheris orchestrator. All parameters "
    "that are not passed as command line arguments will be interactively queried."
)
def create(
    dataset_ids: Annotated[
        str,
        typer.Option(
            "--dataset_ids",
            help="Comma-separated dataset IDs, e.g. `-dataset_ids=id1,id2,id3`",
        ),
    ] = None,
    ignore_limits: Annotated[
        bool,
        typer.Option(
            "--ignore_limits",
            help="The CLI sets some expected bounds for requested infrastructure "
            "resources. Use this flag to override the validation checks if your model "
            "requires more resources.",
        ),
    ] = False,
    client_n_cpu: Annotated[
        float, typer.Option("--client_n_cpu", help="number of vCPUs of Compute Clients")
    ] = None,
    client_n_gpu: Annotated[
        int, typer.Option("--client_n_gpu", help="number of GPUs of Compute Clients")
    ] = None,
    client_memory: Annotated[
        int, typer.Option("--client_memory", help="memory of Compute Clients [MByte]")
    ] = None,
    server_n_cpu: Annotated[
        float,
        typer.Option("--server_n_cpu", help="number of vCPUs of Compute Aggregators"),
    ] = None,
    server_n_gpu: Annotated[
        int,
        typer.Option("--server_n_gpu", help="number of GPUs of Compute Aggregators"),
    ] = None,
    server_memory: Annotated[
        int,
        typer.Option("--server_memory", help="memory of Compute Aggregators [MByte]"),
    ] = None,
    model_id: Annotated[
        str, typer.Option("--model_id", help="A model ID, e.g. apheris-statistics")
    ] = None,
    model_version: Annotated[
        str,
        typer.Option(
            "--model_version", help="The version of the model to use, e.g. v0.0.5"
        ),
    ] = None,
    num_clients_per_gateway: Annotated[
        int,
        typer.Option(
            "--num_clients_per_gateway",
            help="Number of compute clients to spawn (optional, for advanced users)",
        ),
    ] = None,
    json_: Annotated[
        Path,
        typer.Option(
            "--json",
            help="File path to json file that describes a Compute Spec. Please use the "
            "interactive workflow once to learn about the expected format. If "
            "specified, all other arguments (except for `force`) must be None to "
            "avoid clashes.",
            exists=True,
            file_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help=(
                "Do not ask if user is certain, and do not ask for arguments "
                "interactively."
            ),
        ),
    ] = False,
):
    validate_is_logged_in()
    print("\n# Create Compute Spec.\n")

    if ignore_limits:
        compute_api.set_ignore_limits(True)

    if json_:
        compute_spec = _create_with_json(
            dataset_ids,
            client_n_cpu,
            client_n_gpu,
            client_memory,
            server_n_cpu,
            server_n_gpu,
            server_memory,
            model_id,
            model_version,
            num_clients_per_gateway,
            json_,
        )
    else:
        dataset_ids = dataset_ids.split(",") if dataset_ids else None
        if model_id is None and model_version is None:
            model = None
        elif model_id is None or model_version is None:
            print(
                "Only one of `model_id` and `model_version` were supplied and will be "
                "ignored. To avoid this behaviour, please supply both `model_version` "
                "and `model_id`. To see the available models and their versions, run "
                "`apheris models list`\n"
            )
            model = None
        else:
            model = Model(model_id, model_version)
        compute_spec = compute_api.ComputeSpec(
            dataset_ids=dataset_ids,
            client_n_cpu=client_n_cpu,
            client_n_gpu=client_n_gpu,
            client_memory=client_memory,
            server_n_cpu=server_n_cpu,
            server_n_gpu=server_n_gpu,
            server_memory=server_memory,
            model=model,
        )

    unset_fields = compute_spec.get_unset_fields()
    unset_fields = [f.name for f in unset_fields]
    if len(unset_fields) > 0 and force:
        print(
            f"You did not specify following arguments: {unset_fields}. When using "
            "`--force`, it is not possible to set arguments interactively."
        )
        raise typer.Exit(2)

    try:
        compute_spec.ask_for_empty_inputs()
    except InteractiveInputError as err:
        print(err)
        raise err from None

    if not force:
        print("\nYou are about to create following Compute Spec:\n")
        print(compute_spec.to_json())
        answer = input("Do you want to create this Compute Spec? (y/N)\n:")
        is_certain = answer in ["Y", "y"]

        if not is_certain:
            print("\nAborting creation of a Compute Spec")
            return

    _exception_handled_call_print_only(compute_api.create)(compute_spec, verbose=True)


@app.command(help="Get a Compute Spec from the Apheris orchestrator.")
def get(
    compute_spec_id: Annotated[
        UUID,
        typer.Argument(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
):
    validate_is_logged_in()
    cs = _exception_handled_call_404(compute_api.get)(compute_spec_id)
    print(cs.to_json())


@app.command(help="List all your Compute Specs.")
def list(
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help=(
                "Limit the number of Compute Specs shown. Set a negative number to show all"
            ),
        ),
    ] = 10,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show more detailed status information."),
    ] = False,
    active_only: Annotated[
        bool,
        typer.Option("--active_only", help="List only active Compute Specs."),
    ] = False,
):
    validate_is_logged_in()

    if limit < 0:
        limit = None

    compute_specs = _exception_handled_call_print_only(compute_api.list_compute_specs)(
        active_only=active_only, limit=limit
    )
    num_compute_specs = _exception_handled_call_print_only(
        compute_api.get_compute_spec_count
    )(active_only=active_only)

    if len(compute_specs) == 0:
        print("\nNo Compute Specs found.")
        return

    if len(compute_specs) < num_compute_specs:
        print(
            f"\nShowing {len(compute_specs)} out of {num_compute_specs} Compute "
            "Specs. To show more, use '--limit <NUMBER TO SHOW>' flag."
        )

    compute_specs_table = generate_table(compute_specs, verbose)

    print(compute_specs_table)


@app.command(
    help="Activate a Compute Spec. This will spin up a cluster of "
    "Compute Clients and Compute Aggregators."
)
def activate(
    compute_spec_id: Annotated[
        UUID,
        typer.Argument(
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
    if force:
        is_certain = True
    else:
        if not compute_spec_id:
            compute_spec_id = load_cached_compute_spec_id(True)

        answer = input("\nDo you want to activate this Compute Spec? (y/N)\n:")
        is_certain = answer in ["Y", "y"]

    if not is_certain:
        print("\n Aborting activation.")
        return

    _exception_handled_call_404(compute_api.activate)(compute_spec_id, verbose=True)


@app.command(
    help="Deactivate a Compute Spec - stops any running jobs and shuts down any "
    "infrastructure that was brought up for this Compute Spec. Use this if you have spun "
    "up a cluster of Compute Clients and Compute Aggregators, and don't need it "
    "anymore.\n"
    "Provided the Compute Spec remains approved, you can use activate to "
    "reinstate the infrastructure if needed at a later time."
)
def deactivate(
    compute_spec_id: Annotated[
        UUID,
        typer.Argument(
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
    if force:
        is_certain = True
    else:
        if not compute_spec_id:
            compute_spec_id = load_cached_compute_spec_id(True)

        answer = input(
            "\nDo you want to deactivate this Compute Spec and shut down any "
            "attached infrastructure? (y/N)\n:"
        )
        is_certain = answer in ["Y", "y"]

    if not is_certain:
        print("\nAborting deactivation.")
        return

    _exception_handled_call_404(compute_api.deactivate)(compute_spec_id, verbose=True)


@app.command(help="Get information on the status of the activation of a Compute Spec.")
def activate_status(
    compute_spec_id: Annotated[
        UUID,
        typer.Argument(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
):
    validate_is_logged_in()
    status = _exception_handled_call_404(compute_api.get_activation_status)(
        compute_spec_id
    )
    print(status)


@app.command(help="Get the status of a Compute Spec.")
def status(
    compute_spec_id: Annotated[
        UUID,
        typer.Argument(
            help=(
                "The ID of the Compute Spec. If `None`, use the most recently used "
                "Compute Spec ID."
            )
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help=(
                "Show more information about Compute Spec status. Can be used to "
                "diagnose the issue when your Compute Spec is stuck in creating, for "
                "example, due to capacity constraints."
            ),
        ),
    ] = False,
):
    validate_is_logged_in()
    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)
        print("\n")

    try:
        activation_details = compute_api.get_status(compute_spec_id)
    except RequestError as err:
        if "Compute Spec not found" in str(err):
            print("Compute Spec not found.")
            raise typer.Exit(1)
        if err.status_code == 401:
            print("You are not authorized to access this Compute Spec.")
            raise typer.Exit(1)
        else:
            raise err
    activation_status = activation_details.get("status", "unknown")
    print(f"Activation status:\t{activation_status}")

    if verbose:
        try:
            activation_json = activation_details.get("message", "unavailable")
            activation_dict = json.loads(activation_json)

            # Add a newline before and after the list to make it clearer to read, but only
            # if the list is actually being written to prevent a big block of whitespace.
            activation_message = (
                "\n".join([f"\t * [{k}]: {v}" for k, v in activation_dict.items()]) + "\n"
            )
        except json.JSONDecodeError:
            warnings.warn(
                "Could not parse JSON message, outputting raw response instead."
            )
            activation_message = activation_json

        print(f"Activation details:\n{activation_message}")


@app.command(
    help="Deactivate all Compute Specs that are in an active or transitional state."
)
def deactivate_all(
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask for confirmation.")
    ] = False,
):
    validate_is_logged_in()

    if not force:
        answer = input(
            "\nAre you sure you want to deactivate all Compute Specs? (y/N)\n:"
        )
        is_certain = answer in ["Y", "y"]
        if not is_certain:
            print("\nAborting deactivation.")
            return

    _exception_handled_call_404(compute_api.deactivate_all)()
