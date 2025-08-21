import datetime
import hashlib
import uuid


def get_package_version():
    from importlib.metadata import version
    return version("m2c2-datakit")


def get_sys_stats() -> dict:
    """
    Retrieve system statistics for the current process.

    Returns:
        dict: A dictionary containing memory usage (MB) and CPU percentage.
    """
    import psutil
    process = psutil.Process()
    memory = process.memory_info().rss / (1024**2)  # Memory usage in MB
    cpu = process.cpu_percent(interval=0.1)  # CPU usage percentage
    return {"memory_mb": memory, "cpu_percent": cpu}


def get_timestamp() -> datetime.datetime:
    """
    Returns the current timestamp as a datetime object.

    Returns:
        datetime.datetime: The current timestamp.
    """
    return datetime.datetime.now()


def get_filename_timestamp() -> str:
    """
    Returns a timestamp formatted for filenames.

    Returns:
        str: The timestamp as a string in 'YYYYMMDD_HHMMSS' format.
    """
    return get_timestamp().strftime("%Y%m%d_%H%M%S")


def get_uuid(version: int = 4) -> str:
    """
    Generate a UUID based on the specified version.

    Parameters:
        version (int): The version of the UUID to generate (1 or 4).
                      Defaults to version 4.

    Returns:
        str: A string representation of the generated UUID.
    """
    if version == 1:
        return str(uuid.uuid1())
    return str(uuid.uuid4())


def compute_md5_hash(df) -> str:
    """
    Compute an MD5 hash of a Pandas DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to hash.

    Returns:
        str: The MD5 hash as a hexadecimal string.
    """
    import pandas as pd
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    df_string = df.to_json()
    return hashlib.md5(df_string.encode()).hexdigest()
