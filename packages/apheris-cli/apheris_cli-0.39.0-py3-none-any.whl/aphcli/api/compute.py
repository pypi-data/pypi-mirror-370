import json
import os
import time
import warnings
from dataclasses import Field, dataclass, fields
from functools import partial
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from ..utils import (
    cache_compute_spec_id,
    get_oauth_session,
    load_cached_compute_spec_id,
    validate_is_logged_in,
)
from .models import Model
from .utils import ComputeSpecException, interaction
from .utils.comms import RequestError, exception_handled_request
from .utils.interaction import LimitValidationError

# Define timeout constants
COMPUTE_SPEC_ACTIVATION_TIMEOUT = 600  # seconds (10 minutes)

FIELD_PROMPTS = {
    "dataset_ids": "Please provide a value for the Dataset IDs",
    "client_n_cpu": "Please provide the number of Client vCPUs, (e.g. `1` or `2.5`)",
    "client_n_gpu": "Please provide the number of Client GPUs (`0` or `1`)",
    "client_memory": (
        "Please provide the amount of Client Memory in MBytes (e.g. `1024` will translate"
        " into 1GB)"
    ),
    "server_n_cpu": "Please provide the number of Server vCPUs, (e.g. `1` or `2.5`)",
    "server_n_gpu": "Please provide the number of Server GPUs (`0` or `1`)",
    "server_memory": (
        "Please provide the amount of Server Memory in MBytes (e.g. `1024` will translate"
        " into 1GB)"
    ),
    "model": "Please provide the model",
}

LIMITS = {
    "client_n_cpu": {"min": 0.1, "max": 16},
    "server_n_cpu": {"min": 0.1, "max": 16},
    "client_n_gpu": {"min": 0, "max": 1},
    "server_n_gpu": {"min": 0, "max": 1},
    "server_memory": {"min": 500, "max": 16000},
    "client_memory": {"min": 500, "max": 16000},
}

ACTIVE_OR_TRANSITIONAL_STATES = ["updating", "active", "failed"]
PAGE_SIZE = 20_000


def set_ignore_limits(ignore: bool):
    """
    Limits have been set on"""
    if ignore:
        os.environ["APH_CLI_IGNORE_LIMITS"] = "1"
    else:
        if "APH_CLI_IGNORE_LIMITS" in os.environ:
            del os.environ["APH_CLI_IGNORE_LIMITS"]


def _validate_limits(value: Any, var_name: str):
    if os.environ.get("APH_CLI_IGNORE_LIMITS"):
        return

    min = LIMITS[var_name]["min"]
    max = LIMITS[var_name]["max"]
    if (value < min) or (value > max):
        raise LimitValidationError(
            f"The value for `{var_name}` ({value}) is outside of the expected bounds. "
            f"Please choose a value between {min} and {max}.\n"
            "If you still wish to use a value outside the range, please use the flag "
            "`--ignore_limits` if using the terminal CLI or `set_ignore_limits(True)` if "
            "using the Python API.",
            min_limit=min,
            max_limit=max,
        )


def _url_for_compute_command(cmd: Optional[str] = "", id: Optional[UUID] = None) -> str:
    from apheris_auth.config import settings

    base = f"{str(settings.API_ORCHESTRATOR_BASE_URL)}/computespec"
    if not cmd and not id:
        return base
    if cmd and id is None:
        raise ValueError(f"Command {cmd} requires the ID of the Compute Spec")
    if cmd:
        cmd = cmd.strip("/")
    return f"{base}/{str(id)}/{cmd}"


class Resources(BaseModel):
    client_n_cpu: float = 1
    client_n_gpu: int = 0
    client_memory: int = 2048
    server_n_cpu: float = 0.5
    server_n_gpu: int = 0
    server_memory: int = 512


