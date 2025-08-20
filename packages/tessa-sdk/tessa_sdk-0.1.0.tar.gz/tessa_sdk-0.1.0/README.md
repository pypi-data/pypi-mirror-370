# Tessa SDK for Python

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The official Python SDK for the [Tessa Browser Agent API](https://heytessa.ai) - AI-powered browser automation with **93% accuracy on WebVoyager**.

## 🚀 Quick Start

```bash
pip install tessa_sdk
```

```python
from tessa_sdk import BrowserAgent

# One-line browser automation
result = BrowserAgent("YOUR_API_KEY").run("Go to news.ycombinator.com and get the top 5 stories")
print(result.output)
```

## 📚 Features

- **🎯 One-Line Interface** - Run browser automation with a single line of code
- **🔄 Sync & Async Clients** - Both synchronous and asynchronous APIs available
- **🧠 Multiple AI Models** - Claude, GPT-4, or Gemini for action selection
- **🌐 Residential IPs** - Access geo-restricted content
- **📊 Real-time Monitoring** - Watch your browser agent work live
- **📝 Type Safety** - Full type hints for better IDE support
- **🛡️ Thread-Safe** - Sync client works in any environment

## 🔑 Authentication

Get your API key from [app.heytessa.ai/settings](https://app.heytessa.ai/settings)

```python
# Method 1: Pass directly
agent = BrowserAgent("YOUR_API_KEY")

# Method 2: Environment variable
export TESSA_API_KEY="YOUR_API_KEY"
agent = BrowserAgent()  # Uses env var
```

## 🎯 Usage Examples

### Simple Usage

```python
from tessa_sdk import BrowserAgent

agent = BrowserAgent("YOUR_API_KEY")

# Extract data from a website
result = agent.run("Go to example.com and extract the main heading")

# Extract specific data
result = agent.extract(
    url="https://github.com/trending",
    data_description="repository names and star counts"
)

# Search and extract
result = agent.search_and_extract("Python tutorials", num_results=10)

# Fill forms
result = agent.fill_form(
    url="https://example.com/contact",
    form_data={"name": "John", "email": "john@example.com"}
)
```

### Synchronous Client

```python
from tessa_sdk import TessaClient, BrowserConfig

# Using context manager for automatic cleanup
with TessaClient(api_key="YOUR_API_KEY") as client:
    # Run and wait for completion
    result = client.run_and_wait(
        directive="Extract pricing data from the products page",
        browser_config=BrowserConfig(
            width=1920,
            height=1080,
            residential_ip=True
        ),
        verbose=True
    )
    print(f"Output: {result.output}")
    print(f"Credits used: {result.credits_used}")

# Or manage jobs manually
client = TessaClient(api_key="YOUR_API_KEY")
job = client.run_browser_agent(
    directive="Extract data from multiple pages",
    initial_url="https://shop.example.com"
)

# Monitor progress
print(f"Watch live: {job.live_url}")

# Wait for completion
result = job.wait_for_completion(poll_interval=3.0)
print(f"Output: {result.output}")

client.close()
```

### Async Operations

```python
import asyncio
from tessa_sdk import AsyncTessaClient

async def run_multiple():
    async with AsyncTessaClient(api_key="YOUR_API_KEY") as client:
        # Start multiple jobs concurrently
        jobs = await asyncio.gather(
            client.run_browser_agent("Extract from site1.com"),
            client.run_browser_agent("Extract from site2.com"),
            client.run_browser_agent("Extract from site3.com")
        )
        
        # Wait for all to complete
        results = await asyncio.gather(
            *[job.wait_for_completion() for job in jobs]
        )
        
        for result in results:
            print(result.output)

asyncio.run(run_multiple())
```

## 📖 API Reference

### BrowserAgent

Simple interface for one-line automation:

```python
agent = BrowserAgent(
    api_key="YOUR_API_KEY",
    residential_ip=False,
    viewport_width=1920,
    viewport_height=1080,
    max_duration_minutes=30,
    model="claude-sonnet-4-20250514",
    verbose=False
)

result = agent.run(directive, initial_url=None, timeout=None)
```

### TessaClient

Full-featured client with job management:

```python
client = TessaClient(api_key="YOUR_API_KEY")

job = client.run_browser_agent(
    directive="Your instruction",
    browser_config={...}
)

status = client.get_job_status(job_id)
result = job.wait_for_completion()
```

### Models

```python
from tessa_sdk import BrowserConfig, ActionSelectionModel

config = BrowserConfig(
    width=1920,              # 320-4096
    height=1080,             # 320-4096  
    residential_ip=False,
    max_duration_minutes=30, # 1-240
    idle_timeout_minutes=2   # 1-60
)

# AI Models
ActionSelectionModel.CLAUDE_SONNET  # Default
ActionSelectionModel.GPT_4O
ActionSelectionModel.GEMINI_FLASH
```

## 🛡️ Error Handling

```python
from tessa_sdk.exceptions import *

try:
    result = agent.run("Extract data")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except TimeoutError as e:
    print(f"Timed out after {e.timeout_seconds}s")
except JobFailedError as e:
    print(f"Job failed: {e.error_message}")
```

## 📂 Examples

See the [examples/](examples/) directory:

- [quickstart.py](examples/quickstart.py) - Simple one-line usage
- [sync_example.py](examples/sync_example.py) - Synchronous client examples
- [async_example.py](examples/async_example.py) - Concurrent async operations
- [web_scraping.py](examples/web_scraping.py) - Various scraping scenarios
- [advanced_config.py](examples/advanced_config.py) - Advanced features

## 🏗️ Common Use Cases

### E-commerce Monitoring
```python
result = agent.run("""
    Search amazon.com for 'iPhone 15 Pro'.
    Extract prices and availability for top 5 results.
""")
```

### Social Media Analytics
```python
result = agent.run("""
    Go to twitter.com/elonmusk and extract
    the last 5 tweets with likes and retweets.
""")
```

### Job Aggregation
```python
result = agent.run("""
    Search indeed.com for 'Python Developer' in SF.
    Filter: Remote, $150k+. Extract top 10 jobs.
""")
```

## 💳 Credits

- **1 credit** per browser action
- **1,000 free credits** for new accounts
- Check balance: [app.heytessa.ai/settings](https://app.heytessa.ai/settings)

```python
result = agent.run("Your task")
print(f"Credits used: {result.credits_used}")
```

## 📞 Support

- **Docs**: [docs.heytessa.ai](https://docs.heytessa.ai)
- **Email**: [support@generalagency.ai](mailto:support@generalagency.ai)
- **Issues**: [GitHub Issues](https://github.com/GeneralAgencyAI/tessa_sdk/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ by the General Agency team