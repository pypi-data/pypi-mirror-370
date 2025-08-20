"""
Web scraping examples using the Tessa SDK.

This example demonstrates various web scraping scenarios.
"""

import os
import json
from datetime import datetime
from tessa_sdk import TessaClient, BrowserConfig

# Set your API key
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key


def scrape_ecommerce_products():
    """Example: Scrape product information from an e-commerce site."""
    
    print("📦 E-commerce Product Scraping")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    job = client.run_browser_agent(
        directive="""
        Search for 'laptop' and extract information for the first 10 products including:
        - Product name
        - Price
        - Rating (if available)
        - Number of reviews
        - Availability status
        - Product URL
        Format the results as a structured list.
        """,
        initial_url="https://www.amazon.com",
        browser_config=BrowserConfig(
            width=1920,
            height=1080,
            residential_ip=True,  # Use residential IP for e-commerce sites
            max_duration_minutes=10
        )
    )
    
    print(f"Job started: {job.job_id}")
    print(f"Watch live: {job.live_url}")
    print("Waiting for completion...")
    
    result = job.wait_for_completion(verbose=True)
    
    if result.is_successful:
        print("\n✅ Successfully scraped products!")
        print(json.dumps(result.output, indent=2))
        
        # Save to file
        with open(f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(result.output, f, indent=2)
        print("\n📁 Results saved to file")
    else:
        print(f"\n❌ Scraping failed: {result.error}")
    
    print(f"Credits used: {result.credits_used}")
    client.close()


def scrape_news_articles():
    """Example: Scrape news articles from multiple sources."""
    
    print("📰 News Article Scraping")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    news_sources = [
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com",
            "directive": "Extract the headlines, authors, and publish dates of the top 5 articles on the homepage"
        },
        {
            "name": "The Verge",
            "url": "https://www.theverge.com",
            "directive": "Extract the headlines and brief descriptions of the top 5 stories"
        },
        {
            "name": "Ars Technica",
            "url": "https://arstechnica.com",
            "directive": "Extract the titles and categories of the latest 5 articles"
        }
    ]
    
    all_articles = {}
    
    for source in news_sources:
        print(f"\n🔍 Scraping {source['name']}...")
        
        job = client.run_browser_agent(
            directive=source["directive"],
            initial_url=source["url"],
            browser_config={"width": 1366, "height": 768}
        )
        
        result = job.wait_for_completion(poll_interval=3)
        
        if result.is_successful:
            all_articles[source["name"]] = result.output
            print(f"✅ Successfully scraped {source['name']}")
        else:
            print(f"❌ Failed to scrape {source['name']}: {result.error}")
    
    # Display summary
    print("\n📊 Scraping Summary:")
    print("-" * 30)
    for source_name, articles in all_articles.items():
        print(f"{source_name}: {len(articles) if isinstance(articles, list) else 'Data extracted'}")
    
    client.close()
    return all_articles


def scrape_social_media_stats():
    """Example: Scrape social media statistics and trends."""
    
    print("📱 Social Media Stats Scraping")
    print("-" * 50)
    
    from tessa_sdk import BrowserAgent
    
    agent = BrowserAgent(
        api_key=API_KEY,
        residential_ip=True,  # Often needed for social media
        verbose=True
    )
    
    # Example: Get Twitter/X trending topics
    print("\n🐦 Extracting Twitter/X trends...")
    twitter_result = agent.run(
        "Go to x.com/explore and extract the top 10 trending topics with their tweet counts",
        initial_url="https://x.com/explore"
    )
    
    if twitter_result.is_successful:
        print("Trending topics:", twitter_result.output)
    
    # Example: Get YouTube video stats
    print("\n📺 Extracting YouTube video statistics...")
    youtube_result = agent.run(
        """Navigate to youtube.com, search for 'Python tutorial', 
        and extract the view counts, channel names, and upload dates 
        for the top 5 results""",
        initial_url="https://youtube.com"
    )
    
    if youtube_result.is_successful:
        print("YouTube results:", youtube_result.output)
    
    return {
        "twitter_trends": twitter_result.output if twitter_result.is_successful else None,
        "youtube_stats": youtube_result.output if youtube_result.is_successful else None
    }


