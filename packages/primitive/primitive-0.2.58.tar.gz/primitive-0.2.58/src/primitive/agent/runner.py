import asyncio
import os
import shutil
import typing
from enum import Enum
from pathlib import Path, PurePath
from typing import Dict, List, TypedDict

from loguru import logger

from primitive.utils.cache import get_artifacts_cache, get_logs_cache, get_sources_cache
from primitive.utils.logging import fmt, log_context
from primitive.utils.psutil import kill_process_and_children

if typing.TYPE_CHECKING:
    import primitive.client

BUFFER_SIZE = 4096


class Task(TypedDict):
    label: str
    workdir: str
    tags: Dict
    cmd: str


class JobConfig(TypedDict):
    requires: List[str]
    executes: List[Task]
    stores: List[str]


class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"


class Runner:
    def __init__(
        self,
        primitive: "primitive.client.Primitive",
        job_run: Dict,
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> None:
        self.primitive = primitive
        self.job = job_run["job"]
        self.job_run = job_run
        self.job_settings = job_run["jobSettings"]
        self.config = job_run["jobSettings"]["config"]
        self.initial_env = {}
        self.modified_env = {}
        self.file_logger = None

        # If max_log_size set to <= 0, disable file logging
        if max_log_size > 0:
            log_name = f"{self.job['slug']}_{self.job_run['jobRunNumber']}_{{time}}.primitive.log"

            self.file_logger = logger.add(
                Path(get_logs_cache(self.job_run["id"]) / log_name),
                rotation=max_log_size,
                format=fmt,
                backtrace=True,
            )

    @log_context(label="setup")
    def setup(self) -> None:
        # Attempt to download the job source code
        git_repo_full_name = self.job_run["gitCommit"]["repoFullName"]
        git_ref = self.job_run["gitCommit"]["sha"]
        logger.info(f"Downloading repository {git_repo_full_name} at ref {git_ref}")

        github_access_token = self.primitive.jobs.github_access_token_for_job_run(
            self.job_run["id"]
        )

        downloaded_git_repository_dir = (
            self.primitive.git.download_git_repository_at_ref(
                git_repo_full_name=git_repo_full_name,
                git_ref=git_ref,
                github_access_token=github_access_token,
                destination=get_sources_cache(),
            )
        )

        self.source_dir = downloaded_git_repository_dir.joinpath(
            self.job_settings["rootDirectory"]
        )

        # Setup initial process environment
        self.initial_env = os.environ
        self.initial_env = {
            **self.initial_env,
            **self.primitive.jobs.get_job_secrets_for_job_run(self.job_run["id"]),
        }
        self.initial_env["PRIMITIVE_SOURCE_DIR"] = str(self.source_dir)
        self.initial_env["PRIMITIVE_GIT_SHA"] = str(self.job_run["gitCommit"]["sha"])
        self.initial_env["PRIMITIVE_GIT_BRANCH"] = str(
            self.job_run["gitCommit"]["branch"]
        )
        self.initial_env["PRIMITIVE_GIT_REPO"] = str(
            self.job_run["gitCommit"]["repoFullName"]
        )

        if "VIRTUAL_ENV" in self.initial_env:
            del self.initial_env["VIRTUAL_ENV"]
        if "SHELL" in self.initial_env:
            self.initial_env["SHELL"] = "/bin/bash"

    @log_context(label="execute")
    def execute_job_run(self) -> None:
        self.modified_env = {**self.initial_env}
        task_failed = False
        cancelled = False
        timed_out = False

        for task in self.config["executes"]:
            # Everything inside this loop should be contextualized with the task label
            # this way we aren't jumping back and forth between the task label and "execute"
            with logger.contextualize(label=task["label"]):
                # the get status check here is to ensure that if cancel is called
                # while one task is running, we do not run any OTHER labeled tasks
                # THIS is required for MULTI STEP JOBS
                status = self.primitive.jobs.get_job_status(self.job_run["id"])
                status_value = status.data["jobRun"]["status"]
                conclusion_value = status.data["jobRun"]["conclusion"]

                if status_value == "completed" and conclusion_value == "cancelled":
                    cancelled = True
                    break
                if status_value == "completed" and conclusion_value == "timed_out":
                    timed_out = True
                    break

                # Everything within this block should be contextualized as user logs
                with logger.contextualize(type="user"):
                    with asyncio.Runner() as async_runner:
                        if task_failed := async_runner.run(self.run_task(task)):
                            break

        # FOR NONE MULTI STEP JOBS
        # we still have to check that the job was cancelled here as well
        with logger.contextualize(label="conclusion"):
            status = self.primitive.jobs.get_job_status(self.job_run["id"])
            status_value = status.data["jobRun"]["status"]
            conclusion_value = status.data["jobRun"]["conclusion"]
            if status_value == "completed" and conclusion_value == "cancelled":
                cancelled = True
            if status_value == "completed" and conclusion_value == "timed_out":
                timed_out = True

            if cancelled:
                logger.warning("Job cancelled by user")
                return

            if timed_out:
                logger.error("Job timed out")
                return

            conclusion = "success"
            if task_failed:
                conclusion = "failure"
            else:
                logger.success(f"Completed {self.job['slug']} job")

            self.primitive.jobs.job_run_update(
                self.job_run["id"],
                status="request_completed",
                conclusion=conclusion,
            )

    def get_number_of_files_produced(self) -> int:
        """Returns the number of files produced by the job."""
        number_of_files_produced = 0

        # Logs can be produced even if no artifact stores are created for the job run.
        job_run_logs_cache = get_logs_cache(self.job_run["id"])
        has_walk = getattr(job_run_logs_cache, "walk", None)
        if has_walk:
            log_files = [
                file
                for _, _, current_path_files in job_run_logs_cache.walk()
                for file in current_path_files
            ]
        else:
            log_files = [
                file
                for _, _, current_path_files in os.walk(job_run_logs_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(log_files)

        if "stores" not in self.config:
            return number_of_files_produced

        job_run_artifacts_cache = get_artifacts_cache(self.job_run["id"])
        has_walk = getattr(job_run_artifacts_cache, "walk", None)
        if has_walk:
            artifact_files = [
                file
                for _, _, current_path_files in job_run_artifacts_cache.walk()
                for file in current_path_files
            ]
        else:
            artifact_files = [
                file
                for _, _, current_path_files in os.walk(job_run_artifacts_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(artifact_files)

        return number_of_files_produced

    async def run_task(self, task: Task) -> bool:
        logger.info(f"Running step '{task['label']}'")
        commands = task["cmd"].strip().split("\n")
        for i, cmd in enumerate(commands):
            # Adding an additional echo and utilizing stdbuf to force line buffering
            # This ensures that the environment variables and starting delimiter are
            # always in a new chunk, vastly simplifying our parsing logic
            args = ["/bin/bash", "-c", cmd]

            logger.info(
                f"Executing command {i + 1}/{len(commands)}: {cmd} at {self.source_dir / task.get('workdir', '')}"
            )

            process = await asyncio.create_subprocess_exec(
                *args,
                env=self.modified_env,
                cwd=str(Path(self.source_dir / task.get("workdir", ""))),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                while process.pid is None:
                    logger.debug(
                        f"Waiting for process PID to be set for command {i + 1}/{len(commands)}: {cmd}"
                    )
                    await asyncio.sleep(1)
                logger.debug(f"Process started with PID {process.pid} for command")
                await self.primitive.jobs.ajob_run_update(
                    id=self.job_run["id"],
                    parent_pid=process.pid,
                )
            except ValueError:
                logger.error(
                    f"Failed to update job run {self.job_run['id']} with process PID {process.pid}"
                )
                kill_process_and_children(pid=process.pid)
                return False

            await asyncio.gather(
                self.log_cmd(stream=process.stdout, level=LogLevel.INFO),
                self.log_cmd(stream=process.stderr, level=LogLevel.ERROR),
            )

            returncode = await process.wait()

            logger.info(
                f"Finished executing command {i + 1}/{len(commands)}: {cmd} with return code {returncode}"
            )

            if returncode > 0:
                logger.error(
                    f"Task {task['label']} failed on '{cmd}' with return code {returncode}"
                )
                return True

        logger.success(f"Completed {task['label']} task")
        return False

    async def log_cmd(
        self,
        stream: asyncio.StreamReader | None,
        level: LogLevel,
    ):
        buffer = bytearray()
        while stream and not stream.at_eof():
            chunk = await stream.read(BUFFER_SIZE)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, _, buffer = buffer.partition(b"\n")
                logger.log(level.value, line.decode(errors="replace"))
        if buffer:
            logger.log(level.value, buffer.decode(errors="replace"))

    @log_context(label="cleanup")
    def cleanup(self) -> None:
        for glob in self.config.get("stores", []):
            # Glob relative to the source directory
            matches = self.source_dir.rglob(glob)

            for match in matches:
                relative_path = PurePath(match).relative_to(self.source_dir)
                dest = Path(get_artifacts_cache(self.job_run["id"]) / relative_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                Path(match).replace(dest)

        shutil.rmtree(path=self.source_dir)

        number_of_files_produced = self.get_number_of_files_produced()
        logger.info(
            f"Produced {number_of_files_produced} files for {self.job['slug']} job"
        )
        self.primitive.jobs.job_run_update(
            self.job_run["id"],
            number_of_files_produced=number_of_files_produced,
        )

        logger.remove(self.file_logger)
