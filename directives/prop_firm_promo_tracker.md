# Prop Firm Promo Tracker SOP

## Goal
Monitor specific Prop Firm Twitter accounts, detect new promotional offers, extract any promo codes, and post a formatted message containing the promo code and an affiliate link to a Discord channel.

## Inputs
1. `state.json`: Dictionary mapping Twitter handles to the last processed Tweet ID. Example: `{"GoatFunded": "1234567890", "FTMO": "0987654321", "neomaaafunds": "1122334455"}`
2. **Environment Variables**:
   - `APIFY_API_TOKEN`
   - `GROQ_API_KEY`
   - `DISCORD_WEBHOOK_URL`
3. **Target Accounts & Affiliate Links Mapping**:
   - `@GoatFunded` -> `https://checkout.goatfundedtrader.com/aff/EdgarT/`
   - `@FTMO` -> `https://trader.ftmo.com/?affiliates=CLZBoudyNZgnFOsqWLjR`
   - `@neomaaafunds` -> `https://dashboard.neomaaa.com/challenges?affiliateId=EdgarTradea`

## Required Scripts (Execution Layer)
1. `execution/scrape_apify.py`
   - Input: List of Twitter handles and their last processed Tweet IDs.
   - Action: Use Apify API (e.g., a Twitter scraper actor) to fetch new tweets.
   - Output: List of new Tweet objects (ID, author, text, timestamp).

2. `execution/extract_promo.py`
   - Input: Tweet text.
   - Action: Use Groq API (`llama3-8b-8192` or similar) to classify if it's a promotional offer and extract the promo code. Prompt the LLM strictly to return a JSON containing `{"is_promo": bool, "promo_code": "code or null", "discount_amount": "e.g., 20% or null"}`.
   - Output: JSON extraction.

3. `execution/discord_webhook.py`
   - Input: Extracted promo data, the author, the original tweet URL, and the appropriate affiliate URL.
   - Action: Format a beautiful Discord Embed and POST it to the `DISCORD_WEBHOOK_URL`.
   - Output: Success/Failure boolean.

4. `execution/state_manager.py`
   - Action: Helper script to purely read/update `state.json`.

5. `execution/orchestrator.py`
   - Action: Combines the above scripts in a logical flow:
     1. Read state.
     2. Scrape tweets.
     3. For each new tweet, check for promos.
     4. If promo, post to Discord.
     5. Update state.

## Edge Cases
- **No new tweets**: The scraper returns empty, script terminates gracefully.
- **Malformed Tweet (No Promo Code)**: Groq might misunderstand. Ensure JSON mode and strict system prompt.
- **Apify API Limits**: Handle errors if the scraper fails or timed out.
- **Discord Rate Limits**: Sleep if Discord returns HTTP 429.
