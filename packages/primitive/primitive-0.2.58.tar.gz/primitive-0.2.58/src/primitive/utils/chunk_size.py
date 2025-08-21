import math

import speedtest

from .memory_size import MemorySize

max_threads = 4


def get_upload_speed_mb() -> int:
    """
    Calculate the Bytes per Second upload speed using the speedtest-cli library.
    Return the upload speed in a round "MB" MegaBytes to the power of two format.
    """
    speedtest_client = speedtest.Speedtest(secure=True)
    speedtest_client.get_best_server()
    upload_speed_bytes = speedtest_client.upload()

    upload_speed_mb = MemorySize(upload_speed_bytes, "B")
    upload_speed_mb.convert_to("MB")
    return int(upload_speed_mb.value)


def nearest_classic_power_of_two_mb(chunk_size_bytes):
    """
    Finds the nearest 'classic' power-of-2 multiple in MB (e.g., 8, 16, 32 MB).

    Args:
        chunk_size_bytes (int): The chunk size in bytes.

    Returns:
        int: The closest size in bytes that corresponds to 8, 16, 32, etc. MB.
    """
    # Convert bytes to MB
    chunk_size_mb = chunk_size_bytes / (10**6)

    # Calculate log2 of the chunk size in MB
    log2_size = math.log2(chunk_size_mb)

    # Find the nearest powers of 2
    lower_mb = 2 ** math.floor(log2_size)
    upper_mb = 2 ** math.ceil(log2_size)

    # Convert back to bytes
    lower_bytes = lower_mb * (10**6)
    upper_bytes = upper_mb * (10**6)

    # Determine the closest one in bytes
    return (
        lower_bytes
        if abs(chunk_size_bytes - lower_bytes) <= abs(chunk_size_bytes - upper_bytes)
        else upper_bytes
    )


def calculate_optimal_chunk_size(
    upload_speed_mb: int,
    file_size_bytes: int,
    num_workers: int = 4,
    optimal_time_seconds: int = 5,
):
    """
    Calculate the optimal chunk size for a multipart upload based on network speed, cores, and file size.

    :param upload_speed_mbps: The upload speed in Mbit/s (but a single integer represented as MB).
    :param file_size_bytes: The size of the file in bytes.
    :param num_workers: The number of threads available for multi-threading (default is 4).
    :param optimal_time_seconds: The target upload time per chunk in seconds (default is 5).

    :return: A tuple (optimal_chunk_size_bytes, chunk_count, list_of_urls)
    """

    # Estimate transfer rate per thread (Bytes/sec)
    thread_speed_mbps = int(upload_speed_mb) / num_workers  # Mbit/s per thread
    thread_speed_bps = thread_speed_mbps * 125_000  # Convert to Bytes/sec

    # Calculate optimal chunk size (Bytes)
    optimal_chunk_size_bytes = thread_speed_bps * optimal_time_seconds
    rounded_chunk_size_bytes = nearest_classic_power_of_two_mb(optimal_chunk_size_bytes)

    # Adjust chunk size to ensure it's an integer and divide the file size into chunks
    chunk_count = math.ceil(file_size_bytes / rounded_chunk_size_bytes)
    # final_chunk_size_bytes = math.ceil(
    #     int(file_size_bytes) / chunk_count
    # )  # Round up to fit file size evenly

    return rounded_chunk_size_bytes, chunk_count
