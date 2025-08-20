"""Async client for the Tessa API."""

import asyncio
import os
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta

import httpx
from httpx import Response

from .models import (
    BrowserConfig,
    RunBrowserAgentRequest,
    RunBrowserAgentResponse,
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
)


class AsyncJob:
    """Represents an async running job that can be polled for status."""
    
    def __init__(self, client: "AsyncTessaClient", job_response: RunBrowserAgentResponse):
        self.client = client
        self.job_id = job_response.job_id
        self.initial_status = job_response.status
        self.live_url = job_response.live_url
        self.cdp_url = job_response.cdp_url
        self.history_url = job_response.history_url
        self.polling_url = job_response.polling_url
        self._last_status: Optional[JobStatus] = None
    
    async def get_status(self) -> JobStatus:
        """Get the current job status."""
        self._last_status = await self.client.get_job_status(self.job_id)
        return self._last_status
    
    async def wait_for_completion(
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
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_status()
            
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
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(self.job_id, timeout)
            
            await asyncio.sleep(poll_interval)
    
    @property
    def url(self) -> str:
        """Get the URL to view this job in the Tessa app."""
        return self.history_url


class AsyncTessaClient:
    """Async client for interacting with the Tessa API."""
    
    BASE_URL = "https://api.heytessa.ai/v1"
    
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
        self.api_key = api_key or os.getenv("TESSA_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key is required. Set it via constructor or TESSA_API_KEY environment variable")
        
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "tessa_sdk-python/0.1.0"
            },
            timeout=httpx.Timeout(timeout),
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def _handle_response(self, response: Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError()
        elif response.status_code == 403:
            raise AuthenticationError("API key does not have permission to access this resource")
        elif response.status_code == 404:
            raise JobNotFoundError(response.url.path.split("/")[-1])
        elif response.status_code == 422:
            data = response.json()
            raise ValidationError("Validation error", data.get("detail", []))
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)
        else:
            raise TessaError(
                f"API request failed with status {response.status_code}",
                {"status_code": response.status_code, "response": response.text}
            )
    
    async def run_browser_agent(
        self,
        directive: str,
        initial_url: Optional[str] = None,
        cdp_url: Optional[str] = None,
        live_url: Optional[str] = None,
        action_selection_model: Union[str, ActionSelectionModel] = ActionSelectionModel.CLAUDE_SONNET,
        browser_config: Optional[Union[Dict[str, Any], BrowserConfig]] = None,
    ) -> AsyncJob:
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
            AsyncJob object for tracking the job status
        """
        # Convert browser_config to BrowserConfig if it's a dict
        if browser_config and isinstance(browser_config, dict):
            browser_config = BrowserConfig(**browser_config)
        
        # Convert model to enum if it's a string
        if isinstance(action_selection_model, str):
            action_selection_model = ActionSelectionModel(action_selection_model)
        
        # Build request
        request = RunBrowserAgentRequest(
            directive=directive,
            initial_url=initial_url,
            cdp_url=cdp_url,
            live_url=live_url,
            action_selection_model=action_selection_model,
            browser_config=browser_config
        )
        
        # Make API request
        response = await self._client.post(
            "/run_browser_agent",
            json=request.model_dump(exclude_none=True)
        )
        
        data = await self._handle_response(response)
        job_response = RunBrowserAgentResponse(**data)
        
        return AsyncJob(self, job_response)
    
    async def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get the status of a job.
        
        Args:
            job_id: The job ID to check
        
        Returns:
            JobStatus with current job information
        """
        response = await self._client.get(f"/get_job_status/{job_id}")
        data = await self._handle_response(response)
        return JobStatus(**data)
    
    async def health_check(self) -> bool:
        """
        Check if the API is healthy.
        
        Returns:
            True if the API is healthy
        """
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except Exception:
            return False
