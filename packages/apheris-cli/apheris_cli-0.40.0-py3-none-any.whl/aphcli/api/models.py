from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from prettytable import PrettyTable

from ..utils import get_oauth_session, validate_is_logged_in
from .pydantic_models import AddModel, ModelDetails, ModelVersion, RobotDetails
from .utils import ComputeSpecException, ModelException, mark_preview
from .utils.comms import RequestError, exception_handled_request


@dataclass
class Model:
    id: Optional[str]
    version: Optional[str]

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {"id": self.id, "version": self.version}

    @staticmethod
    def from_dict(json_data: Optional[Dict[str, Any]]) -> Optional["Model"]:
        if json_data is None:
            return None
        if not isinstance(json_data, dict) or not set(json_data.keys()) == {
            "id",
            "version",
        }:
            raise ComputeSpecException(
                "JSON data doesn't appear to describe a Model object. It should be a dict"
                " with 2 fields, 'id' and 'version'."
            )
        m = Model(None, None)
        m._populate_from_dict(json_data)
        return m

    def _populate_from_dict(self, json_data: Dict[str, str]):
        self.id = json_data.get("id")
        self.version = json_data.get("version")

    def __eq__(self, __value: object) -> bool:
        if not hasattr(__value, "to_dict"):
            return False
        return self.to_dict() == __value.to_dict()


def _get_model_registry_url():
    from apheris_auth.config import settings

    return f"{str(settings.API_ORCHESTRATOR_BASE_URL)}"


def get_models() -> dict:
    """
    Returns a dictionary with detailed information on models available in the model
    registry. This returns the raw response from the Apheris Registry API and should be
    processed using `models_from_response`.

    Returns:
        A dictionary containing detailed information on models in the Registry.

    """
    validate_is_logged_in()
    session = get_oauth_session()

    url = f"{_get_model_registry_url()}/models"
    response = exception_handled_request(session, url, "get")
    response.raise_for_status()

    return response.json()


def models_from_response(response: dict) -> List[Dict[str, str]]:
    """
    Parses the raw data from the models response and extracts the list of models and
    available versions.

    Args:
        response: The raw response from the API.

    Returns:
        A list of dictionaries, each containing the model ID and version.
    """
    models = []

    for model in response["data"]:
        if len(model["recentVersions"]) == 0:
            models.append({"id": model["id"], "version": "-"})
        else:
            for version in model["recentVersions"]:
                tag = version["tag"]
                models.append({"id": model["id"], "version": tag})

    return models


def list_models(to_table: bool = True) -> Union[PrettyTable, List[Dict[str, str]]]:
    """
    Convenience function to query the model list and parse the response in one call.

    Args:
        to_table: If True, a prettytable.PrettyTable is returned. If False, a list of
            Dictionaries will be returned.

    Returns:
        - If `to_table` is True, a `prettytable.PrettyTable` is returned.
        - If `to_table` is False, a list of Dictionaries is returned.
    """
    validate_is_logged_in()
    response = get_models()
    models = models_from_response(response)

    if to_table:
        rows = indexed_model_list(models)
        table = indexed_model_list_to_table(rows)
        return table
    else:
        return models


def indexed_model_list(models: List[Dict[str, str]]) -> List[Tuple[int, str, str]]:
    """
    Convert the list of models to a tabular format for interaction

    Args:
        models: A list of dictionaries containing model information.

    Returns:
        A list of tuples containing the index, model ID, and model version.
    """
    return [(i, m["id"], m["version"]) for i, m in enumerate(models)]


def indexed_model_list_to_table(rows: List[Tuple[int, str, str]]) -> PrettyTable:
    """
    Convert the list of models to a prettytable for interaction.

    Assumes the input is a list of tuples containing the index, model ID, and model,
    such as that provided by `indexed_model_list`

    Args:
        rows: A list of tuples containing the index, model ID, and model version.

    Returns:
        A prettytable containing the model information.
    """
    table = PrettyTable(field_names=["idx", "name", "version"])
    table.add_rows(rows)

    table.align.update({"idx": "r", "name": "l", "version": "l"})
    return table


