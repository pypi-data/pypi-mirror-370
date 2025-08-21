"""This root level directives are imported from submodules. They are made
available here as well to keep the number of imports to a minimum for most
applications.
"""

import os

from .base import SquirroClient
from .document_uploader import DocumentUploader
from .exceptions import *  # noqa: F403
from .item_uploader import ItemUploader

__all__ = ["SquirroClient", "DocumentUploader", "ItemUploader"]

# Note: This variable is matched in the `make publish-client` sed command to set a static version for a release.
__SQUIRRO_VERSION__ = "3.14.0"
__version__ = __SQUIRRO_VERSION__
