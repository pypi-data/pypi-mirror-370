from datetime import datetime
from typing import List

import prettytable

from aphcli.api.utils.prettytable_helpers import safe_set_table_max_size


def _truncate_string(input_str: str, max_len: int) -> str:

    if max_len < 5:
        raise ValueError(
            "The maximum length must be >= 5 to allow one character either "
            "side of the ellipsis."
        )
    if len(input_str) <= max_len:
        return input_str
    else:
        # Account for the ...
        max_len -= 3

        return input_str[: max_len // 2] + "..." + input_str[-(max_len // 2) :]


def _dataset_string_from_list(dataset_list: List[str], dataset_max_len: int = 30) -> str:
    """
    Dataset list tends to cause overflow. Truncate both dataset names and the
    overall list.
    """

    if len(dataset_list) > 2:
        return f"{len(dataset_list)} datasets"
    else:
        dataset_list = [_truncate_string(c, dataset_max_len) for c in dataset_list]
        return ", ".join(dataset_list)


def _truncate_timestamp(timestamp: str):
    dt = datetime.fromisoformat(timestamp.rsplit(".")[0])
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _format_compute_specs(computespec_list: List[dict]) -> List[dict]:
    output = []
    for compute_spec in computespec_list:
        cs = compute_spec.copy()
        cs["datasets"] = _dataset_string_from_list(cs["datasets"])
        model = cs["model"]["id"]
        if version := cs["model"].get("version"):
            model += f":{version}"
        cs["model"] = _truncate_string(model, 30)

        cs["createdAt"] = _truncate_timestamp(cs["createdAt"])

        resources = cs["resources"]
        cs["resources"] = (
            "Orchestrator:\n"
            f" CPU: {resources['server']['cpu']}\n"
            f" GPU: {resources['server']['gpu']}\n"
            f" Memory: {resources['server']['memory']}MB\n"
            "Gateway:\n"
            f" CPU: {resources['clients']['cpu']}\n"
            f" GPU: {resources['clients']['gpu']}\n"
            f" Memory: {resources['clients']['memory']}MB"
        )

        output += [cs]

    return output


def generate_table(
    compute_spec_data: List[dict], verbose: bool
) -> prettytable.PrettyTable:
    compute_spec_data = _format_compute_specs(compute_spec_data)

    compute_specs_table = prettytable.PrettyTable()
    safe_set_table_max_size(compute_specs_table)

    if verbose:
        compute_specs_table.hrules = prettytable.ALL
        compute_specs_table.field_names = [
            "ID",
            "Created",
            "Model",
            "Datasets",
            "Resources",
            "Activation Status",
        ]

        # Make sure some columns have a sensible minimum width
        compute_specs_table._min_width = {"Resources": 20}

        compute_specs_table.align["Resources"] = "l"
        rows = [
            [
                c["id"],
                c["createdAt"],
                c["model"],
                c["datasets"],
                c["resources"],
                c["status"]["label"],
            ]
            for c in compute_spec_data
        ]
        alignment = {
            "ID": "l",
            "Created": "l",
            "Model": "l",
            "Datasets": "l",
            "Resources": "l",
            "Activation Status": "l",
        }
    else:
        compute_specs_table.field_names = [
            "ID",
            "Created",
            "Activation Status",
        ]
        rows = [
            [
                c["id"],
                c["createdAt"],
                c["status"]["label"],
            ]
            for c in compute_spec_data
        ]
        alignment = {"ID": "l", "Created": "l", "Activation Status": "l"}

    rows.sort(key=lambda x: x[1])

    compute_specs_table.add_rows(rows)
    compute_specs_table.align.update(alignment)

    return compute_specs_table


__all__ = ["generate_table"]
