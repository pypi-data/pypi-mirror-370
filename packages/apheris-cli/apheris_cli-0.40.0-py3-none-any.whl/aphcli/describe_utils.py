import json
from collections import defaultdict
from datetime import datetime
from typing import Optional

from termcolor import colored


def _dump_dict(d: Optional[dict], display: str) -> str:
    if d:
        d_str = json.dumps(d, indent=2)
        d_str = "\t\t" + d_str.replace("\n", "\n\t\t")
        return f"  \t- {display}:\n{d_str}\n"
    return ""


def _format_dataset_permission(policy: Optional[dict] = None) -> str:
    """
    Formats a "policy" dictionary into a human-readable string.

    Args:
    policy: A dictionary representing the policy to be formatted. Its format needs to
        match the format of policies that are provided by `get_policy`.

    Returns:
    str: A human-readable string representation of the policy.
    """
    p = {"models": {}} if policy is None else policy

    model_versions = defaultdict(list)
    for m in p["models"]:
        model_versions[m["id"]].append(m["version"])

    permission_info = ""
    if len(model_versions) == 0:
        permission_info += "You don't have permissions to use any model."
    for model_id in model_versions:
        permission_info += f"* {model_id}\n"

        if model_versions[model_id] == ["*"]:
            version_str = "all"
        else:
            version_str = ", ".join(model_versions[model_id])
        permission_info += f"  \t- Version: {version_str}\n"

        if model_id == "apheris-statistics":
            permission_info += _dump_dict(p["permissions"], "permissions")
            permission_info += _dump_dict(p["privacy"], "privacy")
    return permission_info


def _get_dummy_information(description: dict) -> str:
    dummy_data_files = description.get("data", {}).get("dummy_data", {}).get("files", {})
    if not isinstance(dummy_data_files, dict):
        dummy_data_files = {}
    if len(dummy_data_files) == 0:
        dummy_info = "no dummy data available"
    else:
        dummy_info = list(dummy_data_files)[0]
    return dummy_info


def _reformat_datetime(date_time: str) -> str:
    dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _get_headers(description: dict) -> str:
    header = ""
    given_name = description.get("created_by", {}).get("givenName", None)
    family_name = description.get("created_by", {}).get("familyName", None)
    org_name = description.get("created_by", {}).get("orgName", None)
    updated_at = description.get("updated_at", None)
    created_at = description.get("created_at", None)

    if given_name and family_name:
        header += f"Created by:   {given_name} {family_name}\n"
    if org_name:
        header += f"Organization: {org_name}\n"
    if updated_at:
        header += f"Updated:      {_reformat_datetime(updated_at)}\n"
    if created_at:
        header += f"Created:      {_reformat_datetime(created_at)}\n\n"

    return header


def _get_details(description: dict) -> str:
    s = f"ID:          {description['slug']}\n"
    s += f"Name:        {description['name']}\n"

    description_str = description.get("description", None)
    if description_str:
        s += f"Description: {description_str}\n\n"

    return s


def _get_real_data_info(description: dict) -> str:
    d = description
    gw_name = d.get("gateway", {}).get("name", None)
    paths = list(d.get("data", {}).get("real_data", {}).get("files", {}).values())
    path = paths[0] if len(paths) > 0 else None

    s = ""
    if gw_name:
        s += f"Gateway: {gw_name}\n"
    if path:
        s += f"Path:    {path}\n\n"

    return s


def format_description(description: dict, policy: Optional[dict] = None) -> str:
    """
    Take a dataset description and dataset policies and format them into a human-readable
    string.

    Args:
        description: A raw description, as provided by `get_description`.
        policy: A dictionary representing the policy to be formatted. Its format needs to
            match the format of policies that are provided by `get_policy`.

    Returns:
        str: A human-readable description of a dataset.
    """
    permission_info = _format_dataset_permission(policy)

    dummy_info = _get_dummy_information(description)
    header_info = _get_headers(description)
    details_info = _get_details(description)
    real_data_ino = _get_real_data_info(description)

    def label(txt: str) -> str:
        return colored(txt, attrs=["bold"])

    s = (
        f"\n{label(description['name'])}\n"
        f"{header_info}\n"
        f"{label('1. Details')}\n"
        f"{details_info}"
        f"{label('2. Dummy data')}\n"
        f"{dummy_info}\n\n"
        f"{label('3. Real data')}\n"
        f"{real_data_ino}\n"
        f"{label('4. Your permissions')}\n"
        f"{permission_info}\n"
    )
    return s
