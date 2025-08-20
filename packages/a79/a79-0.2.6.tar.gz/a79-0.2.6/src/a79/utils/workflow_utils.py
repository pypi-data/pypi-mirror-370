from pydantic import BaseModel


class ErrorHandling(BaseModel):
    """
    Configuration for error handling in nodes.

    Attributes:
        timeout_seconds (float | None): Timeout in seconds for node execution.
        retry_interval_seconds (float): Interval between retries in seconds.
        max_retries (int): Maximum number of retries.
        backoff_rate (float): Rate of increase for retry intervals.
    """

    timeout_seconds: float | None = (
        900  # 15 minutes because sub-workflows can be run in the python node
    )
    retry_interval_seconds: float = 1
    max_retries: int = 0
    backoff_rate: float = 1
