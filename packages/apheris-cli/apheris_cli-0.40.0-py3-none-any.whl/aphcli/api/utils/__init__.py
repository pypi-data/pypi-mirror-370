import os
from functools import wraps


class ComputeSpecException(Exception):
    pass


class ApherisDeprecationWarning(DeprecationWarning):
    pass


class ModelException(Exception):
    pass


class PreviewFeatureException(Exception):
    pass


def is_preview_enabled():
    """
    Check if the APH_CLI_PREVIEW environment variable is set to enable preview features.
    """
    val = os.getenv("APH_CLI_PREVIEW")
    return val is not None and val.lower() in ("true", "t", "1", "yes", "y")


def mark_preview():
    """
    A decorator to wrap preview functions and raise an exception if the preview feature is not enabled.

    Raises:
        PreviewFeatureException: If preview mode is not enabled.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_preview_enabled():
                raise PreviewFeatureException(
                    "This preview feature is not currently enabled in your environment. Please contact your "
                    "Apheris representative for more information."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
