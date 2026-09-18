import os
import requests
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID") or os.environ.get("FACEBOOK_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FACEBOOK_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("INSTAGRAM_USER_ID") or os.environ.get("IG_USER_ID")
TIKTOK_ACCOUNT_ID = os.environ.get("TIKTOK_ACCOUNT_ID")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def run_scraper_if_available():
    try:
        import scraper
        print("🔍 Running scraper module...")
        leads = scraper.fetch_tax_delinquent_leads()
        print(f"✅ Ingested {len(leads) if leads else 0} real leads into Supabase.")
    except Exception as e:
        print(f"⚠️ Scraper execution warning: {e}")

def create_branded_flyer(address, price, arv, output_path="flyer.png"):
    width, height = 1080, 1080
    image = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(image)

    # Accent Header Bar
    draw.rectangle([0, 0, width, 140], fill=(220, 38, 38))
    
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        font_body = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 30)
    except:
        font_title = font_body = font_sub = ImageFont.load_default()

    draw.text((40, 45), "🔥 EXCLUSIVE OFF-MARKET DEAL", fill=(255, 255, 255), font=font_title)
    
    # Details Box
    draw.rectangle([60, 200, width - 60, 980], fill=(30, 41, 59), outline=(71, 85, 105), width=3)
    
    draw.text((100, 260), "PROPERTY ADDRESS:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 310), str(address)[:42], fill=(255, 255, 255), font=font_body)
    
    draw.text((100, 430), "ASKING PRICE:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 480), f"${price:,}" if isinstance(price, (int, float)) else str(price), fill=(34, 197, 94), font=font_title)
    
    draw.text((100, 600), "ESTIMATED ARV:", fill=(148, 163, 184), font=font_sub)
    draw.text((100, 650), f"${arv:,}" if isinstance(arv, (int, float)) else str(arv), fill=(255, 255, 255), font=font_body)

    draw.text((100, 800), "📲 DM OR EMAIL DEALS@CWPVENTURES.COM", fill=(250, 204, 21), font=font_sub)

    image.save(output_path)
    return output_path

def post_to_facebook(caption, image_path):
    if not FB_PAGE_ID or not FB_PAGE_TOKEN:
        print("Facebook credentials missing.")
        return None

    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as img:
        res = requests.post(url, data={"caption": caption, "access_token": FB_PAGE_TOKEN}, files={"source": img})
        if res.status_code == 200:
            print("✅ Successfully posted image flyer directly to Facebook Page!")
            return res.json().get("id")
        else:
            print(f"Facebook API Error: {res.text}")
            return None

def handle_tiktok_posting(caption):
    if TIKTOK_ACCOUNT_ID:
        print(f"ℹ️ TikTok Account ID detected ({TIKTOK_ACCOUNT_ID}). Skipping API post until TikTok App Review approval.")
    else:
        print("ℹ️ TIKTOK_ACCOUNT_ID missing in GitHub Secrets.")

def main():
    print("🚀 Running Pipeline...")
    run_scraper_if_available()

    if not supabase:
        print("Supabase client not initialized.")
        return

    res = supabase.table("deals").select("*").eq("status", "ready_for_marketing").order("created_at", desc=True).limit(1).execute()
    deals = res.data

    if not deals:
        print("No active deals in Supabase.")
        return

    deal = deals[0]
    address = deal.get("address")
    price = deal.get("asking_price", 0)
    arv = deal.get("arv", 0)

    caption = (
        f"🔥 EXCLUSIVE OFF-MARKET DEAL\n\n"
        f"📍 Location: {address}\n"
        f"💰 Asking Price: ${price:,}\n"
        f"📈 ARV: ${arv:,}\n\n"
        f"DM or contact deals@cwpventures.com for full inspection details & walkthrough access!"
    )

    flyer_path = create_branded_flyer(address, price, arv)
    fb_post_id = post_to_facebook(caption, flyer_path)
    handle_tiktok_posting(caption)

    try:
        supabase.table("social_posts").insert({
            "deal_id": deal.get("id"),
            "caption": caption,
            "platform": "Facebook",
            "status": "published" if fb_post_id else "failed"
        }).execute()
        print("✅ Logged post entry to Supabase social_posts table.")
    except Exception as e:
        print(f"Supabase logging warning: {e}")

if __name__ == "__main__":
    main()