@dataclass
class ComputeSpec:
    """
    dataset_ids: List of dataset IDs
    client_n_cpu: number of vCPUs of Compute Clients
    client_n_gpu: number of GPUs of Compute Clients
    client_memory: memory of Compute Clients [MByte]
    server_n_cpu: number of vCPUs of Compute Aggregators
    server_n_gpu: number of GPUs of Compute Aggregators
    server_memory: memory of Compute Aggregators [MByte]
    model: model to use
    num_clients_per_gateway: number of compute clients to spawn per gateway (optional)
    """

    dataset_ids: Optional[List[str]] = None
    client_n_cpu: Optional[float] = None
    client_n_gpu: Optional[int] = None
    client_memory: Optional[int] = None
    server_n_cpu: Optional[float] = None
    server_n_gpu: Optional[int] = None
    server_memory: Optional[int] = None
    model: Optional[Union[Model, Dict[str, str]]] = None
    num_clients_per_gateway: Optional[int] = None

    _id: Optional[UUID] = None

    def __post_init__(self):
        if isinstance(self.dataset_ids, str) and "," in self.dataset_ids:
            warnings.warn(
                "Detected comma-separated string list of dataset IDs. Splitting."
            )
            self.dataset_ids = [d.strip() for d in self.dataset_ids.split(",")]
        elif isinstance(self.dataset_ids, str):
            warnings.warn(
                "Dataset ID was provided as a string, but should be a list. Wrapping."
            )
            self.dataset_ids = [self.dataset_ids]
        elif (
            not isinstance(self.dataset_ids, (tuple, list))
            and self.dataset_ids is not None
        ):
            raise ValueError("Dataset IDs should be a list of strings.")

        if self.client_n_gpu is not None:
            self.client_n_gpu = int(self.client_n_gpu)
            _validate_limits(self.client_n_gpu, "client_n_gpu")

        if self.client_memory is not None:
            self.client_memory = int(self.client_memory)
            _validate_limits(self.client_memory, "client_memory")

        if self.server_n_gpu is not None:
            self.server_n_gpu = int(self.server_n_gpu)
            _validate_limits(self.server_n_gpu, "server_n_gpu")

        if self.server_memory is not None:
            self.server_memory = int(self.server_memory)
            _validate_limits(self.server_memory, "server_memory")

        if self.client_n_cpu is not None:
            self.client_n_cpu = float(self.client_n_cpu)
            _validate_limits(self.client_n_cpu, "client_n_cpu")

        if self.server_n_cpu is not None:
            self.server_n_cpu = float(self.server_n_cpu)
            _validate_limits(self.server_n_cpu, "server_n_cpu")

        if self.num_clients_per_gateway is not None:
            self.num_clients_per_gateway = int(self.num_clients_per_gateway)
            if self.num_clients_per_gateway <= 0:
                raise ValueError("num_clients_per_gateway must be a positive integer")

        if self.model is not None and isinstance(self.model, Dict):
            if not set(self.model.keys()) == {"id", "version"}:
                raise ValueError(
                    "`model` must be a `Model(id, version)` object or a dictionary with "
                    "keys `id` and `version`."
                )
            self.model = Model.from_dict(self.model)

        elif self.model is not None and not isinstance(self.model, Model):
            raise ValueError("`model` must be a `Model(id, version)` object.")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "datasets": self.dataset_ids,
            "resources": {
                "clients": {
                    "cpu": self.client_n_cpu,
                    "gpu": self.client_n_gpu,
                    "memory": self.client_memory,
                },
                "server": {
                    "cpu": self.server_n_cpu,
                    "gpu": self.server_n_gpu,
                    "memory": self.server_memory,
                },
            },
            "model": self.model.to_dict() if self.model else None,
        }

        if self.num_clients_per_gateway is not None:
            result["numClientsPerGateway"] = self.num_clients_per_gateway

        return result

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            indent=3,
        )

    def _populate_from_dict(self, dict_data: Dict[str, Any]):
        try:
            self.dataset_ids = dict_data.get("datasets")
            if "resources" in dict_data:
                if "clients" in dict_data["resources"]:
                    self.client_n_cpu = dict_data["resources"]["clients"].get("cpu")
                    self.client_n_gpu = dict_data["resources"]["clients"].get("gpu")
                    self.client_memory = dict_data["resources"]["clients"].get("memory")
                if "server" in dict_data["resources"]:
                    self.server_n_cpu = dict_data["resources"]["server"].get("cpu")
                    self.server_n_gpu = dict_data["resources"]["server"].get("gpu")
                    self.server_memory = dict_data["resources"]["server"].get("memory")

            self.num_clients_per_gateway = dict_data.get("numClientsPerGateway")
            self.model = Model.from_dict(dict_data.get("model", None))
            if "id" in dict_data:
                self._id = UUID(dict_data["id"])
        except KeyError as err:
            raise ComputeSpecException(
                f"Compute Spec JSON was malformed, could not find field {str(err)}."
            )

    @staticmethod
    def from_dict(
        dict_data: Dict[str, Any], skip_validation: bool = False
    ) -> "ComputeSpec":
        cs = ComputeSpec()
        cs._populate_from_dict(dict_data)
        if not skip_validation:
            cs.__post_init__()
        return cs

    def ask_for_empty_inputs(self):
        special_cases = {
            "dataset_ids": lambda x: interaction.get_datasets_interactively(),
            "model": lambda x: interaction.get_model_interactively(),
        }

        unset_fields = self.get_unset_fields()
        for field in unset_fields:
            val = getattr(self, field.name)
            if val is not None or field.name.startswith("_"):
                continue

            if field.name in special_cases:
                value = special_cases[field.name](field.type)
            else:
                field_prompt = FIELD_PROMPTS[field.name]

                value = interaction.get_typed_response_interactively(
                    field.name,
                    f"{field_prompt}: ",
                    interaction.type_from_optional(field.type),
                    limit_validator=partial(_validate_limits, var_name=field.name),
                )

            setattr(self, field.name, value)

    def get_unset_fields(self) -> List[Field]:
        unset_fields = []
        for field in fields(self):
            val = getattr(self, field.name)
            if (
                val is None
                and not field.name.startswith("_")
                and field.name != "num_clients_per_gateway"
            ):
                unset_fields.append(field)
        return unset_fields

    def __str__(self):
        return self.to_json()

    def __eq__(self, __value: object) -> bool:
        return vars(self) == vars(__value)


