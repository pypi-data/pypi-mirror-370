import os
from copy import deepcopy
from typing import Dict, List, Optional, Union

from prettytable import PrettyTable
from pydantic import BaseModel


def table_from_collection_of_base_models(
    input_collection: List[BaseModel],
    field_names: Optional[List[str]] = None,
    index_column: Optional[str] = None,
    include_index: bool = False,
) -> PrettyTable:
    dict_collection = []
    for item in input_collection:
        dict_collection.append(item.model_dump(include=field_names))

    return table_from_collection_of_dicts(
        dict_collection,
        field_names=field_names,
        index_column=index_column,
        include_index=include_index,
    )


def table_from_collection_of_dicts(
    input_collection: Union[Dict[str, dict], List[dict]],
    field_names: Optional[List[str]] = None,
    index_column: Optional[str] = None,
    include_index: bool = False,
) -> PrettyTable:

    input_collection = deepcopy(input_collection)
    field_names = deepcopy(field_names)

    if isinstance(field_names, str):
        field_names = [field_names]

    if isinstance(input_collection, list):
        input_dict = {str(i): v for i, v in enumerate(input_collection)}
    else:
        input_dict = input_collection

    if field_names is None:
        # Need an ordered set, from Py3.7 dicts with None values are the closest proxy
        keys = {}
        for v in input_dict.values():
            keys.update(dict.fromkeys(v))
        field_names = list(keys)

    if include_index:
        field_names = ["_idx"] + field_names

    if index_column is not None:
        if index_column not in field_names:
            raise ValueError("Index column not found in list of field names")
        # Move the index column to the front of the list
        field_names.insert(0, field_names.pop(field_names.index(index_column)))

    table = PrettyTable(field_names=field_names)
    safe_set_table_max_size(table)

    for k, v in input_dict.items():
        row = []
        if include_index:
            row.append(k)

        row += [v.get(f, None) for f in field_names if f != "_idx"]
        table.add_row(row)

    return table


def safe_set_table_max_size(table: PrettyTable):
    """
    Set the maximum width of a prettytable to the terminal width.
    Safely handle the error from Inappropriate ioctl for device in non-interactive
    terminals. In this case, the table will be printed without any width constraints.
    """
    try:
        cols = os.get_terminal_size().columns
        table._max_table_width = cols
    except OSError:
        pass
