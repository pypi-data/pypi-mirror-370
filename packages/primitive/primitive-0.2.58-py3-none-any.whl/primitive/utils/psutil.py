import psutil
from loguru import logger


def kill_process_and_children(pid: int) -> bool:
    """Kill a process and all its children."""
    try:
        try:
            parent = psutil.Process(pid)
            logger.info(f"Process PID {parent.pid} found.")
        except psutil.NoSuchProcess:
            logger.info("Process not found")
            return False

        children = parent.children(recursive=True)

        for child in children:
            logger.info(f"Killing child process {child.pid}...")
            child.kill()

        logger.info(f"Killing parent process {parent.pid}...")
        parent.kill()
        return True
    except psutil.NoSuchProcess:
        logger.warning(f"Process with PID {pid} not found.")
        return False
