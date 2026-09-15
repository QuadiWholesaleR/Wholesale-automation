import os
import json
import asyncio
import requests
import edge_tts
from supabase import create_client, Client
from google import genai

# Read secrets safely from GitHub Actions environment
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# Optional: Direct Social API Credentials
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

supabase: Client = create_client(supabase_url, supabase_key)
ai_client = genai.Client(api_key=gemini_api_key)

VOICE = "en-US-ChristopherNeural"

async def generate_voiceover(text, output_filename):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_filename)

def post_to_facebook_page(caption):
    """Directly publishes text caption to Facebook Page via Meta Graph API."""
    if not FB_PAGE_ID or not FB_PAGE_TOKEN:
        print("Facebook credentials not found. Skipping FB auto-post.")
        return

    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {
        'message': caption,
        'access_token': FB_PAGE_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Successfully published caption to Facebook Page!")
        else:
            print(f"Facebook API Error: {response.text}")
    except Exception as e:
        print(f"Failed to post to Facebook: {e}")

def main():
    # Query single unified 'deals' table
    res = supabase.table("deals").select("*").eq("status", "ready_for_marketing").limit(1).execute()
    deals = res.data

    if not deals:
        print("No deals found marked 'ready_for_marketing'. Exiting.")
        return

    deal = deals[0]
    deal_id = str(deal.get("id", "N/A"))
    address = deal.get("address", "Undisclosed Property")
    price = deal.get("asking_price", "Contact for Price")
    details = deal.get("notes", "")

    # Multi-post prompt generating 4 distinct post variations
    prompt = f"""
    You are a real estate wholesale marketing expert. Create 4 distinct social media posts for this property:
    Property Address: {address}
    Wholesale Price: {price}
    Details: {details}

    Format output as a raw JSON array containing 4 objects. Each object must have "post_type", "script", and "caption".
    Required types:
    1. "deal_alert": Fast-paced promotional script focusing on profit spread.
    2. "educational": Trust-building educational breakdown teaching wholesale/real estate principles.
    3. "market_insight": Post highlighting why this area/market provides strong yields.
    4. "call_to_action": Short-form push encouraging buyers to join your VIP cash list.
    """

    interaction = ai_client.interactions.create(
        model='gemini-3.6-flash',
        input=prompt
    )

    response_text = interaction.output_text

    try:
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        posts = json.loads(clean_json)
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        return

    # Process all generated post variations
    for post in posts:
        script_text = post.get("script", "")
        caption_text = post.get("caption", "")
        post_type = post.get("post_type", "general")

        # 1. Generate Voiceover Audio File for each variation
        audio_filename = f"deal_{deal_id}_{post_type}.mp3"
        asyncio.run(generate_voiceover(script_text, audio_filename))

        # 2. Log generated output back to Supabase
        supabase.table("social_posts").insert({
            "deal_id": deal_id,
            "script": script_text,
            "caption": caption_text,
            "voice_id": VOICE,
            "status": "generated"
        }).execute()

        # 3. Direct Auto-Post Caption to Facebook
        post_to_facebook_page(caption_text)

    print(f"Pipeline successfully generated and logged {len(posts)} content variations for deal {deal_id}!")

if __name__ == "__main__":
    main()
