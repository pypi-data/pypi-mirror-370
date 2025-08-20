import warnings
from typing import Dict, List, Optional, Union

import prettytable
from apheris_auth import login, logout

import aphcli.api.compute as compute_api
from aphcli.api.datasets import list_datasets
from aphcli.api.job import list_jobs
from aphcli.api.models import list_models
from aphcli.api.utils import ApherisDeprecationWarning
from aphcli.api.utils.compute_spec_formatting import generate_table

warnings.simplefilter("always", ApherisDeprecationWarning)


def list_compute_specs(
    limit: Optional[int] = 10, to_table: bool = True, verbose: bool = False
) -> Union[prettytable.PrettyTable, List[Dict[str, str]]]:
    """
    Convenience function to list the `limit` most recent Compute Specs and optionally
    output as a table.

    Arguments:
        limit: The number of most recent Compute Specs to list. If None, all compute
            specs are listed. Defaults to 10.
        to_table: Whether to output the results as a pretty table. Defaults to True.
        verbose: Whether to include all details in the table. Defaults to False.

    Returns:
        - If `to_table` is True, a `prettytable.PrettyTable` is returned.
        - If `to_table` is False, a list of Dictionaries is returned. \
        In future versions this will return a list of `ComputeSpec` objects.
    """
    if limit is not None and (not isinstance(limit, int) or limit < 1):
        raise ValueError("The limit must either be None or an integer >= 1")

    compute_specs = compute_api.list_compute_specs(limit=limit)

    if to_table:
        return generate_table(compute_specs, verbose)
    else:
        return compute_specs


__all__ = [
    "list_datasets",
    "list_compute_specs",
    "list_jobs",
    "list_models",
    "login",
    "logout",
]
