from dataclasses import dataclass, field
from subprocess import PIPE, Popen
from typing import Dict

from primitive.utils.text import slugify


@dataclass
class AndroidDevice:
    slug: str
    serial: str
    usb: str
    product: str
    model: str
    device: str
    transport_id: str
    system_info: Dict = field(default_factory=lambda: {})

    def _get_android_values(self):
        """Get the values of the Android device."""

        # example line:
        # System name | Network (domain) name | Kernel Release number | Kernel Version | Machine (hardware) name
        # Linux localhost 6.1.75-android14-11-g48b922851ac5-ab12039954 #1 SMP PREEMPT Tue Jul  2 09:33:34 UTC 2024 aarch64 Toybox
        uname_output = execute_command(serial=self.serial, command="uname -a")
        self.system_info["name"] = self.serial
        self.system_info["os_family"] = "Android"
        self.system_info["os_release"] = uname_output[2]
        self.system_info["os_version"] = uname_output[3]
        self.system_info["platform"] = ""
        self.system_info["processor"] = ""
        self.system_info["machine"] = uname_output[13]
        self.system_info["architecture"] = "64bit"
        return self.system_info


def list_devices():
    """List all connected Android devices."""
    devices = []

    with Popen(["adb", "devices", "-l"], stdout=PIPE) as process:
        for line in process.stdout.read().decode("utf-8").split("\n"):
            if line == "":
                continue

            if "List of devices attached" in line:
                continue

            device_details_array = [
                detail for detail in line.split(" ") if detail != ""
            ]

            slug = slugify(device_details_array[0])
            android_device = AndroidDevice(
                slug=slug,
                serial=device_details_array[0],
                usb=device_details_array[1],
                product=device_details_array[2],
                model=device_details_array[3],
                device=device_details_array[4],
                transport_id=device_details_array[5],
            )
            android_device._get_android_values()
            devices.append(android_device)

    return devices


def execute_command(serial: str, command: str):
    """Execute a command on an Android device."""
    with Popen(
        ["adb", "-s", serial, "shell", *command.split(" ")], stdin=PIPE, stdout=PIPE
    ) as process:
        return process.stdout.read().decode("utf-8")


def create_interactive_shell(serial: str, command: str):
    """Create an interactive shell to an Android device."""
    with Popen(["adb", "-s", serial, "shell"], stdin=PIPE, stdout=PIPE) as process:
        return process.stdout.read().decode("utf-8")
