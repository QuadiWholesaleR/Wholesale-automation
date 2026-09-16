import os
import json
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client, Client
from google import genai

# Setup API Credentials
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")
fb_page_id = os.environ.get("FB_PAGE_ID") or os.environ.get("FACEBOOK_PAGE_ID")
fb_page_token = os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FACEBOOK_ACCESS_TOKEN")

supabase: Client = create_client(supabase_url, supabase_key)
ai_client = genai.Client(api_key=gemini_api_key)

def create_social_graphic(title, body_text, output_filename="social_card.png"):
    """Generates a styled 1080x1080 branded social media graphic card."""
    img = Image.new('RGB', (1080, 1080), color='#0F172A')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Header Banner
    draw.rectangle([0, 0, 1080, 140], fill='#1E293B')
    draw.text((50, 50), title.upper(), fill='#F8FAFC', font=font)
    
    # Body Text
    draw.text((50, 200), body_text, fill='#E2E8F0', font=font)
    img.save(output_filename)
    return output_filename

def generate_deal_flyer(deal_data, output_path="daily_deal_flyer.png"):
    """Generates a deal flyer embedding property image directly."""
    flyer = Image.new('RGB', (1080, 1350), color='#FFFFFF')
    draw = ImageDraw.Draw(flyer)
    font = ImageFont.load_default()
    
    # Fetch real property image or create fallback placeholder
    image_url = deal_data.get('image_url')
    if image_url:
        try:
            res = requests.get(image_url, timeout=10)
            prop_img = Image.open(BytesIO(res.content)).convert('RGB')
            prop_img = prop_img.resize((1000, 600))
            flyer.paste(prop_img, (40, 180))
        except Exception as e:
            print(f"Could not load image URL, using placeholder: {e}")
            draw.rectangle([40, 180, 1040, 780], fill='#E2E8F0')
            draw.text((400, 470), "PROPERTY PHOTO", fill='#64748B', font=font)
    else:
        draw.rectangle([40, 180, 1040, 780], fill='#E2E8F0')
        draw.text((400, 470), "PROPERTY PHOTO", fill='#64748B', font=font)
    
    # Text overlays
    draw.text((40, 50), f"OFF-MARKET DEAL: {deal_data.get('address', 'Atlanta Deal')}", fill='#0F172A', font=font)
    draw.text((40, 820), f"Asking Price: {deal_data.get('asking_price', 'Contact')}", fill='#16A34A', font=font)
    draw.text((40, 880), f"Est. ARV: {deal_data.get('arv', 'N/A')}", fill='#0284C7', font=font)
    
    flyer.save(output_path)
    return output_path

def post_image_to_facebook(image_path, caption):
    """Posts a rendered image file directly to Facebook Page via Graph API."""
    if not fb_page_id or not fb_page_token:
        print("Facebook secrets missing. Skipping live post.")
        return
        
    url = f"https://graph.facebook.com/v19.0/{fb_page_id}/photos"
    payload = {'message': caption, 'access_token': fb_page_token}
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            res = requests.post(url, data=payload, files=files)
            if res.status_code == 200:
                print("✓ Successfully posted image flyer directly to Facebook Page!")
            else:
                print(f"Facebook Graph API Error: {res.text}")
    except Exception as e:
        print(f"Failed to publish to Facebook: {e}")

def main():
    print("🚀 Running Wholesale Engine & Social Machine...")
    
    # Fetch from unified 'deals' table
    res = supabase.table("deals").select("*").eq("status", "ready_for_marketing").limit(1).execute()
    deals = res.data

    if not deals:
        print("No active marketing deals found in 'deals' table.")
        return

    deal = deals[0]
    
    # 1. Create Property Image Flyer
    flyer_path = generate_deal_flyer(deal)
    
    # 2. Build Caption
    caption = f"🔥 OFF-MARKET DEAL: {deal.get('address')}\n" \
              f"Asking Price: {deal.get('asking_price')}\n" \
              f"Details: {deal.get('notes')}\n\n" \
              f"DM us or email deals@cwpventures.com for access!"
              
    # 3. Post Flyer Image Directly to Social Media
    post_image_to_facebook(flyer_path, caption)
    print("Pipeline Execution Complete!")

if __name__ == "__main__":
    main()
