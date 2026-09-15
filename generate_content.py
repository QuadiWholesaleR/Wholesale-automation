import os
import json
import asyncio
import edge_tts
from supabase import create_client, Client
from google import genai

# Init Clients
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

supabase: Client = create_client(supabase_url, supabase_key)
ai_client = genai.Client(api_key=gemini_api_key)

# Brand Voice ID
VOICE = "en-US-ChristopherNeural"

async def generate_voiceover(text, output_filename="voiceover.mp3"):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_filename)
    print(f"Generated voiceover: {output_filename}")

def main():
    # 1. Fetch deal from Supabase
    res = supabase.table("deals").select("*").eq("status", "ready_for_marketing").limit(1).execute()
    deals = res.data

    if not deals:
        print("No deals currently marked 'ready_for_marketing'. Exiting.")
        return

    deal = deals[0]
    deal_id = str(deal.get("id", "N/A"))
    address = deal.get("address", "Undisclosed Property")
    price = deal.get("asking_price", "Contact for Price")
    details = deal.get("notes", "")

    # 2. Generate Content using Gemini
    prompt = f"""
    You are a real estate wholesale marketing expert. Write a high-converting 30-second video script and social caption for this property deal:
    Property Address: {address}
    Wholesale Price: {price}
    Details: {details}

    Format output as JSON with two keys: "script" (for voiceover audio) and "caption" (for social media text with hashtags).
    """

    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    try:
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        script_text = data.get("script", "")
        caption_text = data.get("caption", "")
    except Exception as e:
        print("Failed to parse AI JSON, falling back to raw text.")
        script_text = f"Hot wholesale deal at {address}! Asking price {price}. DM for details."
        caption_text = response.text

    # 3. Generate Audio Voiceover
    asyncio.run(generate_voiceover(script_text, f"deal_{deal_id}.mp3"))

    # 4. Save Record to Supabase
    supabase.table("social_posts").insert({
        "deal_id": deal_id,
        "script": script_text,
        "caption": caption_text,
        "voice_id": VOICE,
        "status": "generated"
    }).execute()

    print("Successfully generated content and saved to Supabase!")

if __name__ == "__main__":
    main()
