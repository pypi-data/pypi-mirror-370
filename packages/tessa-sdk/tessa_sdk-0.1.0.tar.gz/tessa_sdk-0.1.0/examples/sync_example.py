"""
Synchronous client examples for the Tessa SDK.

This example demonstrates using the TessaClient synchronous interface
for browser automation tasks.
"""

import os
import json
from datetime import datetime
from tessa_sdk import TessaClient, BrowserConfig, JobStatus, ActionSelectionModel
from tessa_sdk.exceptions import JobFailedError, TimeoutError, AuthenticationError

# Set your API key
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key


def basic_sync_example():
    """Basic example using the synchronous client."""
    
    print("🔄 Basic Synchronous Client Example")
    print("-" * 50)
    
    # Create a synchronous client
    client = TessaClient(api_key=API_KEY)
    
    try:
        # Start a browser agent job
        print("Starting browser agent...")
        job = client.run_browser_agent(
            directive="Go to example.com and extract the main heading and the example domain text",
            browser_config=BrowserConfig(
                width=1920,
                height=1080
            )
        )
        
        print(f"✅ Job started: {job.job_id}")
        print(f"📺 Watch live: {job.live_url}")
        print(f"📊 View history: {job.history_url}")
        
        # Check status manually
        print("\nChecking job status...")
        status = job.get_status()
        print(f"Current status: {status.status}")
        
        # Wait for completion
        print("\nWaiting for job to complete...")
        result = job.wait_for_completion(
            poll_interval=3.0,
            verbose=True
        )
        
        print(f"\n✅ Job completed successfully!")
        print(f"Output: {json.dumps(result.output, indent=2)}")
        print(f"Credits used: {result.credits_used}")
        if result.duration_seconds:
            print(f"Duration: {result.duration_seconds:.1f} seconds")
        
    except JobFailedError as e:
        print(f"❌ Job failed: {e.error_message}")
    except TimeoutError as e:
        print(f"⏱️ Job timed out after {e.timeout_seconds} seconds")
    finally:
        client.close()


def context_manager_example():
    """Example using context manager for automatic cleanup."""
    
    print("🔄 Context Manager Example")
    print("-" * 50)
    
    # Use context manager for automatic cleanup
    with TessaClient(api_key=API_KEY) as client:
        
        # Run and wait in one call
        result = client.run_and_wait(
            directive="Go to python.org and extract the latest Python version number",
            poll_interval=2.0,
            verbose=True
        )
        
        if result.is_successful:
            print(f"\n✅ Successfully extracted data!")
            print(f"Output: {result.output}")
            print(f"Credits used: {result.credits_used}")
        else:
            print(f"❌ Job failed: {result.error}")


def multiple_jobs_sequential():
    """Run multiple jobs sequentially with the sync client."""
    
    print("📋 Multiple Sequential Jobs")
    print("-" * 50)
    
    tasks = [
        {
            "name": "GitHub Trending",
            "directive": "Go to github.com/trending and extract the names of the top 3 trending repositories"
        },
        {
            "name": "Hacker News",
            "directive": "Go to news.ycombinator.com and extract the titles of the top 3 stories"
        },
        {
            "name": "Python Package",
            "directive": "Go to pypi.org and search for 'requests', then extract the latest version number"
        }
    ]
    
    results = []
    
    with TessaClient(api_key=API_KEY) as client:
        for task in tasks:
            print(f"\n🔄 Running: {task['name']}")
            print(f"   Directive: {task['directive'][:50]}...")
            
            try:
                job = client.run_browser_agent(
                    directive=task["directive"],
                    browser_config={"width": 1366, "height": 768}
                )
                
                print(f"   Job ID: {job.job_id}")
                
                # Wait for completion with timeout
                result = job.wait_for_completion(
                    poll_interval=3.0,
                    timeout=60.0,
                    verbose=False
                )
                
                results.append({
                    "task": task["name"],
                    "success": True,
                    "output": result.output,
                    "credits": result.credits_used
                })
                
                print(f"   ✅ Completed - Credits used: {result.credits_used}")
                
            except (JobFailedError, TimeoutError) as e:
                results.append({
                    "task": task["name"],
                    "success": False,
                    "error": str(e)
                })
                print(f"   ❌ Failed: {e}")
    
    # Summary
    print("\n📊 Results Summary:")
    print("-" * 30)
    successful = sum(1 for r in results if r["success"])
    total_credits = sum(r.get("credits", 0) for r in results if r["success"])
    
    print(f"Successful: {successful}/{len(tasks)}")
    print(f"Total credits used: {total_credits}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['task']}")


