import json
import re

import prettytable
import typer
from apheris_auth.core.exceptions import Unauthorized
from typing_extensions import Annotated

from aphcli.api.utils.comms import RequestError
from aphcli.api.utils.prettytable_helpers import safe_set_table_max_size

from .api.datasets import get_description, get_policy, list_datasets
from .describe_utils import format_description
from .utils import validate_is_logged_in

app = typer.Typer(no_args_is_help=True)


@app.command(help="List all datasets that you have access to.")
def list():
    validate_is_logged_in()
    try:
        datasets_table = list_datasets(to_table=True)
        safe_set_table_max_size(datasets_table)
        print(datasets_table)
    except Unauthorized:
        print("You are not logged in. Please log in.")
        raise typer.Exit(1)


@app.command(help="Show information on a single dataset.")
def describe(
    dataset_id: Annotated[
        str,
        typer.Argument(
            help="ID of the dataset to show information on.",
        ),
    ],
):
    validate_is_logged_in()

    error_message_403 = (
        "You are not authorized. Please log in or check your permissions with "
        "`apheris datasets list` to confirm you have access to this dataset."
    )
    try:
        description = get_description(dataset_id)
    except RequestError as err:
        if err.status_code == 403:
            print(error_message_403)
            raise typer.Exit(1)
        elif err.status_code == 404:
            print("Dataset not found.")
            raise typer.Exit(1)
        else:
            raise

    try:
        policy = get_policy(dataset_id)
    except RequestError as err:
        if err.status_code == 403:
            print(error_message_403)
            raise typer.Exit(1)
        elif err.status_code == 404:
            policy = None
        else:
            raise

    print(format_description(description, policy))


@app.command(help="Show the asset policy of a dataset that you have access to.")
def policy(
    dataset_id: Annotated[
        str,
        typer.Argument(
            help="ID of the dataset to get the policy for.",
        ),
    ],
):
    validate_is_logged_in()

    try:
        p = get_policy(dataset_id)
    except RequestError as err:
        if err.status_code == 403:
            print("You are not authorized. Please log in or check your permissions.")
            raise typer.Exit(1)
        elif err.status_code == 404:
            p = r"No Asset Policy was found that grants access to the dataset"
            if re.compile(p).findall(err.message):
                print("No models allowed.")
                raise typer.Exit(0)
            elif f"Dataset with the slug {dataset_id} is not found." in err.message:
                print("Dataset not found.")
                raise typer.Exit(1)
            else:
                raise
        else:
            raise

    [x.pop("image") for x in p["models"] if "image" in x]  # Don't show docker image hash

    print("\n# Allowed models:")
    print(str(prettytable.from_json(json.dumps([["id", "version"]] + p["models"]))))

    is_statistics_available = any(
        [
            x["id"] in ["apheris-statistics", "apheris-regression-models"]
            for x in p["models"]
        ]
    )
    if is_statistics_available:
        # These elements have variable structure and can have 3 layers of nesting.
        # So we don't "beautify" them.
        print("\n# Statistics permissions:")
        print(json.dumps(p["permissions"], indent=2))
        print("\n# Statistics privacy policies:")
        print(json.dumps(p["privacy"], indent=2))
