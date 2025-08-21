import os

# The default amount of time, in seconds, before raising a timeout exception
# Can be overwritten using the APH_TIMEOUT_JOB_SECONDS environment variable
DEFAULT_JOB_TIMEOUT_SECONDS = "300"

# The default amount of time, in seconds, before printing a warning to the user that the
# computation is taking longer than we might expect.
JOB_WARNING_TIMEOUT_SECONDS = 30


def get_job_timeout() -> int:
    """
    Get the job timeout value from the environment variable APH_TIMEOUT_JOB_SECONDS.
    If the variable is not set or is invalid, return the default value.
    """
    try:
        return int(os.environ.get("APH_TIMEOUT_JOB_SECONDS", DEFAULT_JOB_TIMEOUT_SECONDS))
    except ValueError:
        print(
            f"""Invalid value for APH_TIMEOUT_JOB_SECONDS.
            Using default value of {DEFAULT_JOB_TIMEOUT_SECONDS} seconds."""
        )
    return int(DEFAULT_JOB_TIMEOUT_SECONDS)
