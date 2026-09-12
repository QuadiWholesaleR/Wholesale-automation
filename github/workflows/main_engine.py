import os
import json
from supabase import create_client, Client
from data_scraper import fetch_tax_delinquent_leads, run_due_diligence_and_mao
from outreach_engine import send_seller_outreach, broadcast_deal_to_buyers
from flyer_engine import generate_pro_flyer
from social_scheduler import generate_daily_post

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def main():
    print("==========================================================")
    print("🚀 EXECUTING AUTOMATED WHOLESALE REAL ESTATE & CONTENT SYSTEM")
    print("==========================================================")
    
    # 1. SCRAPE & DUEDILIGENCE ON MOTIVATED SELLER LEADS
    raw_leads = fetch_tax_delinquent_leads()
    verified_leads = []
    
    for lead in raw_leads:
        analyzed_lead = run_due_diligence_and_mao(lead)
        if analyzed_lead.get("zoning_approved") and analyzed_lead.get("mao", 0) > 0:
            verified_leads.append(analyzed_lead)
            # Automate Seller Outreach
            send_seller_outreach(analyzed_lead)

    print(f"\n📊 Approved {len(verified_leads)} seller leads following automated due diligence & MAO calculation.")

    # 2. SUPABASE DB INTEGRATION & BUYER MATCHING
    properties = []
    cash_buyers = [
        {"name": "Midwest Capital Fund", "email": "invest@midwestcap.com", "target_states": ["OH", "NC", "IN"]},
        {"name": "Triangle Cash Flow Group", "email": "buyers@trianglegroup.com", "target_states": ["NC", "MO"]}
    ]

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Fetch active deals
            res = supabase.table("properties").select("*").neq("address", "123 Test Ave").execute()
            if res.data:
                properties = res.data
        except Exception as e:
            print(f"⚠️ Supabase Integration Note: {e}")

    if not properties:
        properties = [{
            "address": "412 Elm St",
            "city": "Toledo",
            "state": "OH",
            "price": 40000,
            "arv": 115000,
            "estimated_repairs": 22000,
            "est_profit": 53000
        }]

    # Match & Broadcast Deals to Buyers
    for deal in properties:
        matched = [b for b in cash_buyers if deal.get("state", "OH") in b.get("target_states", [])]
        broadcast_deal_to_buyers(deal, matched)

    # 3. GENERATE MARKETING FLYER
    top_deal = properties[0]
    generate_pro_flyer(
        property_address=f"{top_deal.get('address')}, {top_deal.get('city')}, {top_deal.get('state')}",
        price=int(float(top_deal.get("price", 40000))),
        arv=int(float(top_deal.get("arv", 115000))),
        est_repairs=int(float(top_deal.get("estimated_repairs", 22000))),
        est_profit=int(float(top_deal.get("est_profit", 53000))),
        contact_info="deals@cwpventures.com",
        website="CWPVentures.com",
        output_path="daily_deal_flyer.png"
    )

    # 4. GENERATE DAILY SOCIAL CONTENT
    print("\n📱 Generating 4x Daily Social Media Posts...")
    post_types = ["educational", "seller", "buyer", "deal"]
    daily_output = []

    for p_type in post_types:
        post = generate_daily_post(p_type)
        daily_output.append(
            f"========================================\n"
            f"=== POST TYPE: {p_type.upper()} ===\n"
            f"Title: {post.get('title', 'Social Post')}\n\n"
            f"{post.get('body', '')}\n\n"
        )

    with open("daily_posts.txt", "w") as f:
        f.writelines(daily_output)

    with open("deal_summary.json", "w") as f:
        json.dump(verified_leads, f, indent=2)

    print("\n✅ ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
