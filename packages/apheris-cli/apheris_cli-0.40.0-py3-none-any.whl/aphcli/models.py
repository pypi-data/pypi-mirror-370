from typing import List, Optional, Tuple

import prettytable
import typer
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored
from typing_extensions import Annotated

from aphcli.api.pydantic_models import ModelVersion
from aphcli.api.utils import is_preview_enabled
from aphcli.api.utils.comms import RequestError
from aphcli.api.utils.prettytable_helpers import safe_set_table_max_size

from .api.models import (
    add_model,
    add_model_version,
    get_model,
    get_robot,
    list_model_versions,
    list_models,
)
from .utils import validate_is_logged_in

app = typer.Typer(no_args_is_help=True)


@app.command(
    help="List models that are available in the Apheris Registry. "
    "Note that only the 3 most recent versions of each model are shown."
)
def list():
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    try:
        table = list_models(to_table=True)
        safe_set_table_max_size(table)

        if len(table.rows) == 0:
            print("No models available.")
            return

        print(table)
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)


def _create_version_table(
    versions: List[ModelVersion], verbose: bool = False, max_versions_to_show: int = 3
) -> Tuple[prettytable.PrettyTable, Optional[str]]:
    """
    Create a prettytable with version information for a model.

    Args:
        versions: List of ModelVersion objects.
        verbose: If True, show all versions. If False, show only the first
            `max_versions_to_show` versions.
        max_versions_to_show: Number of versions to show if `verbose` is False.

    Returns:
        A tuple of the prettytable and a string with a message to show if not all
        versions are shown. If verbose is True, or all versions are shown, the
        message is None.
    """
    table = prettytable.PrettyTable(
        ["Version", "Created By", "Created At", "Digest", "Commit Hash"]
    )
    table.align.update(
        {
            "Commit Hash": "l",
            "Created At": "l",
            "Created By": "l",
            "Digest": "l",
            "Version": "l",
        }
    )
    safe_set_table_max_size(table)
    table._min_width = {"Version": 12}

    num_versions = len(versions)

    versions = versions if verbose else versions[:max_versions_to_show]

    for version in versions:
        if version.createdAt:
            created_at = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            created_at = ""
        table.add_row(
            [
                version.tag,
                version.createdBy,
                created_at,
                version.digest,
                version.commitHash[:6],  # Show the shortened commit hash
            ]
        )

    table_footer_string = None
    if (not verbose) and num_versions > max_versions_to_show:
        table.add_row(["..."] * 5)

        table_footer_string = (
            f"Showing {max_versions_to_show} of {num_versions} model versions."
            " To see all, use the `--verbose` flag"
        )

    return table, table_footer_string


@app.command(help="Get a model by its ID.")
def get(
    model_id: str = typer.Argument(
        ..., help="Apheris ID of a model. Can be obtained via Apheris UI or CLI."
    ),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show more detailed status information."),
    ] = False,
):
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    def label(txt: str) -> str:
        return colored(txt, attrs=["bold"])

    try:
        model = get_model(model_id)
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)
    except RequestError as err:
        if "Model not found" in str(err):
            print("Model not found.")
            raise typer.Exit(1)
        else:
            raise err

    print()
    print(f"{label('Model:'):<28s} {model_id}")
    print(f"{label('Name:'):<28s} {model.name}")
    print(f"{label('Created by:'):<28s} {model.createdBy}")
    if model.createdAt:
        print(
            f"{label('Created at:'):<28s} {model.createdAt.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    print(f"{label('OCI Repository:'):<28s} {model.ociRepository}")
    print(f"{label('Source Repository:'):<28s} {model.sourceRepositoryURL}")
    print(f"{label('Description:'):<28s} ")
    if model.card.get("details", {}).get("description") is not None:
        Console().print(Markdown(model.card["details"]["description"]))
    print()
    print("Versions:")

    table, table_footer_msg = _create_version_table(model.versions, verbose)
    print(table)

    if table_footer_msg:
        print(table_footer_msg)


@app.command(help="Get a list of all versions available for a given model.")
def list_versions(
    model_id: str = typer.Argument(
        ...,
        help="Apheris ID of a model. Can be obtained via Apheris UI or CLI.",
    ),
):
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    try:
        versions = list_model_versions(model_id)
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)
    except RequestError as err:
        if "Model not found" in str(err):
            print("Model not found.")
            raise typer.Exit(1)
        else:
            raise err
    table, _ = _create_version_table(versions, verbose=True)
    print(table)


