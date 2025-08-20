"""
Tessa SDK - Python SDK for the Tessa Browser Agent & Workflows API

Simple one-line usage:
    >>> from tessa_sdk import BrowserAgent
    >>> result = BrowserAgent("YOUR_API_KEY").run("Go to example.com and extract the title")

Advanced usage:
    >>> from tessa_sdk import TessaClient
    >>> client = TessaClient(api_key="YOUR_API_KEY")
    >>> job = client.run_browser_agent(directive="...", browser_config={...})
    >>> result = job.wait_for_completion()
"""

from .browser import BrowserAgent
from .sync_client import TessaClient
from .async_client import AsyncTessaClient
from .models import (
    BrowserConfig,
    JobStatus,
    JobResult,
    JobStatusEnum,
    ActionSelectionModel,
)
from .exceptions import (
    TessaError,
    AuthenticationError,
    RateLimitError,
    JobNotFoundError,
    JobFailedError,
    ValidationError,
    TimeoutError,
    ConfigurationError,
)

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "BrowserAgent",
    "TessaClient",
    "AsyncTessaClient",
    # Models
    "BrowserConfig",
    "JobStatus",
    "JobResult",
    "JobStatusEnum",
    "ActionSelectionModel",
    # Exceptions
    "TessaError",
    "AuthenticationError",
    "RateLimitError",
    "JobNotFoundError",
    "JobFailedError",
    "ValidationError",
    "TimeoutError",
    "ConfigurationError",
]