def scrape_job_listings():
    """Example: Scrape job listings with filtering."""
    
    print("💼 Job Listings Scraping")
    print("-" * 50)
    
    from tessa_sdk import BrowserAgent
    
    agent = BrowserAgent(api_key=API_KEY)
    
    # Search for specific jobs
    result = agent.run(
        """Go to indeed.com and search for 'Python Developer' jobs in 'San Francisco, CA'.
        Apply the following filters:
        - Remote jobs only
        - Posted in the last 7 days
        - Salary $100k+
        
        Then extract for the first 10 results:
        - Job title
        - Company name
        - Salary range (if shown)
        - Job type (full-time, contract, etc.)
        - Key requirements (first 3 bullet points)
        - Application URL
        """,
        initial_url="https://indeed.com",
        timeout=180  # 3 minutes for complex filtering
    )
    
    if result.is_successful:
        print("\n✅ Job listings extracted!")
        
        # Process and display results
        jobs = result.output
        if isinstance(jobs, dict) and "jobs" in jobs:
            jobs = jobs["jobs"]
        elif not isinstance(jobs, list):
            jobs = [jobs]
        
        for i, job in enumerate(jobs[:5], 1):  # Show first 5
            print(f"\n{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            if 'salary' in job:
                print(f"   Salary: {job['salary']}")
            print(f"   Type: {job.get('type', 'N/A')}")
    
    print(f"\n💳 Credits used: {result.credits_used}")
    return result


def scrape_real_estate():
    """Example: Scrape real estate listings with specific criteria."""
    
    print("🏠 Real Estate Listings Scraping")
    print("-" * 50)
    
    client = TessaClient(api_key=API_KEY)
    
    # Complex real estate search
    job = client.run_browser_agent(
        directive="""
        Go to zillow.com and search for homes in Austin, TX with these criteria:
        - For sale
        - Single family homes
        - 3+ bedrooms
        - 2+ bathrooms
        - Price range: $400k - $600k
        - Built after 2000
        
        Extract the following for the first 15 listings:
        - Address
        - Price
        - Bedrooms and bathrooms count
        - Square footage
        - Lot size
        - Year built
        - Days on Zillow
        - Monthly estimated payment
        - Zillow URL
        
        Sort by newest listings first if possible.
        """,
        browser_config=BrowserConfig(
            width=1920,
            height=1080,
            residential_ip=True,
            max_duration_minutes=15
        )
    )
    
    print(f"Scraping real estate listings...")
    print(f"Live view: {job.live_url}")
    
    result = job.wait_for_completion(poll_interval=5, verbose=True)
    
    if result.is_successful:
        print("\n✅ Successfully scraped listings!")
        
        # Save to CSV-like format
        import csv
        from datetime import datetime
        
        filename = f"austin_homes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if isinstance(result.output, list) and len(result.output) > 0:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=result.output[0].keys())
                writer.writeheader()
                writer.writerows(result.output)
            print(f"📁 Saved {len(result.output)} listings to {filename}")
    
    client.close()
    return result


def main():
    """Run web scraping examples."""
    
    print("🌐 Tessa SDK - Web Scraping Examples")
    print("=" * 60)
    
    # Choose which example to run
    examples = {
        "1": ("E-commerce Products", scrape_ecommerce_products),
        "2": ("News Articles", scrape_news_articles),
        "3": ("Social Media Stats", scrape_social_media_stats),
        "4": ("Job Listings", scrape_job_listings),
        "5": ("Real Estate", scrape_real_estate)
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-5) or 'all' to run all: ").strip()
    
    if choice == 'all':
        for name, func in examples.values():
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}")
    elif choice in examples:
        name, func = examples[choice]
        func()
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    # Set API key via environment variable if preferred
    # os.environ["TESSA_API_KEY"] = "YOUR_API_KEY"
    
    main()
