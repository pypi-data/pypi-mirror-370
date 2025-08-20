"""Synchronous client for the Tessa API."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, Union
import time

from .async_client import AsyncTessaClient, AsyncJob
from .models import (
    BrowserConfig,
    JobStatus,
    JobResult,
    JobStatusEnum,
    ActionSelectionModel,
)
from .exceptions import TimeoutError, JobFailedError


class Job:
    """Represents a running job that can be polled for status."""
    
    def __init__(self, client: "TessaClient", job_id: str, initial_response: dict):
        self.client = client
        self.job_id = job_id
        self.initial_status = initial_response.get("status")
        self.live_url = initial_response.get("live_url")
        self.cdp_url = initial_response.get("cdp_url")
        self.history_url = initial_response.get("history_url")
        self.polling_url = initial_response.get("polling_url")
        self._last_status: Optional[JobStatus] = None
    
    def get_status(self) -> JobStatus:
        """Get the current job status."""
        self._last_status = self.client.get_job_status(self.job_id)
        return self._last_status
    
    def wait_for_completion(
        self,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
        verbose: bool = False
    ) -> JobResult:
        """
        Wait for the job to complete.
        
        Args:
            poll_interval: Seconds between status checks (default: 5.0)
            timeout: Maximum seconds to wait (default: None for no timeout)
            verbose: Print status updates while waiting
        
        Returns:
            JobResult with the final output or error
        
        Raises:
            TimeoutError: If timeout is exceeded
            JobFailedError: If the job fails
        """
        start_time = time.time()
        
        while True:
            status = self.get_status()
            
            if verbose:
                print(f"Job {self.job_id} status: {status.status}")
            
            if status.status in [JobStatusEnum.COMPLETED, JobStatusEnum.FAILED, JobStatusEnum.USER_TAKEN_OVER]:
                if status.status == JobStatusEnum.FAILED:
                    raise JobFailedError(self.job_id, status.error or "Unknown error")
                
                # Calculate duration
                duration = None
                if status.created_at and status.updated_at:
                    duration = (status.updated_at - status.created_at).total_seconds()
                
                return JobResult(
                    job_id=self.job_id,
                    status=status.status,
                    output=status.output,
                    error=status.error,
                    credits_used=status.credits_used or 0,
                    duration_seconds=duration
                )
            
            # Check timeout
            if timeout:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(self.job_id, timeout)
            
            time.sleep(poll_interval)
    
    @property
    def url(self) -> str:
        """Get the URL to view this job in the Tessa app."""
        return self.history_url


class TessaClient:
    """
    Synchronous client for interacting with the Tessa API.
    
    This client provides a synchronous interface to the Tessa API, using
    thread-based execution for async operations to ensure compatibility
    across different environments.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3
    ):
        """
        Initialize the Tessa client.
        
        Args:
            api_key: Your Tessa API key (can also be set via TESSA_API_KEY env var)
            base_url: Override the base API URL (default: https://api.heytessa.ai/v1)
            timeout: Default timeout for API requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        
        # Thread pool for running async operations
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._async_client: Optional[AsyncTessaClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def _ensure_async_client(self):
        """Ensure the async client is initialized."""
        if self._async_client is None:
            def create_client():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                client = AsyncTessaClient(
                    api_key=self._api_key,
                    base_url=self._base_url,
                    timeout=self._timeout,
                    max_retries=self._max_retries
                )
                return loop, client
            
            self._loop, self._async_client = self._executor.submit(create_client).result()
    
    def _run_async(self, coro):
        """Run an async coroutine in the thread pool."""
        self._ensure_async_client()
        
        def run_in_loop():
            asyncio.set_event_loop(self._loop)
            return asyncio.run_coroutine_threadsafe(coro, self._loop).result()
        
        return self._executor.submit(run_in_loop).result()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the client and clean up resources."""
        if self._async_client:
            self._run_async(self._async_client.close())
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._executor.shutdown(wait=True)
    
    def run_browser_agent(
        self,
        directive: str,
        initial_url: Optional[str] = None,
        cdp_url: Optional[str] = None,
        live_url: Optional[str] = None,
        action_selection_model: Union[str, ActionSelectionModel] = ActionSelectionModel.CLAUDE_SONNET,
        browser_config: Optional[Union[Dict[str, Any], BrowserConfig]] = None,
    ) -> Job:
        """
        Start a browser agent session.
        
        Args:
            directive: Natural language instruction for the browser agent
            initial_url: Starting URL for the browser session
            cdp_url: Chrome DevTools Protocol URL for custom browser
            live_url: Live view URL for custom browser session
            action_selection_model: AI model for action selection
            browser_config: Browser configuration options
        
        Returns:
            Job object for tracking the job status
        
        Example:
            >>> client = TessaClient(api_key="YOUR_API_KEY")
            >>> job = client.run_browser_agent(
            ...     directive="Go to example.com and extract the title",
            ...     browser_config={"width": 1920, "height": 1080}
            ... )
            >>> result = job.wait_for_completion()
            >>> print(result.output)
        """
        self._ensure_async_client()
        
        async_job = self._run_async(
            self._async_client.run_browser_agent(
                directive=directive,
                initial_url=initial_url,
                cdp_url=cdp_url,
                live_url=live_url,
                action_selection_model=action_selection_model,
                browser_config=browser_config
            )
        )
        
        # Convert async job response to dict for sync Job
        response_dict = {
            "job_id": async_job.job_id,
            "status": async_job.initial_status,
            "live_url": async_job.live_url,
            "cdp_url": async_job.cdp_url,
            "history_url": async_job.history_url,
            "polling_url": async_job.polling_url
        }
        
        return Job(self, async_job.job_id, response_dict)
    
    def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get the status of a job.
        
        Args:
            job_id: The job ID to check
        
        Returns:
            JobStatus with current job information
        """
        self._ensure_async_client()
        return self._run_async(self._async_client.get_job_status(job_id))
    
    def health_check(self) -> bool:
        """
        Check if the API is healthy.
        
        Returns:
            True if the API is healthy
        """
        self._ensure_async_client()
        return self._run_async(self._async_client.health_check())
    
    def run_and_wait(
        self,
        directive: str,
        initial_url: Optional[str] = None,
        browser_config: Optional[Union[Dict[str, Any], BrowserConfig]] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
        verbose: bool = False
    ) -> JobResult:
        """
        Convenience method to run a browser agent and wait for completion.
        
        Args:
            directive: Natural language instruction for the browser agent
            initial_url: Starting URL for the browser session
            browser_config: Browser configuration options
            poll_interval: Seconds between status checks (default: 5.0)
            timeout: Maximum seconds to wait (default: None for no timeout)
            verbose: Print status updates while waiting
        
        Returns:
            JobResult with the final output or error
        
        Example:
            >>> client = TessaClient(api_key="YOUR_API_KEY")
            >>> result = client.run_and_wait(
            ...     "Go to example.com and extract the title",
            ...     verbose=True
            ... )
            >>> print(result.output)
        """
        job = self.run_browser_agent(
            directive=directive,
            initial_url=initial_url,
            browser_config=browser_config
        )
        return job.wait_for_completion(
            poll_interval=poll_interval,
            timeout=timeout,
            verbose=verbose
        )
