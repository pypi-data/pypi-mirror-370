from abc import ABC, abstractmethod
from enum import StrEnum

__all__ = [
    "StartupType",
    "BasePlatformService",
]


class StartupType(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"


class BasePlatformService(ABC):
    name: str
    title: str
    description: str
    startup: StartupType = StartupType.AUTO

    @abstractmethod
    def run(self) -> None:
        """Run whatever functions this service performs. Main, blocking, function."""

    @abstractmethod
    def started(self) -> None:
        """Signal the service has completed starting. Should be called by `run`
        when it finishes starting."""

    @abstractmethod
    def stopped(self) -> None:
        """Signal the service has completed stopping. Should be called by `run`
        when it finishes stopping."""

    @abstractmethod
    def stop(self) -> None:
        """Send signal to service to shutdown and return"""

    @classmethod
    @abstractmethod
    def execute(self) -> None:
        """Called to handle command line arguments and to handle being called by
        the platform to run the service. Blocking.

        Commandline Options:
            install: install the service, updating if already installed
            uninstall: uninstall the service, or do nothing if not installed
            start: start the service if installed
            stop: stop the service or do nothing if not running
        """
