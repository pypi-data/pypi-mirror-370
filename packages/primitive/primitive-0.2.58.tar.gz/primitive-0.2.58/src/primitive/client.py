from typing import Optional

from gql import Client
from loguru import logger
from rich.logging import RichHandler
from rich.traceback import install

from .agent.actions import Agent
from .auth.actions import Auth
from .daemons.actions import Daemons
from .exec.actions import Exec
from .files.actions import Files
from .git.actions import Git
from .hardware.actions import Hardware
from .jobs.actions import Jobs
from .monitor.actions import Monitor
from .organizations.actions import Organizations
from .projects.actions import Projects
from .provisioning.actions import Provisioning
from .reservations.actions import Reservations
from .utils.config import read_config_file


class Primitive:
    def __init__(
        self,
        host: str = "api.primitive.tech",
        DEBUG: bool = False,
        JSON: bool = False,
        token: Optional[str] = None,
        transport: Optional[str] = None,
    ) -> None:
        self.host: str = host
        self.session: Optional[Client] = None
        self.DEBUG: bool = DEBUG
        self.JSON: bool = JSON

        # Enable tracebacks with local variables
        if self.DEBUG:
            install(show_locals=True)

        # Configure rich logging handler
        rich_handler = RichHandler(
            rich_tracebacks=self.DEBUG,  # Pretty tracebacks
            markup=True,  # Allow Rich markup tags
            show_time=self.DEBUG,  # Show timestamps
            show_level=self.DEBUG,  # Show log levels
            show_path=self.DEBUG,  # Hide source path (optional)
        )

        def formatter(record) -> str:
            match record["level"].name:
                case "ERROR":
                    return "[bold red]Error>[/bold red] {name}:{function}:{line} - {message}"
                case "CRITICAL":
                    return "[italic bold red]Critical>[/italic bold red] {name}:{function}:{line} - {message}"
                case "WARNING":
                    return "[bold yellow]Warning>[/bold yellow] {message}"
                case _:
                    return "[#666666]>[/#666666] {message}"

        logger.remove()
        logger.add(
            sink=rich_handler,
            format="{message}" if self.DEBUG else formatter,
            level="DEBUG" if self.DEBUG else "INFO",
            backtrace=self.DEBUG,
        )

        # Nothing will print here if DEBUG is false
        logger.debug("Debug mode enabled")

        # Generate full or partial host config
        if not token and not transport:
            # Attempt to build host config from file
            try:
                self.get_host_config()
            except KeyError:
                self.host_config = {}
        else:
            self.host_config = {"username": "", "token": token, "transport": transport}

        self.auth: Auth = Auth(self)
        self.organizations: Organizations = Organizations(self)
        self.projects: Projects = Projects(self)
        self.jobs: Jobs = Jobs(self)
        self.files: Files = Files(self)
        self.reservations: Reservations = Reservations(self)
        self.hardware: Hardware = Hardware(self)
        self.agent: Agent = Agent(self)
        self.git: Git = Git(self)
        self.daemons: Daemons = Daemons(self)
        self.exec: Exec = Exec(self)
        self.provisioning: Provisioning = Provisioning(self)
        self.monitor: Monitor = Monitor(self)

    def get_host_config(self):
        self.full_config = read_config_file()
        self.host_config = self.full_config.get(self.host)

        if not self.host_config:
            raise KeyError(f"Host {self.host} not found in config file.")
