# ruff: noqa: F403,F405

from . import _stardust
from ._stardust import sum_as_string

__version__ = "0.3.380"
__author__ = "beyChill"
__description__ = "Capture video streams"
__repo_name__ = "helio"
__repo_url__ = "https://github.com/beyChill/helio"
__repo_path__ = "beyChill/helio"


__all__ = ["sum_as_string"]
__all__ += _stardust.__all__