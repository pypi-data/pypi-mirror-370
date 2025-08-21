import os
import shutil
import typing
from pathlib import Path, PurePath
from typing import Dict

from loguru import logger

from ..utils.cache import get_artifacts_cache, get_logs_cache

if typing.TYPE_CHECKING:
    import primitive.client


class Uploader:
    def __init__(
        self,
        primitive: "primitive.client.Primitive",
    ):
        self.primitive = primitive

    def upload_dir(self, cache: Path) -> Dict:
        file_ids = []
        job_run_id = cache.name

        files = None
        has_walk = getattr(cache, "walk", None)
        if has_walk:
            files = sorted(
                [
                    current_path / file
                    for current_path, _, current_path_files in cache.walk()
                    for file in current_path_files
                ],
                key=lambda p: p.stat().st_size,
            )
        else:
            files = sorted(
                [
                    Path(Path(current_path) / file)
                    for current_path, _, current_path_files in os.walk(cache)
                    for file in current_path_files
                ],
                key=lambda p: p.stat().st_size,
            )

        for file in files:
            try:
                upload_file_result = self.primitive.files.upload_file_direct(
                    path=file,
                    key_prefix=str(PurePath(file).relative_to(cache.parent).parent),
                )

                if upload_file_result and upload_file_result.data is not None:
                    upload_file_data = upload_file_result.data
                    upload_id = upload_file_data.get("fileUpdate", {}).get("id")

                    if upload_id:
                        file_ids.append(upload_id)
                        continue

                logger.error(f"Unable to upload file {file}")
            except Exception as exception:
                if "is empty" in str(exception):
                    logger.warning(f"{file} is empty, skipping upload")
                    continue

        # Clean up job cache
        shutil.rmtree(path=cache)

        return {job_run_id: file_ids}

    def scan(self) -> None:
        # Scan artifacts directory
        artifacts_dir = get_artifacts_cache()
        logs_dir = get_logs_cache()

        artifacts = sorted(
            [
                artifacts_cache
                for artifacts_cache in artifacts_dir.iterdir()
                if artifacts_cache.is_dir()
            ],
            key=lambda p: p.stat().st_ctime,
        )

        logs = sorted(
            [logs_cache for logs_cache in logs_dir.iterdir() if logs_cache.is_dir()],
            key=lambda p: p.stat().st_ctime,
        )

        log_files = {
            job_id: files
            for log_path in logs
            for job_id, files in self.upload_dir(log_path).items()
        }

        artifact_files = {
            job_id: files
            for artifact_path in artifacts
            for job_id, files in self.upload_dir(artifact_path).items()
        }

        files_by_id = {
            job_id: log_files.get(job_id, []) + artifact_files.get(job_id, [])
            for job_id in log_files.keys() | artifact_files.keys()
        }

        # Update job run
        for job_id, files in files_by_id.items():
            self.primitive.jobs.job_run_update(id=job_id, file_ids=files)
