import platform
import typing
from pathlib import Path
from typing import Dict, List, Optional

if typing.TYPE_CHECKING:
    from ..client import Primitive

from ..utils.daemons import Daemon
from .launch_agents import LaunchAgent
from .launch_service import LaunchService

HOME_DIRECTORY = Path.home()


class Daemons:
    def __init__(self, primitive) -> None:
        self.primitive: Primitive = primitive
        command_flags = ""

        if primitive.host != "api.primitive.tech":
            command_flags += f"--host {primitive.host} "
        if primitive.DEBUG:
            command_flags += "--debug "
        self.os_family = platform.system()

        match self.os_family:
            case "Darwin":
                self.daemons: Dict[str, Daemon] = {
                    "agent": LaunchAgent(
                        label="tech.primitive.agent",
                        command=f"{command_flags} agent",
                    ),
                    "monitor": LaunchAgent(
                        label="tech.primitive.monitor",
                        command=f"{command_flags} monitor",
                    ),
                }
            case "Linux":
                self.daemons: Dict[str, Daemon] = {
                    "agent": LaunchService(
                        label="tech.primitive.agent",
                        command=f"{command_flags} agent",
                    ),
                    "monitor": LaunchService(
                        label="tech.primitive.monitor",
                        command=f"{command_flags} monitor",
                    ),
                }
            case _:
                raise NotImplementedError(f"{self.os_family} is not supported.")

    def install(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name].install()
        else:
            return all([daemon.install() for daemon in self.daemons.values()])

    def uninstall(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name].uninstall()
        else:
            return all([daemon.uninstall() for daemon in self.daemons.values()])

    def stop(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name].stop()
        else:
            return all([daemon.stop() for daemon in self.daemons.values()])

    def start(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name].start()
        else:
            return all([daemon.start() for daemon in self.daemons.values()])

    def list(self) -> List[Daemon]:
        """List all daemons"""
        return list(self.daemons.values())

    def logs(self, name: str) -> None:
        self.daemons[name].view_logs()
