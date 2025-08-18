import platform

from ._base import *

__version__ = "1.1.2"


if platform.system().casefold() == "windows":
    from ._windows import WindowsPlatformService as PlatformService  # noqa: F401
else:
    raise RuntimeError("Platform not supported.")
