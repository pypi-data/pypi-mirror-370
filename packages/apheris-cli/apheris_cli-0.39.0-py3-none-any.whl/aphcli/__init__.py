import warnings

from .api.utils import ApherisDeprecationWarning
from .version import __version__  # noqa

warnings.simplefilter("always", ApherisDeprecationWarning)
