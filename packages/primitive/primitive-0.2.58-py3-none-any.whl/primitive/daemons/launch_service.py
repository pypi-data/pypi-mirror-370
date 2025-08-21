import configparser
import os
import subprocess
from pathlib import Path

from loguru import logger

from ..utils.daemons import Daemon

HOME_DIRECTORY = Path.home()


class LaunchService(Daemon):
    def __init__(self, label: str, command: str):
        self.label = label
        self.name = label.split(".")[-1]
        self.command = command

    @property
    def service_name(self) -> str:
        return f"{self.label}.service"

    @property
    def file_path(self) -> Path:
        return Path(HOME_DIRECTORY / ".config" / "systemd" / "user" / self.service_name)

    @property
    def logs(self) -> Path:
        return Path(HOME_DIRECTORY / ".cache" / "primitive" / f"{self.label}.log")

    def stop(self) -> bool:
        try:
            if self.is_active():
                stop_existing_service = f"systemctl --user stop {self.service_name}"
                subprocess.check_output(
                    stop_existing_service.split(" "), stderr=subprocess.DEVNULL
                )
                logger.info(f":white_check_mark: {self.label} stopped successfully!")
            return True
        except subprocess.CalledProcessError as exception:
            if exception.returncode == 4:
                logger.debug(f"{self.label} is not running or does not exist.")
                return True
            else:
                logger.error(f"Unable to stop {self.label}, {exception.returncode}")
                logger.error(exception)
                return False

    def start(self) -> bool:
        try:
            start_new_service = f"systemctl --user start {self.service_name}"
            subprocess.check_output(start_new_service.split(" "))
            logger.info(f":white_check_mark: {self.label} started successfully!")
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to start {self.label}")
            logger.error(exception)
            return False

    def disable(self) -> bool:
        try:
            if self.is_installed():
                disable_existing_service = (
                    f"systemctl --user disable {self.service_name}"
                )
                subprocess.check_output(
                    disable_existing_service.split(" "), stderr=subprocess.DEVNULL
                )
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to disable {self.label}")
            logger.error(exception)
            return False

    def enable(self) -> bool:
        try:
            enable_service = f"systemctl --user enable {self.service_name}"
            subprocess.check_output(
                enable_service.split(" "), stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to enable {self.label}")
            logger.error(exception)
            return False

    def verify(self) -> bool:
        systemctl_check = (
            f"systemctl --user show {self.service_name} -p CanStart --value"
        )
        try:
            output = (
                subprocess.check_output(systemctl_check.split(" ")).decode().strip()
            )
            if output == "no":
                raise Exception(f"{systemctl_check} yielded {output}")
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to verify {self.label}")
            logger.error(exception)
            return False

    def view_logs(self) -> None:
        follow_logs = f"tail -f -n +1 {self.logs}"
        os.system(follow_logs)

    def populate(self) -> bool:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        if self.file_path.exists():
            self.file_path.unlink()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        config = configparser.ConfigParser()
        config.optionxform = str  # type: ignore

        config["Unit"] = {
            "Description": "Primitive Agent",
            "After": "network.target",
        }

        # this is here so that it won't break on primitive's init
        # do not move
        result = subprocess.run(["which", "primitive"], capture_output=True)
        if result.returncode == 0:
            self.executable = result.stdout.decode().rstrip("\n")
        else:
            raise Exception("primitive binary not found")

        config["Service"] = {
            "ExecStart": f'/bin/sh -lc "{self.executable} {self.command}"',
            "Restart": "always",
            "StandardError": f"append:{self.logs}",
            "StandardOutput": f"append:{self.logs}",
        }

        config["Install"] = {
            "WantedBy": "default.target",
        }

        try:
            with open(self.file_path, "w") as service_file:
                config.write(service_file)
        except IOError as exception:
            print(f"populate_service_file: {exception}")

        self.file_path.chmod(0o644)
        return self.verify()

    def create_stdout_file(self) -> bool:
        try:
            if not self.logs.exists():
                self.logs.parent.mkdir(parents=True, exist_ok=True)
                self.logs.touch()

            return True
        except Exception as e:
            logger.error(
                f"Unable to create log file at {self.logs} for daemon {self.label}"
            )
            logger.error(e)
            return False

    def delete_stdout_file(self) -> bool:
        try:
            if self.logs.exists():
                self.logs.unlink()

            return True
        except Exception as e:
            logger.error(
                f"Unable to delete log file at {self.logs} for daemon {self.label}"
            )
            logger.error(e)
            return False

    def delete_service_file(self) -> bool:
        try:
            if self.file_path.exists():
                self.file_path.unlink()

            return True
        except Exception as e:
            logger.error(
                f"Unable to delete service file at {self.file_path} for daemon {self.label}"
            )
            logger.error(e)
            return False

    def install(self) -> bool:
        return all(
            [
                self.stop(),
                self.disable(),
                self.create_stdout_file(),
                self.populate(),
                self.enable(),
                self.start(),
            ]
        )

    def uninstall(self) -> bool:
        return all(
            [
                self.stop(),
                self.disable(),
                self.delete_service_file(),
                self.delete_stdout_file(),
            ]
        )

    def is_active(self) -> bool:
        try:
            is_service_active = (
                f"systemctl --user show {self.service_name} -p ActiveState --value"
            )
            output = (
                subprocess.check_output(is_service_active.split(" ")).decode().strip()
            )
            return output == "active"
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to check if {self.label} is active")
            logger.error(exception)
            return False

    def is_installed(self) -> bool:
        try:
            is_service_active = (
                f"systemctl --user show {self.service_name} -p UnitFileState --value"  # noqa
            )
            output = (
                subprocess.check_output(is_service_active.split(" ")).decode().strip()
            )
            return output == "enabled"
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to check if {self.label} is enabled")
            logger.error(exception)
            return False
