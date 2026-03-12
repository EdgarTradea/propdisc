import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_promo_code_from_text(text):
    """
    Uses Groq API (Llama3) to extract promotional data from text.
    Returns:
        dict: {"is_promo": bool, "promo_code": str or null, "discount_amount": str or null} 
              or None if error.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set.")

    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = """\
You are an intelligent data extraction assistant. 
Read the provided social media post and determine if it contains a promotional offer for a trading prop firm challenge or account.
If it is a promotional offer, extract the `promo_code` AND the `discount_amount` (e.g. '20%', '$50 off'). 
If there is no explicit promo code, set `promo_code` to null.
If it is NOT a promotional post, set `is_promo` to false.

Return ONLY a strict JSON object with these exact keys:
{
  "is_promo": boolean,
  "promo_code": string or null,
  "discount_amount": string or null
}
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model="llama3-8b-8192",
            temperature=0,  # We want deterministic, factual extraction
            max_tokens=200,
            response_format={"type": "json_object"}  # Enforce JSON mode
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        return extracted_data
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

if __name__ == "__main__":
    # Test data
    test_text = "Happy Friday traders! Get 25% off all challenges this weekend with code WEEKEND25. Don't miss out!"
    print(extract_promo_code_from_text(test_text))
