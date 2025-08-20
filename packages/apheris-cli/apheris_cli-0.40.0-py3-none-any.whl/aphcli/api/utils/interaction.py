import numbers
from typing import Callable, Optional, Type, TypeVar, Union

from aphcli.api.datasets import list_datasets
from aphcli.api.models import (
    Model,
    get_models,
    indexed_model_list,
    indexed_model_list_to_table,
    models_from_response,
)
from aphcli.utils import validate_is_logged_in

T = TypeVar("T")


class LimitValidationError(ValueError):
    def __init__(
        self, *args: object, min_limit: numbers.Number, max_limit: numbers.Number
    ) -> None:
        super().__init__(*args)

        self.min_limit = min_limit
        self.max_limit = max_limit


class InteractiveInputError(ValueError):
    pass


def get_datasets_interactively(max_attempts: Optional[int] = None):

    validate_is_logged_in()
    print("## List of available datasets:\n")
    datasets = list_datasets()
    print(datasets)

    attempts = 0
    while True:
        attempts += 1
        if max_attempts is not None and attempts > max_attempts:
            raise InteractiveInputError(
                "Could not parse dataset selection, and exceeded "
                "the maximum number of attempts allowed."
            )

        answer = input(
            "\nPlease list the indices of all datasets that you want to include. "
            "Separate the numbers by comma, semicolon or space:\n:"
        )
        dataset_ids = answer.replace(";", " ").replace(",", " ").split()
        try:
            dataset_ids = [int(x) for x in dataset_ids]
            dataset_ids_unique = set(dataset_ids)

            if len(dataset_ids_unique) < len(dataset_ids):
                dataset_ids = list(dataset_ids_unique)
                print(
                    "Warning: the same dataset ID was provided multiple times. It will "
                    "only be used once."
                )

        except ValueError:
            print(
                "One or more of the provided indices is not a valid integer. Please "
                "provide the numerical index of the dataset(s) you wish to use."
            )
            continue

        has_error = False
        if len(dataset_ids) == 0:
            print("Please provide at least one dataset for this Compute Spec.")
            continue

        print(f"\nYou have selected following indices: {dataset_ids}")
        dataset_indices = sorted([r[0] for r in datasets.rows])
        for idx in dataset_ids:
            if idx not in dataset_indices:
                print(
                    f"A dataset with index {idx} does not exist. Please choose an index "
                    f"between {dataset_indices[0]} and {dataset_indices[-1]}."
                )
                has_error = True

        if not has_error:
            break

    selected_datasets = [r[1] for r in datasets.rows if r[0] in dataset_ids]
    print(f"\nThey correspond to following dataset IDs:\n {selected_datasets}\n")
    return selected_datasets


def get_model_interactively() -> Model:
    models = models_from_response(get_models())
    model_list = indexed_model_list(models)

    print("\n## List of available models:\n")
    table = indexed_model_list_to_table(model_list)
    print(table)

    while True:
        try:
            answer = input("\nPlease choose the index of your preferred model:\n:")
            idx = int(answer)

            _, model_id, model_version = model_list[idx]

            print(f"You chose '{model_id}:{model_version}'.")
            return Model(model_id, model_version)
        except ValueError:
            print("Please enter a valid integer.")
        except IndexError:
            print(
                f"Invalid index. Please choose a number between 0 and {len(models) - 1}."
            )


def type_from_optional(t: Type) -> Type:
    """
    Use introspection to extract the concrete type from an Optional field
    """
    if hasattr(t, "__origin__") and t.__origin__ is Union:
        return next(t for t in t.__args__ if not isinstance(t, type(None)))
    return t


def get_typed_response_interactively(
    field_name: str,
    msg: str,
    response_type: Type[T],
    max_attempts: Optional[int] = None,
    limit_validator: Optional[Callable] = None,
) -> Optional[T]:
    """
    Attempt to get a response of a given type from a user.

    If casting fails, will raise a value error, tell the user the value is invalid, and
    loop until a valid response is provided.

    Optionally accepts a callable `limit_validator` which should take the value, and
    if it's outside of allowed limits, raise a `LimitValidationError`.
    """
    attempts = 0
    while True:
        attempts += 1
        if max_attempts is not None and attempts > max_attempts:
            return None

        try:
            answer = input(msg)
            if response_type == bool:
                if answer.lower() in ("y", "yes", "true", "1"):
                    return True
                elif answer.lower() in ("", "n", "no", "false", "0"):
                    return False
                else:
                    raise ValueError("Invalid response")
            else:
                answer = response_type(answer)
                if limit_validator is not None:
                    # Will raise a ValueError if outside of limits
                    limit_validator(answer)
            return answer
        except (ValueError, LimitValidationError) as err:
            if response_type == bool:
                allowed_responses = "(y/N)"
            else:
                allowed_responses = f"valid {response_type.__name__}"

                if isinstance(err, LimitValidationError):
                    allowed_responses += f" between {err.min_limit} and {err.max_limit}"

            print(
                f"Invalid input for field `{field_name}`. Please enter a "
                f"{allowed_responses}."
            )
