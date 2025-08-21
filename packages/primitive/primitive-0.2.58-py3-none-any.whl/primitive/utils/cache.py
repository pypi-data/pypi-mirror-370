import platform
from pathlib import Path


def get_cache_dir() -> Path:
    os_family = platform.system()

    cache_dir = None
    if os_family == "Darwin":
        cache_dir = Path(Path.home() / "Library" / "Caches" / "tech.primitive.agent")
    elif os_family == "Linux":
        cache_dir = Path(Path.home() / ".cache" / "primitive")
    elif os_family == "Windows":
        raise NotImplementedError("Windows is not currently supported.")

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def get_sources_cache() -> Path:
    cache_dir = get_cache_dir()

    sources_dir = cache_dir / "sources"

    if not sources_dir.exists():
        sources_dir.mkdir(parents=True, exist_ok=True)

    return sources_dir


def get_artifacts_cache(cache_id: str = None) -> Path:
    cache_dir = get_cache_dir()

    artifacts_dir = cache_dir / "artifacts"

    if cache_id:
        artifacts_dir = artifacts_dir / cache_id

    if not artifacts_dir.exists():
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    return artifacts_dir


def get_logs_cache(cache_id: str = None) -> Path:
    cache_dir = get_cache_dir()

    logs_dir = cache_dir / "logs"

    if cache_id:
        logs_dir = logs_dir / cache_id

    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)

    return logs_dir


def get_deps_cache() -> Path:
    cache_dir = get_cache_dir()

    deps_dir = cache_dir / "deps"

    if not deps_dir.exists():
        deps_dir.mkdir(parents=True, exist_ok=True)

    return deps_dir
