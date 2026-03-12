import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Mapping Twitter Handles to their appropriate affiliate links
AFFILIATE_LINKS = {
    "GoatFunded": "https://checkout.goatfundedtrader.com/aff/EdgarT/",
    "FTMO": "https://trader.ftmo.com/?affiliates=CLZBoudyNZgnFOsqWLjR",
    "neomaaafunds": "https://dashboard.neomaaa.com/challenges?affiliateId=EdgarTradea"
}

def post_discord_promo_alert(tweet_author, tweet_text, tweet_url, promo_data):
    """
    Sends a beautiful embedded message to Discord with the promo code.
    """
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL is not set.")

    # Match the author handle to the correct affiliate link
    # (Handling case insensitivity just in case)
    affiliate_link = None
    firm_name = tweet_author
    for key, link in AFFILIATE_LINKS.items():
        if key.lower() == tweet_author.lower():
            affiliate_link = link
            firm_name = key
            break
    
    if not affiliate_link:
        affiliate_link = tweet_url # Fallback if for some reason handle doesn't match perfectly
        print(f"Warning: No explicit affiliate link found for {tweet_author}")

    promo_code = promo_data.get("promo_code", "No Code Needed")
    discount_amount = promo_data.get("discount_amount", "Special Offer")

    # Build the rich Discord Embed
    embed = {
        "title": f"🚨 NEW PROMO: {discount_amount} at {firm_name}! 🚨",
        "description": tweet_text,
        "url": tweet_url,
        "color": 15548997, # Redish color
        "fields": [
            {
                "name": "🔑 Promo Code",
                "value": f"**{promo_code}**",
                "inline": True
            },
            {
                "name": "🔗 Registration Link",
                "value": f"[Click here to use the offer]({affiliate_link})",
                "inline": True
            }
        ],
        "footer": {
            "text": "Automated Prop Firm Promo Tracker"
        }
    }

    payload = {
        "embeds": [embed],
        "username": "PropPromo Bot"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print(f"Successfully posted promo alert for {firm_name} to Discord.")
            return True
        else:
            print(f"Failed to post to Discord: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error posting to Discord Webhook: {e}")
        return False