# The __eq__ method tries to match the hidden _id field which breaks the purpose of this method
def match(cs1: ComputeSpec, cs2: ComputeSpec) -> bool:
    """
    Compare two ComputeSpec objects for equality, ignoring internal fields.

    Args:
        cs1: First ComputeSpec object to compare
        cs2: Second ComputeSpec object to compare

    Returns:
        bool: True if all non-internal fields match between the two objects, False otherwise
    """
    for field in fields(cs1):
        if field.name.startswith("_"):
            continue
        if getattr(cs1, field.name) != getattr(cs2, field.name):
            return False
    return True


def deactivate_all():
    """
    Deactivate all Compute Specs that are in an active or transitional state.

    This includes Compute Specs with status:
    - running
    - creating
    - failed
    - waiting_for_resources
    """
    for cs in list_compute_specs(active_only=True, limit=None):
        deactivate(cs["id"], cache=False)


def create(compute_spec: ComputeSpec, verbose: bool = False, cache: bool = True) -> UUID:
    """
    Create a Compute Spec.

    Args:
        compute_spec:    Compute Spec to be created.
        verbose:         If `True`, print more detailed information.
        cache:           If `True`, cache the Compute Spec ID after creation.

    Returns:
        UUID: ID of the created Compute Spec."""
    validate_is_logged_in()

    unset_fields = compute_spec.get_unset_fields()
    if unset_fields:
        unset_field_str = ", ".join(f.name for f in unset_fields)
        raise ComputeSpecException(
            f"Compute Spec is not correctly configured - some mandatory "
            f"fields have not been set:\n {unset_field_str}"
        )

    payload = compute_spec.to_json()

    session = get_oauth_session()
    response = exception_handled_request(
        session, _url_for_compute_command(), "post", payload
    )

    try:
        if response.reason.upper() == "CREATED":
            data = response.json()
            id = data["id"]
            if verbose:
                print(
                    "\nWe successfully created a Compute Spec. Please note the "
                    f"ID {id}"
                )
                print(json.dumps(data, indent=3))
            if cache:
                cache_compute_spec_id(id)
            return UUID(id)
        else:
            raise RequestError(
                "Something went wrong. \n" + json.dumps(response.json(), indent=3),
                status_code=response.status_code,
            )
    except json.decoder.JSONDecodeError:
        raise ComputeSpecException(
            "Could not decode response from the creation request. Note that your "
            "Compute Spec may have been created successfully; please check "
            f"the raw error for more details: \n{response.text}."
        )


