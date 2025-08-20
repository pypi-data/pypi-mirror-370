"""
Quickstart example for the Tessa SDK.

This example demonstrates the simplest way to use the SDK with one line of code.
"""

import os
from tessa_sdk import BrowserAgent

# Set your API key (or use environment variable TESSA_API_KEY)
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

def main():
    """Run a simple browser agent example."""
    
    # Example 1: One-line usage
    print("Example 1: Simple one-line extraction")
    print("-" * 50)
    
    result = BrowserAgent(API_KEY).run(
        "Go to news.ycombinator.com and extract the titles of the top 3 stories"
    )
    
    if result.is_successful:
        print("✅ Successfully extracted data!")
        print(f"Output: {result.output}")
    else:
        print(f"❌ Job failed: {result.error}")
    
    print("\n")
    
    # Example 2: Reusable agent
    print("Example 2: Reusable agent for multiple tasks")
    print("-" * 50)
    
    agent = BrowserAgent(API_KEY, verbose=True)
    
    # First task
    result1 = agent.run(
        "Go to example.com and extract the main heading text"
    )
    print(f"Task 1 result: {result1.output if result1.is_successful else result1.error}")
    
    # Second task
    result2 = agent.run(
        "Go to wikipedia.org and extract the featured article title"
    )
    print(f"Task 2 result: {result2.output if result2.is_successful else result2.error}")
    
    print("\n")
    
    # Example 3: Extract specific data from a URL
    print("Example 3: Extract specific data")
    print("-" * 50)
    
    agent = BrowserAgent(API_KEY)
    result = agent.extract(
        url="https://github.com/trending",
        data_description="repository names and star counts for the top 5 trending repositories"
    )
    
    if result.is_successful:
        print("Extracted trending repositories:")
        print(result.output)
    
    print(f"\nCredits used: {result.credits_used}")


if __name__ == "__main__":
    # You can also set the API key via environment variable
    # os.environ["TESSA_API_KEY"] = "YOUR_API_KEY"
    
    main()
