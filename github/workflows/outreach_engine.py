import os

def send_seller_outreach(lead):
    """
    Automates multi-channel SMS and Email outreach to motivated sellers.
    Includes compliance opt-out mechanisms.
    """
    address = lead.get("address")
    mao = lead.get("mao", 0)
    owner_name = lead.get("owner_name", "Property Owner")
    
    sms_body = (
        f"Hi {owner_name}, this is Clear Wholesale Property Ventures. "
        f"We noticed your property at {address} and would love to buy it as-is for cash. "
        f"We can cover all closing costs and close in 14 days. Reply YES if open to a cash offer! "
        f"Reply STOP to unsubscribe."
    )
    
    email_body = (
        f"Subject: Cash Purchase Offer for {address}\n\n"
        f"Hello {owner_name},\n\n"
        f"Clear Wholesale Property Ventures is actively expanding in your market and purchasing properties in as-is condition.\n"
        f"We can offer roughly ${mao:,.02f} net cash to you, with zero agent fees or repair requirements.\n\n"
        f"If you are open to discussing a quick cash closing, please reply to this email or visit CWPVentures.com.\n\n"
        f"Best regards,\nClear Wholesale Property Ventures Team"
    )

    print(f"📲 [OUTREACH QUEUED] SMS to {lead.get('owner_phone')}: \"{sms_body[:60]}...\"")
    print(f"📧 [OUTREACH QUEUED] Email to {lead.get('owner_email')}")
    
    return True

def broadcast_deal_to_buyers(deal, matched_buyers):
    """
    Matches actionable deals with VIP cash buyers based on state, property type, and target criteria.
    """
    print(f"🎯 Matching Deal at {deal.get('address')} to VIP Cash Buyers...")
    
    for buyer in matched_buyers:
        msg = (
            f"🔥 EXCLUSIVE OFF-MARKET DEAL BROADCAST 🔥\n"
            f"Property: {deal.get('address')}, {deal.get('city')}, {deal.get('state')}\n"
            f"Purchase Price: ${deal.get('price'):,}\n"
            f"ARV: ${deal.get('arv'):,}\n"
            f"Est. Repairs: ${deal.get('estimated_repairs'):,}\n"
            f"Est. Profit: ${deal.get('est_profit'):,}\n\n"
            f"Reply DEAL to lock in equitable interest assignment today!"
        )
        print(f"📤 [BUYER BROADCAST] Sent deal alert to Buyer {buyer.get('name')} ({buyer.get('email')})")