def create_from_args(
    dataset_ids: Optional[List[str]] = None,
    client_n_cpu: Optional[float] = None,
    client_n_gpu: Optional[int] = None,
    client_memory: Optional[int] = None,
    server_n_cpu: Optional[float] = None,
    server_n_gpu: Optional[int] = None,
    server_memory: Optional[int] = None,
    model: Optional[Dict[str, str]] = None,
    model_id: Optional[str] = None,
    model_version: Optional[str] = None,
) -> UUID:
    """Create a Compute Spec from raw arguments.

    To describe the model, the user can supply either a dictionary with `id` and `version`
    fields, or provide them as individual arguments.

    Args:
        dataset_ids: List of dataset IDs.
        client_n_cpu: Number of vCPUs for the client.
        client_n_gpu: Number of GPUs for the client.
        client_memory: Amount of memory in MB for the client.
        server_n_cpu: Number of vCPUs for the server.
        server_n_gpu: Number of GPUs for the server.
        server_memory: Amount of memory in MB for the server.
        model: Dictionary with `id` and `version` fields.
        model_id: ID of the model.
        model_version: Version of the model.

    Returns:
        UUID: ID of the created Compute Spec.
    """

    if model is None:
        if model_id or model_version:
            model = Model(model_id, model_version)
    elif model_id or model_version:
        raise ComputeSpecException(
            "Please supply only a `model` dict or the `model_id` and "
            "`model_version` parameters, not both."
        )
    elif not isinstance(model, Dict):
        raise ComputeSpecException(
            "Model must be a dictionary with 2 keys, 'id' and 'version'."
        )

    compute_spec = ComputeSpec(
        dataset_ids,
        client_n_cpu,
        client_n_gpu,
        client_memory,
        server_n_cpu,
        server_n_gpu,
        server_memory,
        model,
    )

    return create(compute_spec)


def get(compute_spec_id: Optional[UUID] = None, cache: bool = True) -> ComputeSpec:
    """Get a Compute Spec ID.

    Args:
        compute_spec_id:    Compute Spec ID that shall be fetched. If `None`, use the
            most recently used Compute Spec ID.
        cache:              If `True`, cache the Compute Spec ID after getting the Compute Spec.

    Returns:
        ComputeSpec: definition of a Compute Spec
    """
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)

    session = get_oauth_session()
    url = _url_for_compute_command(id=compute_spec_id)
    response = exception_handled_request(session, url, "get")

    try:
        # Exising compute specs can have resource limits that are outside the recommended
        # range. Validating them would result in an exception.
        compute_spec = ComputeSpec.from_dict(response.json(), skip_validation=True)

        if cache:
            cache_compute_spec_id(compute_spec_id)
    except json.decoder.JSONDecodeError as err:
        raise ComputeSpecException(
            "Could not decode response from the Compute Spec request. "
            f"Please check the raw error for more details: \n{str(err)}."
        )
    return compute_spec


def activate(
    compute_spec_id: Optional[UUID] = None, verbose: bool = False, cache: bool = True
):
    """Activate a Compute Spec ID.

    Args:
        compute_spec_id:    Compute Spec ID that shall be activated. If `None`, use the
            most recently used Compute Spec ID.
        verbose: If `True`, print more detailed information.
        cache:    If `True`, cache the Compute Spec ID after activation.
    """
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)

    session = get_oauth_session()
    url = _url_for_compute_command(cmd="deploy", id=compute_spec_id)
    response = exception_handled_request(session, url, "post", payload={})

    if response.reason == "OK":
        if verbose:
            print(
                "\nSuccessfully requested activation of the Compute Spec "
                f"{compute_spec_id}!"
            )
            deployment = response.json()
            print(json.dumps(deployment, indent=3))
        if cache:
            cache_compute_spec_id(compute_spec_id)
    else:
        raise ComputeSpecException(
            "An unexpected error occurred while activating the Compute Spec. "
            "Please see the response text for more information: \n"
            f"[{response.status_code}] {response.text}"
        )


