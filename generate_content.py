import os
import requests
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client, Client

# Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID") or os.environ.get("FACEBOOK_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FACEBOOK_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("INSTAGRAM_USER_ID") or os.environ.get("IG_USER_ID")
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def run_scraper_if_available():
    """Triggers scraper to populate fresh deals into Supabase before generating content."""
    try:
        from scraper import fetch_tax_delinquent_leads
        print("🔍 Running scraper to ingest real off-market deals...")
        leads = fetch_tax_delinquent_leads()
        print(f"✅ Ingested/updated {len(leads) if leads else 0} leads into Supabase.")
    except Exception as e:
        print(f"⚠️ Scraper execution warning: {e}")

def create_branded_flyer(address, price, arv, output_path="flyer.png"):
    """Generates a professional dark-themed deal flyer with bold overlay elements."""
    width, height = 1080, 1080
    image = Image.new("RGB", (width, height), color=(18, 24, 38)) # Dark modern theme
    draw = ImageDraw.Draw(image)

    # Accent Header Bar
    draw.rectangle([0, 0, width, 140], fill=(220, 38, 38)) # Red accent header
    
    # Text Overlays
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
        font_body = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 32)
    except:
        font_title = font_body = font_sub = ImageFont.load_default()

    draw.text((40, 40), "🔥 EXCLUSIVE OFF-MARKET DEAL", fill=(255, 255, 255), font=font_title)
    
    # Deal Details Card
    draw.rectangle([60, 200, width - 60, 980], fill=(30, 41, 59), outline=(71, 85, 105), width=3)
    
    draw.text((100, 260), "PROPERTY ADDRESS:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 310), str(address)[:40], fill=(255, 255, 255), font=font_body)
    
    draw.text((100, 430), "ASKING PRICE:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 480), f"${price:,}" if isinstance(price, (int, float)) else str(price), fill=(34, 197, 94), font=font_title)
    
    draw.text((100, 600), "ESTIMATED ARV:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 650), f"${arv:,}" if isinstance(arv, (int, float)) else str(arv), fill=(255, 255, 255), font=font_body)

    draw.text((100, 800), "📲 DM OR EMAIL DEALS@CWPVENTURES.COM", fill=(250, 204, 21), font=font_sub)

    image.save(output_path)
    print(f"🎨 Branded flyer saved to {output_path}")
    return output_path

def post_to_facebook(caption, image_path):
    """Posts image & caption to Facebook Page."""
    if not FB_PAGE_ID or not FB_PAGE_TOKEN:
        print("Facebook credentials missing. Skipping FB post.")
        return None

    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as img:
        payload = {"caption": caption, "access_token": FB_PAGE_TOKEN}
        files = {"source": img}
        res = requests.post(url, data=payload, files=files)
        if res.status_code == 200:
            print("✅ Successfully posted to Facebook Page!")
            return res.json().get("id")
        else:
            print(f"❌ Facebook API Error: {res.text}")
            return None

def post_to_instagram(caption, image_url):
    """Posts to linked Instagram Business account via Meta Graph API."""
    if not IG_USER_ID or not FB_PAGE_TOKEN or not image_url:
        print("Instagram configuration or public image URL missing. Skipping IG post.")
        return

    # Container Creation
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {"image_url": image_url, "caption": caption, "access_token": FB_PAGE_TOKEN}
    res = requests.post(container_url, data=payload)
    container_id = res.json().get("id")

    if container_id:
        # Publish Container
        pub_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": container_id, "access_token": FB_PAGE_TOKEN})
        if pub_res.status_code == 200:
            print("✅ Successfully published to Instagram!")
        else:
            print(f"❌ Instagram Publish Error: {pub_res.text}")

def main():
    print("🚀 Running Pipeline...")
    
    # Step 1: Run scraper to ingest real properties into Supabase
    run_scraper_if_available()

    if not supabase:
        print("Supabase client not initialized.")
        return

    # Step 2: Fetch real property from Supabase deals table
    res = supabase.table("deals").select("*").order("created_at", desc=True).limit(1).execute()
    deals = res.data

    if not deals:
        print("No deals found in Supabase table.")
        return

    deal = deals[0]
    address = deal.get("address", "Off-Market Investment Opportunity")
    price = deal.get("asking_price", 0)
    arv = deal.get("arv", 0)

    caption = (
        f"🔥 EXCLUSIVE OFF-MARKET DEAL\n\n"
        f"📍 Location: {address}\n"
        f"💰 Asking Price: {price}\n"
        f"📈 ARV: {arv}\n\n"
        f"DM or contact deals@cwpventures.com for full inspection details & walkthrough access!"
    )

    # Step 3: Create Branded Flyer
    flyer_path = create_branded_flyer(address, price, arv)

    # Step 4: Publish to Facebook
    fb_post_id = post_to_facebook(caption, flyer_path)

    # Step 5: Log to Supabase social_posts table
    try:
        supabase.table("social_posts").insert({
            "deal_id": deal.get("id"),
            "caption": caption,
            "platform": "Facebook",
            "status": "published" if fb_post_id else "failed"
        }).execute()
        print("✅ Logged post to Supabase social_posts table.")
    except Exception as e:
        print(f"Supabase logging error: {e}")

if __name__ == "__main__":
    main()
