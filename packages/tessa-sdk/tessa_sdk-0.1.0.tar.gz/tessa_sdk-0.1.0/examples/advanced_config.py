"""
Advanced configuration examples for the Tessa SDK.

This example demonstrates advanced features like custom browsers, 
different AI models, and complex automation scenarios.
"""

import os
from tessa_sdk import TessaClient, BrowserConfig, ActionSelectionModel
from tessa_sdk.exceptions import JobFailedError, TimeoutError

# Set your API key
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key


def custom_browser_example():
    """Example: Using your own browser via Chrome DevTools Protocol."""
    
    print("🖥️ Custom Browser Example")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    # Use your own browser instance
    # You need to start Chrome/Chromium with remote debugging enabled:
    # google-chrome --remote-debugging-port=9222
    
    job = client.run_browser_agent(
        directive="Navigate to the dashboard and extract the monthly revenue data",
        cdp_url="ws://localhost:9222/devtools/browser/YOUR-BROWSER-ID",  # Your CDP URL
        live_url="http://localhost:9222",  # Optional: for viewing
    )
    
    print(f"Using custom browser: {job.cdp_url}")
    
    try:
        result = job.wait_for_completion(timeout=120)
        print(f"✅ Result: {result.output}")
    except TimeoutError as e:
        print(f"⏱️ Operation timed out: {e}")
    except JobFailedError as e:
        print(f"❌ Job failed: {e.error_message}")
    
    client.close()


def different_ai_models():
    """Example: Compare different AI models for the same task."""
    
    print("🤖 AI Model Comparison")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    task = "Go to wikipedia.org and find information about artificial intelligence, then summarize the main concepts in 3 bullet points"
    
    models = [
        ActionSelectionModel.CLAUDE_SONNET,
        ActionSelectionModel.GPT_4O,
        ActionSelectionModel.GEMINI_FLASH
    ]
    
    results = {}
    
    for model in models:
        print(f"\n🔄 Testing with {model.value}...")
        
        job = client.run_browser_agent(
            directive=task,
            action_selection_model=model,
            browser_config={"width": 1366, "height": 768}
        )
        
        try:
            result = job.wait_for_completion(timeout=90)
            results[model.value] = {
                "success": True,
                "output": result.output,
                "credits_used": result.credits_used,
                "duration": result.duration_seconds
            }
            print(f"✅ Completed in {result.duration_seconds:.1f}s using {result.credits_used} credits")
        except Exception as e:
            results[model.value] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ Failed: {e}")
    
    # Compare results
    print("\n📊 Model Comparison Results:")
    print("-" * 40)
    for model, data in results.items():
        if data["success"]:
            print(f"{model}:")
            print(f"  Credits: {data['credits_used']}")
            print(f"  Duration: {data['duration']:.1f}s")
        else:
            print(f"{model}: Failed - {data['error']}")
    
    client.close()
    return results


def complex_workflow():
    """Example: Multi-step workflow with conditional logic."""
    
    print("🔄 Complex Multi-Step Workflow")
    print("-" * 50)
    
    from tessa_sdk import BrowserAgent
    
    agent = BrowserAgent(
        api_key=API_KEY,
        max_duration_minutes=20,
        verbose=True
    )
    
    # Step 1: Search for a product
    print("\n📍 Step 1: Searching for product...")
    search_result = agent.run(
        """Go to amazon.com and search for 'wireless headphones'. 
        Extract the name and price of the top-rated product under $100.""",
        timeout=60
    )
    
    if not search_result.is_successful:
        print("❌ Search failed")
        return
    
    product_info = search_result.output
    print(f"Found product: {product_info}")
    
    # Step 2: Compare prices on another site
    print("\n📍 Step 2: Comparing prices...")
    if isinstance(product_info, dict) and 'name' in product_info:
        product_name = product_info['name']
        
        comparison_result = agent.run(
            f"""Go to bestbuy.com and search for '{product_name}'.
            Find the closest matching product and extract its price and availability.""",
            timeout=60
        )
        
        if comparison_result.is_successful:
            print(f"Comparison result: {comparison_result.output}")
    
    # Step 3: Check reviews
    print("\n📍 Step 3: Checking reviews...")
    review_result = agent.run(
        f"""Go to youtube.com and search for '{product_name} review'.
        Extract the channel name and view count of the top 3 review videos.""",
        timeout=60
    )
    
    if review_result.is_successful:
        print(f"Review videos found: {review_result.output}")
    
    # Summary
    total_credits = (
        search_result.credits_used + 
        comparison_result.credits_used + 
        review_result.credits_used
    )
    
    print(f"\n📊 Workflow Summary:")
    print(f"  Total steps: 3")
    print(f"  Total credits used: {total_credits}")
    
    return {
        "product_search": search_result.output,
        "price_comparison": comparison_result.output if comparison_result.is_successful else None,
        "reviews": review_result.output if review_result.is_successful else None
    }