def deactivate(
    compute_spec_id: Optional[UUID] = None, verbose: bool = False, cache: bool = True
):
    """Deactivate a Compute Spec ID.

    Args:
        compute_spec_id:    Compute Spec ID that shall be de-activated. If `None`, use the
            most recently used Compute Spec ID.
        verbose: If `True`, print more detailed information.
        cache:    If `True`, cache the Compute Spec ID after deactivation.
    """
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)
    session = get_oauth_session()

    url = _url_for_compute_command(cmd="/deploy/shutdown", id=compute_spec_id)
    response = exception_handled_request(session, url, "delete", payload={})

    if response.reason == "OK":
        if verbose:
            print(
                "\nSuccessfully shutdown the deployment of the Compute Spec "
                f"{compute_spec_id}!"
            )
        if cache:
            cache_compute_spec_id(compute_spec_id)
    else:
        raise ComputeSpecException(
            "An unexpected error occurred while deactivating the Compute Spec. "
            "Please see the response text for more information: \n"
            f"[{response.status_code}] {response.text}"
        )


def get_activation_status(compute_spec_id: Optional[UUID] = None) -> str:
    """Get the activation status of a Compute Spec.

    Args:
        compute_spec_id: ID of the Compute Spec that shall be queried. If `None`, use
            the most recently used Compute Spec ID.
    """
    details = get_status(compute_spec_id)
    return details.get("status", "unknown")


def get_status(
    compute_spec_id: Optional[UUID] = None,
) -> Dict[str, str]:
    """Get the detailed status of a Compute Spec.

    Args:
        compute_spec_id: ID of the Compute Spec that shall be queried. If `None`, use
            the most recently used Compute Spec ID.

    Returns:
        dict: A dict with keys `status` and `message`. The ´status` shows the activation
            status, e.g. `creating` or `running`. The `message` contains detail
            information. For example, if the Compute Spec isn't activating, the message
            might show that there is not enough hardware resource of a certain type.
    """
    validate_is_logged_in()

    if not compute_spec_id:
        compute_spec_id = load_cached_compute_spec_id(True)

    session = get_oauth_session()
    url = _url_for_compute_command(cmd="/deploy/status", id=compute_spec_id)

    try:
        response = exception_handled_request(session, url, "get")
    except RequestError as err:
        if err.status_code == 404:
            raise RequestError("Compute Spec not found", 404) from None
        elif err.status_code == 401:
            raise RequestError(
                "Not authorized to access Compute Spec's activation status", 401
            ) from None
        else:
            raise
    try:
        details = response.json()
    except json.decoder.JSONDecodeError as err:
        raise ComputeSpecException(
            "Could not decode response from the Compute Spec request. "
            f"Please check the raw error for more details: \n{str(err)}."
        )
    return details


def _unpack_compute_spec_row(cs: Dict):
    try:
        deploy_status = get_activation_status(cs["id"])
    except RequestError as err:
        if "Compute Spec not found" in str(err):
            deploy_status = "None"
        elif "Max retries exceeded with url" in str(err):
            deploy_status = "None"
        elif "Not authorized" in str(err):
            deploy_status = "None"
        else:
            raise

    id = cs.get("model", {}).get("id", "None")
    version = cs.get("model", {}).get("version", "None")

    resources = cs.get("resources", {})

    return {
        "id": cs.get("id", "None"),
        "model": f"{id}:{version}",
        "datasets": cs.get("datasets", "None"),
        "createdAt": cs.get("createdAt", "None"),
        "resources": resources,
        "deploy_status": deploy_status,
    }