def get_model(model_id: str) -> ModelDetails:
    """
    Returns a dictionary with detailed information on a specific model in the model
    registry.

    Args:
        model_id: The ID of the model to get.

    Returns:
        A `ModelDetails` object containing detailed information on the model.
    """
    validate_is_logged_in()
    session = get_oauth_session()

    url = f"{_get_model_registry_url()}/models/{model_id}"
    try:
        response = exception_handled_request(session, url, "get")
    except RequestError as err:
        if err.status_code == 404:
            raise RequestError("Model not found", 404) from None
        elif err.status_code == 401:
            raise RequestError("Not authorized to access model details", 401) from None
        else:
            raise

    response.raise_for_status()

    response_json = response.json()

    if "data" not in response_json:
        raise RuntimeError("Model payload is malformed.")

    model = ModelDetails.model_validate(response_json["data"])
    model.versions.sort(key=lambda x: x.tag, reverse=True)
    return model


def add_model_version(
    model_id: str,
    version: str,
    digest: str,
    commit_hash: str,
    engine_version: str,
) -> Dict[str, Any]:
    """
    Adds a new version to an existing model in the Apheris Registry.

    Args:
        model_id: The ID of the model to add a version to.
        version: The version tag for the new model version.
        digest: The digest of the model.
        commit_hash: The commit hash associated with this model version.
        engine_version: Engine version, for example `nvflare:2.6.0`. For information on
            supported engines and versions, please contact your Apheris representative.

    Returns:
        A dictionary containing the response from the API.

    Raises:
        ComputeSpecException: If there's an error in adding the model version.
    """
    validate_is_logged_in()
    session = get_oauth_session()

    url = f"{_get_model_registry_url()}/models/{model_id}/versions"

    try:
        data = {
            "tag": version,
            "digest": digest,
            "commitHash": commit_hash,
            "engineVersion": engine_version,
        }

        response = exception_handled_request(session, url, "post", json=data)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        raise ComputeSpecException(f"Failed to add model version: {str(e)}")


def list_model_versions(model_id: str) -> List[ModelVersion]:
    """
    Convenience function to list all the versions of a model.

    Args:
        model_id: The ID of the model whose versions to list.

    Returns:
        A list of`ModelVersion` objects
    """
    model_data = get_model(model_id)
    return model_data.versions


@mark_preview()
def add_model(
    model_id: str,
    model_name: str,
    source_repository_url: str,
    model_description: str = "",
    logo_url: str = "",
) -> ModelDetails:
    """
    Adds a new model to the Apheris Registry.

    Args:
        model_id: The ID of the new model.
        model_name: The Name of the new model.
        source_repository_url: The URL of the source repository.
        model_description: The description of the model.
        logo_url: The URL of the logo or base64 encoded image.
    Returns:
        A `ModelDetails` object containing detailed information on the model.

    Raises:
        ModelException: If there's an error in adding the new model.
    """
    validate_is_logged_in()
    session = get_oauth_session()

    payload = AddModel(
        id=model_id,
        name=model_name,
        description=model_description,
        source_repository_url=source_repository_url,
        logo_url=logo_url,
    ).model_dump_json(
        by_alias=True,
        exclude_unset=True,
        exclude_defaults=True,
        exclude_none=True,
    )
    url = f"{_get_model_registry_url()}/models"

    try:
        response = exception_handled_request(session, url, "post", payload=payload)
    except RequestError as err:
        if err.status_code == 403:
            raise RequestError(
                "Not authorized to add model. "
                "Please ensure you have the model_manager role.",
                403,
            ) from None
        else:
            raise ModelException(f"Failed to add new model: {str(err)}")

    try:
        return ModelDetails.model_validate(response.json()["data"])
    except Exception:
        raise ModelException(
            f"Model add request succeeded, failed to parse response data: '{response.text}'"
        )


@mark_preview()
def get_robot() -> RobotDetails:
    """
    Returns the user's robot account to use for pushing model images to the model's
    OCI repository.

    Returns:
        A `RobotDetails` object containing detailed information on the robot.
    """
    validate_is_logged_in()
    session = get_oauth_session()

    url = f"{_get_model_registry_url()}/me/robot"
    try:
        response = exception_handled_request(session, url, "get")
    except RequestError as err:
        if err.status_code == 403:
            raise RequestError(
                "Not authorized to get the robot details. "
                "Please ensure you have the model_manager role.",
                403,
            ) from None
        else:
            raise

    try:
        return RobotDetails.model_validate(response.json()["data"])
    except Exception:
        raise RuntimeError(f"Robot details payload is malformed: '{response.text}'.")