def form_automation():
    """Example: Complex form filling and submission."""
    
    print("📝 Form Automation Example")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    # Example: Fill out a complex contact form
    job = client.run_browser_agent(
        directive="""
        Navigate to the contact form and fill it out with the following information:
        - Name: John Smith
        - Email: john.smith@example.com
        - Phone: (555) 123-4567
        - Company: Acme Corporation
        - Job Title: Software Engineer
        - Message: I'm interested in learning more about your enterprise solution. 
                  Please send me pricing information and schedule a demo.
        - Select 'Enterprise' from the product dropdown
        - Check the box for 'Subscribe to newsletter'
        - Select 'Web Search' as how you heard about us
        
        Submit the form and extract the confirmation message or confirmation number.
        """,
        initial_url="https://example-forms.com/contact",  # Replace with actual URL
        browser_config=BrowserConfig(
            width=1920,
            height=1080,
            idle_timeout_minutes=5
        )
    )
    
    print("Filling and submitting form...")
    print(f"Watch live: {job.live_url}")
    
    try:
        result = job.wait_for_completion(verbose=True)
        
        if result.is_successful:
            print(f"\n✅ Form submitted successfully!")
            print(f"Confirmation: {result.output}")
        else:
            print(f"\n❌ Form submission failed: {result.error}")
    
    except TimeoutError:
        print("\n⏱️ Form submission timed out")
    
    client.close()


def authentication_flow():
    """Example: Handle authentication and protected content."""
    
    print("🔐 Authentication Flow Example")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    # Example: Login and extract protected data
    job = client.run_browser_agent(
        directive="""
        Perform the following steps:
        1. Click on 'Sign In' or 'Login' button
        2. Enter username: demo_user@example.com
        3. Enter password: DemoPass123!
        4. Click the login/submit button
        5. Wait for the dashboard to load
        6. Navigate to the 'Account Settings' or 'Profile' section
        7. Extract the account information including:
           - Account type/plan
           - Registration date
           - Usage statistics
           - Billing information (if visible)
        8. Then navigate to 'Reports' section and download the latest report
        """,
        initial_url="https://app.example.com",  # Replace with actual URL
        browser_config=BrowserConfig(
            width=1920,
            height=1080,
            max_duration_minutes=10,
            residential_ip=False
        )
    )
    
    print("Performing authentication flow...")
    print(f"Monitor progress: {job.history_url}")
    
    result = job.wait_for_completion(poll_interval=3, verbose=True)
    
    if result.is_successful:
        print("\n✅ Authentication successful!")
        print("Extracted account data:")
        print(result.output)
    else:
        print(f"\n❌ Authentication failed: {result.error}")
    
    print(f"\n💳 Credits used: {result.credits_used}")
    client.close()


def mobile_viewport_example():
    """Example: Using mobile viewport for mobile-optimized sites."""
    
    print("📱 Mobile Viewport Example")
    print("-" * 50)
    
    from tessa_sdk import BrowserAgent
    
    # Create agent with mobile viewport
    mobile_agent = BrowserAgent(
        api_key=API_KEY,
        viewport_width=375,   # iPhone viewport width
        viewport_height=667,  # iPhone viewport height
        verbose=True
    )
    
    result = mobile_agent.run(
        """Navigate to twitter.com on mobile view.
        Scroll through the feed and extract:
        - The first 5 tweets (text content)
        - Number of likes and retweets for each
        - Whether each tweet has images or videos
        """,
        initial_url="https://mobile.twitter.com"
    )
    
    if result.is_successful:
        print("\n✅ Mobile extraction successful!")
        print(result.output)
    
    print(f"\n💳 Credits used: {result.credits_used}")


def error_handling_example():
    """Example: Comprehensive error handling."""
    
    print("⚠️ Error Handling Example")
    print("-" * 50)
    
    from tessa_sdk import BrowserAgent
    from tessa_sdk.exceptions import (
        AuthenticationError,
        RateLimitError,
        JobFailedError,
        TimeoutError,
        ValidationError
    )
    
    agent = BrowserAgent(api_key=API_KEY)
    
    try:
        # This might fail in various ways
        result = agent.run(
            "Go to a-site-that-might-not-exist.com and extract data",
            timeout=30
        )
        
        if result.is_successful:
            print(f"✅ Success: {result.output}")
        else:
            print(f"⚠️ Job completed with issues: {result.error}")
    
    except AuthenticationError as e:
        print(f"🔐 Authentication failed: {e.message}")
        print("Please check your API key")
    
    except RateLimitError as e:
        print(f"🚫 Rate limit exceeded: {e.message}")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
    
    except TimeoutError as e:
        print(f"⏱️ Operation timed out after {e.timeout_seconds} seconds")
        print(f"Job ID: {e.job_id}")
    
    except JobFailedError as e:
        print(f"❌ Job failed: {e.error_message}")
        print(f"Job ID: {e.job_id}")
    
    except ValidationError as e:
        print(f"📝 Invalid request: {e.message}")
        for error in e.errors:
            print(f"  - {error}")
    
    except Exception as e:
        print(f"🔥 Unexpected error: {e}")


def main():
    """Run advanced configuration examples."""
    
    print("🚀 Tessa SDK - Advanced Configuration Examples")
    print("=" * 60)
    
    examples = {
        "1": ("Custom Browser (CDP)", custom_browser_example),
        "2": ("AI Model Comparison", different_ai_models),
        "3": ("Complex Workflow", complex_workflow),
        "4": ("Form Automation", form_automation),
        "5": ("Authentication Flow", authentication_flow),
        "6": ("Mobile Viewport", mobile_viewport_example),
        "7": ("Error Handling", error_handling_example)
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-7): ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        func()
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    # Set API key via environment variable if preferred
    # os.environ["TESSA_API_KEY"] = "YOUR_API_KEY"
    
    main()
