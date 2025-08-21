import os
import subprocess
from pathlib import Path

from loguru import logger

from ..utils.daemons import Daemon

HOME_DIRECTORY = Path.home()
CURRENT_USER = str(HOME_DIRECTORY.expanduser()).lstrip("/Users/")


class LaunchAgent(Daemon):
    def __init__(self, label: str, command: str):
        self.label = label
        self.name = label.split(".")[-1]
        self.command = command

    @property
    def file_path(self) -> Path:
        return Path(HOME_DIRECTORY / "Library" / "LaunchAgents" / f"{self.label}.plist")

    @property
    def logs(self) -> Path:
        return Path(HOME_DIRECTORY / "Library" / "Logs" / f"{self.label}.log")

    def stop(self, unload: bool = True) -> bool:
        try:
            stop_existing_process = f"launchctl stop {self.label}"
            subprocess.check_output(
                stop_existing_process.split(" "), stderr=subprocess.DEVNULL
            )
            logger.info(f":white_check_mark: {self.label} stopped successfully!")
            if unload:
                self.unload()  # Need to unload with KeepAlive = true or else launchctl will try to pick it up again
            return True
        except subprocess.CalledProcessError as exception:
            if exception.returncode == 3:
                logger.debug(f"{self.label} is not running or does not exist.")
                return True
            else:
                logger.error(f"Unable to stop {self.label}, {exception.returncode}")
                logger.error(exception)
                return False

    def start(self, load: bool = True) -> bool:
        if load:
            self.load()
        try:
            start_new_agent = f"launchctl start {self.label}"
            subprocess.check_output(
                start_new_agent.split(" "), stderr=subprocess.DEVNULL
            )
            logger.info(f":white_check_mark: {self.label} started successfully!")
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to start {self.label}")
            logger.error(exception)
            return False

    def unload(self) -> bool:
        try:
            remove_existing_agent = f"launchctl unload -w {self.file_path}"
            subprocess.check_output(
                remove_existing_agent.split(" "), stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to unload {self.label}")
            logger.error(exception)
            return False

    def load(self) -> bool:
        try:
            load_new_plist = f"launchctl load -w {self.file_path}"
            subprocess.check_output(
                load_new_plist.split(" "), stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to load {self.label}")
            logger.error(exception)
            return False

    def verify(self) -> bool:
        plutil_check = f"plutil -lint {self.file_path}"
        try:
            subprocess.check_output(plutil_check.split(" "), stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to verify {self.label}")
            logger.error(exception)
            return False

    def view_logs(self) -> None:
        follow_logs = f"tail -f -n +1 {self.logs}"
        os.system(follow_logs)

    def populate(self) -> bool:
        self.logs.parent.mkdir(parents=True, exist_ok=True)
        self.logs.touch()

        if self.file_path.exists():
            self.file_path.unlink()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        # this is here so that it won't break on primitive's init
        # do not move
        result = subprocess.run(["which", "primitive"], capture_output=True)
        if result.returncode == 0:
            self.executable = result.stdout.decode().rstrip("\n")
        else:
            raise Exception("primitive binary not found")

        self.file_path.write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>KeepAlive</key>
    <true/>
    <key>Label</key>
    <string>{self.label}</string>
    <key>LimitLoadToSessionType</key>
	<array>
		<string>Aqua</string>
		<string>Background</string>
		<string>LoginWindow</string>
		<string>StandardIO</string>
	</array>
    <key>ProgramArguments</key>
    <array>
        <string>{self.executable}</string>
        {"".join([f"<string>{arg}</string>" for arg in self.command.split(" ") if arg.strip() != ""])}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>{self.logs}</string>
    <key>StandardOutPath</key>
    <string>{self.logs}</string>
</dict>
</plist>"""
        )
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

    def delete_plist_file(self) -> bool:
        try:
            if self.file_path.exists():
                self.file_path.unlink()
            return True
        except Exception as e:
            logger.error(
                f"Unable to delete log file at {self.logs} for daemon {self.label}"
            )
            logger.error(e)
            return False

    def install(self) -> bool:
        return all(
            [
                self.stop(),
                self.unload(),
                self.create_stdout_file(),
                self.populate(),
                self.load(),
                self.start(load=False),
            ]
        )

    def uninstall(self) -> bool:
        return all(
            [
                self.stop(unload=False),
                self.unload(),
                self.delete_plist_file(),
                self.delete_stdout_file(),
            ]
        )

    def is_active(self) -> bool:
        if not self.is_installed():
            return False

        try:
            is_service_active = f"launchctl list {self.label}"  # noqa
            output = (
                subprocess.check_output(is_service_active.split(" ")).decode().strip()
            )
            return "PID" in output
        except subprocess.CalledProcessError as exception:
            logger.error(f"Unable to check if {self.label} active")
            logger.error(exception)
            return False

    def is_installed(self) -> bool:
        try:
            is_service_active = f"launchctl list {self.label}"  # noqa
            subprocess.check_output(
                is_service_active.split(" "), stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError as exception:
            if exception.returncode != 113:
                logger.error(f"Unable to check if {self.label} enabled")
                logger.error(exception)
            return False
