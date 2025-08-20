"""Simple one-line browser agent interface."""

from typing import Optional, Dict, Any, Union
import os

from .sync_client import TessaClient
from .models import BrowserConfig, JobResult, ActionSelectionModel


class BrowserAgent:
    """
    Simple interface for running browser agents with one line of code.
    
    Examples:
        >>> # One-line usage
        >>> result = BrowserAgent("YOUR_API_KEY").run("Go to example.com and extract the title")
        >>> print(result.output)
        
        >>> # Or using environment variable
        >>> os.environ["TESSA_API_KEY"] = "YOUR_API_KEY"
        >>> result = BrowserAgent().run("Extract prices from shop.example.com")
        
        >>> # Reusable agent
        >>> agent = BrowserAgent("YOUR_API_KEY")
        >>> result1 = agent.run("Search for Python tutorials")
        >>> result2 = agent.run("Get trending topics from Twitter")
        
        >>> # With custom configuration
        >>> agent = BrowserAgent("YOUR_API_KEY", residential_ip=True)
        >>> result = agent.run("Access geo-restricted content")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        residential_ip: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        max_duration_minutes: int = 30,
        model: Union[str, ActionSelectionModel] = ActionSelectionModel.CLAUDE_SONNET,
        verbose: bool = False
    ):
        """
        Initialize a browser agent.
        
        Args:
            api_key: Your Tessa API key (can also be set via TESSA_API_KEY env var)
            base_url: Override the base API URL (for testing/development)
            residential_ip: Use residential IP proxy for the browser
            viewport_width: Browser viewport width in pixels (320-4096)
            viewport_height: Browser viewport height in pixels (320-4096)
            max_duration_minutes: Maximum session duration (1-240 minutes)
            model: AI model for action selection
            verbose: Print status updates while running
        """
        self.api_key = api_key or os.getenv("TESSA_API_KEY")
        self.base_url = base_url
        self.verbose = verbose
        self.model = model
        
        # Store browser config
        self.browser_config = BrowserConfig(
            width=viewport_width,
            height=viewport_height,
            residential_ip=residential_ip,
            max_duration_minutes=max_duration_minutes
        )
        
        # Client will be created on demand
        self._client: Optional[TessaClient] = None
    
    @property
    def client(self) -> TessaClient:
        """Get or create the client instance."""
        if self._client is None:
            self._client = TessaClient(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    def run(
        self,
        directive: str,
        initial_url: Optional[str] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None
    ) -> JobResult:
        """
        Run a browser agent with the given directive and wait for completion.
        
        Args:
            directive: Natural language instruction for the browser agent
            initial_url: Starting URL for the browser session
            poll_interval: Seconds between status checks (default: 5.0)
            timeout: Maximum seconds to wait (default: None for no timeout)
        
        Returns:
            JobResult with the extracted data or error
        
        Raises:
            TimeoutError: If timeout is exceeded
            JobFailedError: If the job fails
            AuthenticationError: If API key is invalid
        
        Examples:
            >>> agent = BrowserAgent("YOUR_API_KEY")
            >>> 
            >>> # Simple extraction
            >>> result = agent.run("Go to news.ycombinator.com and get the top 5 stories")
            >>> print(result.output)
            >>> 
            >>> # With starting URL
            >>> result = agent.run(
            ...     "Extract all product prices",
            ...     initial_url="https://shop.example.com/products"
            ... )
            >>> 
            >>> # With timeout
            >>> result = agent.run(
            ...     "Complete the checkout process",
            ...     timeout=120  # 2 minutes max
            ... )
        """
        return self.client.run_and_wait(
            directive=directive,
            initial_url=initial_url,
            browser_config=self.browser_config,
            poll_interval=poll_interval,
            timeout=timeout,
            verbose=self.verbose
        )
    
    def run_async(
        self,
        directive: str,
        initial_url: Optional[str] = None
    ):
        """
        Start a browser agent without waiting for completion.
        
        Args:
            directive: Natural language instruction for the browser agent
            initial_url: Starting URL for the browser session
        
        Returns:
            Job object for tracking the job status
        
        Examples:
            >>> agent = BrowserAgent("YOUR_API_KEY")
            >>> job = agent.run_async("Extract data from multiple pages")
            >>> # Do other work...
            >>> result = job.wait_for_completion()
        """
        return self.client.run_browser_agent(
            directive=directive,
            initial_url=initial_url,
            action_selection_model=self.model,
            browser_config=self.browser_config
        )
    
    def extract(self, url: str, data_description: str) -> JobResult:
        """
        Convenience method to extract specific data from a URL.
        
        Args:
            url: The URL to extract data from
            data_description: Description of what data to extract
        
        Returns:
            JobResult with the extracted data
        
        Examples:
            >>> agent = BrowserAgent("YOUR_API_KEY")
            >>> result = agent.extract(
            ...     "https://example.com/products",
            ...     "product names, prices, and availability"
            ... )
        """
        directive = f"Go to {url} and extract {data_description}"
        return self.run(directive, initial_url=url)
    
    def search_and_extract(
        self,
        search_query: str,
        search_engine: str = "google",
        num_results: int = 5
    ) -> JobResult:
        """
        Search for a query and extract results.
        
        Args:
            search_query: The search query
            search_engine: Which search engine to use (google, bing, duckduckgo)
            num_results: Number of results to extract
        
        Returns:
            JobResult with search results
        
        Examples:
            >>> agent = BrowserAgent("YOUR_API_KEY")
            >>> result = agent.search_and_extract("Python tutorials", num_results=10)
        """
        search_urls = {
            "google": "https://google.com",
            "bing": "https://bing.com",
            "duckduckgo": "https://duckduckgo.com"
        }
        
        url = search_urls.get(search_engine.lower(), "https://google.com")
        directive = f"Search for '{search_query}' and extract the top {num_results} results including titles, URLs, and descriptions"
        
        return self.run(directive, initial_url=url)
    
    def fill_form(
        self,
        url: str,
        form_data: Dict[str, Any],
        submit: bool = True
    ) -> JobResult:
        """
        Fill out a form on a webpage.
        
        Args:
            url: The URL with the form
            form_data: Dictionary of form field names/values
            submit: Whether to submit the form after filling
        
        Returns:
            JobResult with confirmation or extracted data
        
        Examples:
            >>> agent = BrowserAgent("YOUR_API_KEY")
            >>> result = agent.fill_form(
            ...     "https://example.com/contact",
            ...     {
            ...         "name": "John Doe",
            ...         "email": "john@example.com",
            ...         "message": "Hello!"
            ...     }
            ... )
        """
        form_str = ", ".join([f"{k}: {v}" for k, v in form_data.items()])
        directive = f"Fill out the form with: {form_str}"
        if submit:
            directive += " and submit it"
        
        return self.run(directive, initial_url=url)
    
    def close(self):
        """Close the client and clean up resources."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __del__(self):
        """Clean up resources when the agent is destroyed."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup
