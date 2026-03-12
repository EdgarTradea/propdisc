import time
from execution.state_manager import load_state, update_handle_state
from execution.scrape_apify import scrape_latest_tweets, TARGET_HANDLES
from execution.extract_promo import extract_promo_code_from_text
from execution.discord_webhook import post_discord_promo_alert

def main():
    print("Starting Prop Firm Promo Tracker Orchestrator...")
    
    # 1. Load the last seen state
    state = load_state()
    
    # 2. Scrape the latest tweets for the target handles
    # We scrape all handles in one go to save Apify compute units
    tweets = scrape_latest_tweets(TARGET_HANDLES, max_items=15)
    
    if not tweets:
        print("No tweets retrieved. Exiting early.")
        return

    # Sort tweets chronologically from oldest to newest to process them in order
    # (Apify returns them latest first)
    tweets.reverse()

    for tweet in tweets:
        tweet_id = tweet.get("id")
        author_handle = tweet.get("author") or "unknown_user"
        text = tweet.get("text", "")
        url = tweet.get("url", "")
        
        # Only process handles we track (case insensitively mapped)
        original_handle = None
        for th in TARGET_HANDLES:
            if author_handle and th.lower() == author_handle.lower():
                original_handle = th
                break
                
        if not original_handle:
            continue
            
        # Check against state to avoid duplicate processing
        last_seen_id = state.get(original_handle)
        
        # NOTE: String comparison for IDs might be tricky if lengths differ,
        # but Twitter IDs generally increase monotonically.
        # Direct string equality check handles exact recurrence.
        # To be completely robust, consider converting to int if it's purely digits.
        if last_seen_id and last_seen_id == tweet_id:
            continue # We already processed this one recently (or Apify returned the same one)
            
        print(f"Processing new tweet from {original_handle}: ID {tweet_id}")
        
        # 3. Use Groq to check if it's a promotional tweet
        promo_data = extract_promo_code_from_text(text)
        
        if promo_data and promo_data.get("is_promo"):
            print(f"-> Promo found! {promo_data}")
            
            # 4. Post to Discord
            success = post_discord_promo_alert(
                tweet_author=original_handle,
                tweet_text=text,
                tweet_url=url,
                promo_data=promo_data
            )
            
            if success:
                print(f"-> Discord alert sent.")
            else:
                print("-> Failed to send Discord alert. Continuing anyway to not block pipe.")
        else:
            print("-> Not a promotional tweet.")
            
        # 5. Update state tracker
        update_handle_state(original_handle, tweet_id)
        
        # Small delay to prevent rate limit spikes if multiple promos exist
        time.sleep(1)

    print("Orchestrator finished successfully.")

if __name__ == "__main__":
    main()