def list_compute_specs(
    limit: Optional[int] = 10, active_only: bool = False
) -> List[dict]:
    """
    List most recent Compute Specs.

    Args:
        limit: The maximum number of Compute Specs to return. If None,
            return all.
        active_only: If `True`, only return Compute Specs that are active.

    Returns:
        List[dict]: A list of dictionaries containing the Compute Spec information."""
    from apheris_auth.config import settings

    session = get_oauth_session()
    url = f"{str(settings.API_ORCHESTRATOR_BASE_URL)}/v2/computespec"

    page_size = limit if limit else PAGE_SIZE
    payload: dict[str, Any] = {"page_size": page_size}

    if active_only:
        payload["status"] = ACTIVE_OR_TRANSITIONAL_STATES

    compute_specs = []
    try:
        response = exception_handled_request(session, url, "get", payload=payload)
        if response.reason == "OK":
            data = response.json()
            compute_specs.extend(data["data"])

            num_pages = data["meta"]["total_pages"]

            for page in range(1, num_pages):
                payload["page"] = page
                response = exception_handled_request(session, url, "get", payload=payload)
                compute_specs.extend(response.json()["data"])

                if limit and (len(compute_specs) >= limit):
                    break

            if limit:
                compute_specs = compute_specs[:limit]
            return compute_specs
        else:
            raise RequestError(
                "\nSomething went wrong: " + response.text, response.status_code
            )
    except RequestError as err:
        if 404 == err.status_code:
            raise RequestError("Compute Specs endpoint not found", 404) from None
        else:
            raise


def get_compute_spec_count(active_only: bool = False) -> int:
    """
    Get the number of compute specs.

    Args:
        active_only: If `True`, only return the number of active Compute Specs.

    Returns:
        int: Number of Compute Specs.
    """
    from apheris_auth.config import settings

    session = get_oauth_session()
    url = f"{str(settings.API_ORCHESTRATOR_BASE_URL)}/v2/computespec"

    payload: dict[str, Any] = {"page_size": 1}
    if active_only:
        payload["status"] = ACTIVE_OR_TRANSITIONAL_STATES

    try:
        response = exception_handled_request(session, url, "get", payload=payload)
        if response.reason == "OK":
            data = response.json()
            return data["meta"]["total_items"]
        else:
            raise RequestError(
                "\nSomething went wrong: " + response.text, response.status_code
            )
    except RequestError as err:
        if 404 == err.status_code:
            raise RequestError("Compute Specs endpoint not found", 404) from None
        else:
            raise


def get_compute_specs_details(
    compute_specs: Union[Dict[str, str], List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    """
    Parse the Compute Spec response from the API end point into the data required for
    the tabular format.

    Args:
        compute_specs: A list of dictionaries containing Compute Spec information. Can also be a
            single dictionary containing one Compute Spec.

    Returns:
        List[dict]: A list of dictionaries containing the Compute Spec information.
    """
    if not isinstance(compute_specs, list):
        compute_specs = [compute_specs]

    return [_unpack_compute_spec_row(c) for c in compute_specs]


def wait_until_running(
    compute_spec_id: Optional[UUID],
    check_interval: float = 10,
    timeout: Optional[float] = COMPUTE_SPEC_ACTIVATION_TIMEOUT,
) -> None:
    """
    Wait until a Compute Spec's activation status is `running`.

    Arguments:
        compute_spec_id: ID of the Compute Spec that we want to observe. If `None`,
            use the most recently used Compute Spec id.
        check_interval: Interval to check the status in seconds
        timeout: Timeout in seconds. If the target status is not reached within this time
            a TimeoutError is raised. If set to `None`, the function will not time out.
    """

    # Sanity check the format of the Compute Spec ID - will raise if invalid
    # Needed to prevent a hang from a 400 error below.
    if not isinstance(compute_spec_id, UUID):
        compute_spec_id = UUID(compute_spec_id)

    start = time.time()
    while timeout is None or time.time() - start <= timeout:
        try:
            deploy_status = get_activation_status(compute_spec_id)
        except (ComputeSpecException, RequestError) as err:
            if isinstance(err, RequestError) and err.status_code == 404:
                raise RequestError("Compute Spec not found", 404) from None

            time.sleep(check_interval)
            continue
        if deploy_status == "running":
            return
        time.sleep(check_interval)

    raise TimeoutError(f"Compute Spec is not running after {timeout}s.")


__all__ = [
    "ComputeSpec",
    "create",
    "create_from_args",
    "get",
    "activate",
    "deactivate",
    "get_status",
    "get_activation_status",
    "wait_until_running",
    "list_compute_specs",
    "get_compute_specs_details",
    "deactivate_all",
]
