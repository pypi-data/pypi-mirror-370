"""
Async example for the Tessa SDK.

This example demonstrates how to use the async client for concurrent operations.
"""

import asyncio
import os
from typing import List
from tessa_sdk import AsyncTessaClient, JobResult

# Set your API key
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key


async def run_multiple_agents(client: AsyncTessaClient, tasks: List[str]) -> List[JobResult]:
    """Run multiple browser agents concurrently."""
    
    # Start all jobs concurrently
    jobs = []
    for i, task in enumerate(tasks):
        print(f"Starting job {i+1}: {task[:50]}...")
        job = await client.run_browser_agent(directive=task)
        jobs.append(job)
    
    print(f"\n🚀 Started {len(jobs)} jobs concurrently!")
    print("Waiting for all jobs to complete...\n")
    
    # Wait for all jobs to complete concurrently
    results = await asyncio.gather(
        *[job.wait_for_completion(verbose=True) for job in jobs],
        return_exceptions=True
    )
    
    return results


async def main():
    """Run async browser agent examples."""
    
    print("Async Browser Agent Examples")
    print("=" * 60)
    
    async with AsyncTessaClient(api_key=API_KEY) as client:
        
        # Example 1: Single async job
        print("\nExample 1: Single async job")
        print("-" * 40)
        
        job = await client.run_browser_agent(
            directive="Go to python.org and extract the latest Python version number"
        )
        
        print(f"Job started: {job.job_id}")
        print(f"Live URL: {job.live_url}")
        print(f"History URL: {job.history_url}")
        
        result = await job.wait_for_completion(verbose=True)
        
        if result.is_successful:
            print(f"✅ Result: {result.output}")
        else:
            print(f"❌ Error: {result.error}")
        
        # Example 2: Multiple concurrent jobs
        print("\nExample 2: Multiple concurrent jobs")
        print("-" * 40)
        
        tasks = [
            "Go to github.com and extract the number of repositories shown on the homepage",
            "Go to stackoverflow.com and extract the total number of questions",
            "Go to reddit.com and extract the names of the top 3 trending subreddits"
        ]
        
        results = await run_multiple_agents(client, tasks)
        
        print("\n📊 Results Summary:")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  Task {i+1}: ❌ Failed - {str(result)}")
            elif result.is_successful:
                print(f"  Task {i+1}: ✅ Success - Credits used: {result.credits_used}")
            else:
                print(f"  Task {i+1}: ❌ Failed - {result.error}")
        
        # Example 3: Parallel data extraction from multiple pages
        print("\nExample 3: Parallel extraction from multiple URLs")
        print("-" * 40)
        
        urls = [
            "https://news.ycombinator.com",
            "https://lobste.rs",
            "https://www.reddit.com/r/programming"
        ]
        
        extraction_jobs = []
        for url in urls:
            job = await client.run_browser_agent(
                directive=f"Go to {url} and extract the title of the top post",
                initial_url=url
            )
            extraction_jobs.append(job)
        
        print(f"Extracting top posts from {len(urls)} sites...")
        
        extraction_results = await asyncio.gather(
            *[job.wait_for_completion() for job in extraction_jobs],
            return_exceptions=True
        )
        
        print("\n📰 Top Posts:")
        for url, result in zip(urls, extraction_results):
            if isinstance(result, Exception):
                print(f"  {url}: Failed - {str(result)}")
            elif result.is_successful:
                print(f"  {url}: {result.output}")
            else:
                print(f"  {url}: Failed - {result.error}")
        
        # Calculate total credits used
        total_credits = sum(
            r.credits_used for r in extraction_results 
            if not isinstance(r, Exception) and r.credits_used
        )
        print(f"\n💳 Total credits used: {total_credits}")


if __name__ == "__main__":
    # Set API key via environment variable if not hardcoded
    # os.environ["TESSA_API_KEY"] = "YOUR_API_KEY"
    
    # Run the async main function
    asyncio.run(main())
