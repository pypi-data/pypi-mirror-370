from datetime import datetime
from typing import List, Optional, Union

from apheris_auth.core.api import get_client
from prettytable import PrettyTable

from aphcli.utils import get_oauth_session, validate_is_logged_in

from .utils.comms import exception_handled_request


def _create_dataset_table(rows: List[List[Union[int, str]]]) -> PrettyTable:
    table = PrettyTable()
    table.field_names = ["idx", "dataset_id", "organization", "data custodian"]
    table.add_rows(rows)
    table.align.update(
        {"idx": "r", "dataset_id": "l", "organization": "l", "data custodian": "l"}
    )
    return table


def list_datasets(
    n: Optional[int] = None,
    to_table: bool = True,
) -> Union[PrettyTable, List[dict]]:
    """
    List the `n` most recently updated remote datasets.

    Args:
        n: number of remote datasets to list. If None, list all. Default: None
        to_table: If True, a prettytable.PrettyTable is returned. If False, a list of
            Dictionaries will be returned.

    Returns:
        If `to_table` is True, a `prettytable.PrettyTable` is returned. The datasets
            are sorted by their updated_at time, starting from the most recent one.
            most recently updated remote datasets is returned. If `n` is provided, will
            return the `n` most recent rows.
        If `to_table` is False, a list of Dictionaries is returned. The datasets
            are sorted by their updated_at time, starting from the most recent one.
            most recently updated remote datasets is returned. If `n` is provided, will
            return the `n` most recent rows.
    """
    client = get_client()
    datasets = client.get_datasets()

    def date_sort(x, key):
        return datetime.strptime(x[key], "%Y-%m-%dT%H:%M:%S.%fZ")

    if to_table:
        rows = [
            [
                x["slug"],
                x["organization"],
                x["owner"]["full_name"],
                x["updated_at"],
            ]
            for x in datasets
        ]
        rows.sort(key=lambda x: date_sort(x, 3))

        # Now remove the updated_at column as it's only used for sorting
        if n is not None:
            rows = rows[-n:]

        rows = [[i] + r[:3] for i, r in enumerate(rows)]
        return _create_dataset_table(rows)
    else:
        datasets = sorted(datasets, key=lambda x: date_sort(x, "updated_at"))
        if n is not None:
            datasets = datasets[-n:]
        return datasets


def get_policy(dataset_id: str) -> dict:
    """
    Get the asset policy of a dataset you are granted access to.

    Args:
        dataset_id: ID of the dataset to get the policy for

    Returns:
        dictionary with asset policy information
    """
    from apheris_auth.config import settings

    validate_is_logged_in()
    session = get_oauth_session()
    url = f"{settings.API_BASE_URL}/datastore/asset_policy/settings/{dataset_id}"

    response = exception_handled_request(session, url, "get", payload={})
    return response.json()


def get_description(dataset_id: str):
    """
    Get the description of a dataset. The description is a dictionary with information
    such as the dataset's name, description, and the user that registered it.

    Args:
        dataset_id: ID of the dataset to get the description for

    Returns:
        dictionary with description information
    """
    from apheris_auth.config import settings

    validate_is_logged_in()

    session = get_oauth_session()
    url = f"{settings.API_DATASETS_URL}{dataset_id}/"

    response = exception_handled_request(session, url, "get", payload={})
    return response.json()