def job_management_example():
    """Example showing job management features."""
    
    print("🎛️ Job Management Example")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    try:
        # Start a long-running job
        job = client.run_browser_agent(
            directive="""
            Go to amazon.com and:
            1. Search for 'laptop'
            2. Apply filters: 4+ stars, Prime eligible
            3. Extract details of the first 5 results including:
               - Product name
               - Price
               - Rating
               - Number of reviews
            """,
            browser_config=BrowserConfig(
                width=1920,
                height=1080,
                residential_ip=True,
                max_duration_minutes=10
            )
        )
        
        print(f"Job started: {job.job_id}")
        print(f"Monitor at: {job.url}")
        
        # Poll status manually with custom logic
        import time
        max_attempts = 20
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            status = client.get_job_status(job.job_id)
            
            print(f"\nAttempt {attempt}/{max_attempts}")
            print(f"Status: {status.status}")
            print(f"Credits used so far: {status.credits_used or 0}")
            
            if status.status == "completed":
                print("\n✅ Job completed!")
                print(f"Final output: {json.dumps(status.output, indent=2)}")
                print(f"Total credits: {status.credits_used}")
                break
            elif status.status == "failed":
                print(f"\n❌ Job failed: {status.error}")
                break
            elif status.status == "user_taken_over":
                print("\n👤 User took control of the session")
                break
            
            time.sleep(5)
        else:
            print("\n⏱️ Max polling attempts reached")
    
    finally:
        client.close()


def different_models_comparison():
    """Compare different AI models using the sync client."""
    
    print("🤖 AI Model Comparison (Sync)")
    print("-" * 50)
    
    models = [
        ActionSelectionModel.CLAUDE_SONNET,
        ActionSelectionModel.GPT_4O,
        ActionSelectionModel.GEMINI_FLASH
    ]
    
    task = "Go to wikipedia.org and search for 'artificial intelligence', then extract a one-paragraph summary"
    
    with TessaClient(api_key=API_KEY) as client:
        for model in models:
            print(f"\n🔄 Testing model: {model.value}")
            
            try:
                start_time = datetime.now()
                
                result = client.run_and_wait(
                    directive=task,
                    browser_config={"width": 1366, "height": 768},
                    poll_interval=3.0,
                    timeout=90.0,
                    verbose=False
                )
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                print(f"✅ Success!")
                print(f"   Time: {elapsed:.1f}s")
                print(f"   Credits: {result.credits_used}")
                print(f"   Output length: {len(str(result.output))} chars")
                
            except Exception as e:
                print(f"❌ Failed: {e}")


def error_handling_example():
    """Demonstrate comprehensive error handling with sync client."""
    
    print("⚠️ Error Handling with Sync Client")
    print("-" * 50)
    
    # Test various error scenarios
    scenarios = [
        {
            "name": "Invalid API Key",
            "api_key": "INVALID_KEY_12345",
            "directive": "This will fail due to auth"
        },
        {
            "name": "Timeout Handling",
            "api_key": API_KEY,
            "directive": "Go to a very slow loading site and wait for 10 minutes",
            "timeout": 10  # Very short timeout
        },
        {
            "name": "Invalid Directive",
            "api_key": API_KEY,
            "directive": ""  # Empty directive
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        
        try:
            client = TessaClient(api_key=scenario.get("api_key", API_KEY))
            
            if scenario.get("timeout"):
                result = client.run_and_wait(
                    directive=scenario["directive"],
                    timeout=scenario["timeout"],
                    verbose=False
                )
            else:
                result = client.run_and_wait(
                    directive=scenario["directive"],
                    verbose=False
                )
            
            print(f"✅ Unexpected success: {result}")
            
        except AuthenticationError as e:
            print(f"🔐 Authentication error (expected): {e}")
        except TimeoutError as e:
            print(f"⏱️ Timeout error (expected): Job {e.job_id} timed out after {e.timeout_seconds}s")
        except JobFailedError as e:
            print(f"❌ Job failed (expected): {e.error_message}")
        except Exception as e:
            print(f"🔥 Other error: {type(e).__name__}: {e}")
        finally:
            if 'client' in locals():
                client.close()


def health_check_example():
    """Check API health using sync client."""
    
    print("🏥 API Health Check")
    print("-" * 50)
    
    with TessaClient(api_key=API_KEY) as client:
        is_healthy = client.health_check()
        
        if is_healthy:
            print("✅ API is healthy and ready!")
        else:
            print("❌ API is not responding properly")
        
        return is_healthy


def main():
    """Run sync client examples."""
    
    print("🔄 Tessa SDK - Synchronous Client Examples")
    print("=" * 60)
    
    examples = {
        "1": ("Basic Sync Example", basic_sync_example),
        "2": ("Context Manager", context_manager_example),
        "3": ("Multiple Sequential Jobs", multiple_jobs_sequential),
        "4": ("Job Management", job_management_example),
        "5": ("Model Comparison", different_models_comparison),
        "6": ("Error Handling", error_handling_example),
        "7": ("Health Check", health_check_example)
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-7) or 'all' to run all: ").strip()
    
    if choice == 'all':
        for name, func in examples.values():
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}")
            print("\nPress Enter to continue...")
            input()
    elif choice in examples:
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