@app.command(help="Add a new version to an existing model in the Apheris Registry.")
def add_version(
    model_id: str = typer.Argument(
        ...,
        help="Apheris ID of the model to which you want to add a version to. Obtainable via Apheris UI or CLI.",
    ),
    version: str = typer.Option(
        ...,
        help="Version number for the new model version. Needs to match the repo that holds the built image.",
    ),
    digest: str = typer.Option(
        ...,
        help="Digest for the new model. Needs to match the repository that holds the built image.",
    ),
    commit_hash: str = typer.Option(..., help="Hash for the new model version."),
    engine_version: str = typer.Option(
        ...,
        help=(
            "Engine version, for example `nvflare:2.6.0`. For information "
            "on supported engines and versions, please contact your Apheris "
            "representative."
        ),
    ),
):
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    try:
        result = add_model_version(model_id, version, digest, commit_hash, engine_version)
        if result:
            existed = (
                result.get("result")
                == "model version with same digest already exists, skipping"
            )
            if existed:
                print(
                    f"Version {version} was already present with the same digest {digest} in model {model_id}."
                )
            else:
                print(
                    f"Successfully added version {version} (digest {digest}, commit_hash: "
                    f"{commit_hash}, engine_version: {engine_version}) to model {model_id}."
                )
        else:
            print("Failed to add model version")
            raise typer.Exit(1)
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise typer.Exit(1)


@app.command(
    help="\b**Preview functionality:** please speak to your Apheris representative to enable this feature.\n"
    "Add a new model to the Apheris Registry.",
    hidden=(not is_preview_enabled()),
)
def add(
    model_id: str = typer.Argument(
        ...,
        help=(
            "ID of the model. Must be unique and contain only lowercase letters (a-z), "
            "digits (0-9), and single hyphens. "
            "No leading, trailing, or consecutive hyphens are allowed."
        ),
    ),
    model_name: str = typer.Option(
        ...,
        help="Name of the model. This is the human-readable name of the model.",
    ),
    source_repository_url=typer.Option(..., help="FQDN of the source repository."),
    model_description: str = typer.Option(
        default="",
        help="Longer description of the model. Markdown is supported. Max 5000 characters.",
    ),
    logo_url: str = typer.Option(
        default="",
        help="URL to the logo of the model or base64 encoded image.",
    ),
):
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    try:
        model = add_model(
            model_id, model_name, source_repository_url, model_description, logo_url
        )
        print(
            f"Successfully added new model with id: {model.id}, name: {model.name}, source repository: "
            f"{model.sourceRepositoryURL}."
        )
        print(
            f"Please use the provided docker repository '{model.ociRepository}' to push your model image."
        )
        print(
            "To have access to your robot account details to push model versions to the model's OCI repository, "
            "please use the `apheris models show-robot` command."
        )
        print(
            "Model versions can be added using the `apheris models add-version` command."
        )
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise typer.Exit(1)


@app.command(
    help="\b**Preview functionality:** please speak to your Apheris representative to enable this feature.\n"
    "Show user's robot account details to push model versions to the model's OCI repository.",
    hidden=(not is_preview_enabled()),
)
def show_robot():
    from apheris_auth.core.exceptions import Unauthorized

    validate_is_logged_in()

    try:
        robot = get_robot()
        print(
            "Successfully retrieved your robot account details:\n"
            f"- user: {robot.name}\n"
            f"- password: {robot.token}\n"
        )
        print(
            "Ensure you are logged in to the docker registry by using the following command:\n"
        )
        print(f"docker login -u='{robot.name}' -p='{robot.token}' quay.io")
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise typer.Exit(1)
