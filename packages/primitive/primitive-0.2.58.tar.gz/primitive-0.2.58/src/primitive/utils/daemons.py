from abc import ABC, abstractmethod
from pathlib import Path


class Daemon(ABC):
    name: str
    label: str

    @property
    @abstractmethod
    def logs(self) -> Path:
        """Path to to agent or service logs"""
        pass

    @property
    @abstractmethod
    def file_path(self) -> Path:
        """Path to agent or service definition file"""
        pass

    @abstractmethod
    def install(self) -> bool:
        """Install the daemon"""
        pass

    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall the daemon"""
        pass

    @abstractmethod
    def start(self) -> bool:
        """Start the daemon"""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stop the daemon"""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the daemon is installed"""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Check if the daemon is active"""
        pass

    @abstractmethod
    def view_logs(self) -> None:
        """View the daemon logs"""
        pass
