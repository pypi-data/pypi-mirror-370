from dataclasses import dataclass


@dataclass
class P_CLI_100(Exception):
    """Check In Connection Failure while Stopping Agent"""

    codename: str = "P_CLI_100"
    message: str = "Check In Connection Failure while Stopping Agent"

    def __str__(self):
        return f"{self.codename}: {self.message}"


@dataclass
class P_CLI_101(Exception):
    """Could Not Get Status for JobRun"""

    codename: str = "P_CLI_101"
    message: str = "Could Not Get Status for JobRun"

    def __str__(self):
        return f"{self.codename}: {self.message}"
