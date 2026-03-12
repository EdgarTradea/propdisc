import os
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

# Map Twitter handles to Apify Actor URLs or standard format
TARGET_HANDLES = ["GoatFunded", "FTMO", "neomaaafunds"]

def scrape_latest_tweets(handles=TARGET_HANDLES, max_items=5):
    """
    Uses the Apify 'quacker/twitter-scraper' (or similar free tier scraper) 
    to fetch the latest tweets for the given handles.
    """
    if not APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN is not set in the environment.")

    client = ApifyClient(APIFY_API_TOKEN)

    # Prepare the Actor input structure (using a popular, reliable free-tier actor for Twitter)
    # Actor: apidojo/tweet-scraper
    run_input = {
        "twitterHandles": handles,
        "maxItems": max_items,
        "sort": "Latest"
    }

    try:
        # Run the Actor and wait for it to finish
        print("Starting Apify Twitter Scraper...")
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)

        # Fetch and return Actor results from the run's dataset
        print(f"Apify Scraper finished. Fetching dataset {run['defaultDatasetId']}...")
        dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()
        
        results = []
        for item in dataset_items:
            # Standardize the output format
            tweet_data = {
                "id": item.get("id"),
                "author": item.get("author", {}).get("userName"),
                "text": item.get("text"),
                "url": item.get("url"),
                "created_at": item.get("createdAt")
            }
            results.append(tweet_data)
        
        return results

    except Exception as e:
        print(f"Error scraping tweets with Apify: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    print(scrape_latest_tweets(max_items=2))
