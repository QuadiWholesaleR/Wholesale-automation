import os
from PIL import Image, ImageDraw, ImageFont

def generate_pro_flyer(property_address, price, arv, est_repairs, est_profit, contact_info, website, output_path="daily_deal_flyer.png"):
    width, height = 1080, 1350
    canvas = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(canvas)

    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    
    def get_font(size):
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        except:
            return ImageFont.load_default()

    font_brand = get_font(28)
    font_title = get_font(44)
    font_sub = get_font(24)
    font_addr = get_font(36)
    font_price = get_font(62)
    font_label = get_font(22)
    font_body = get_font(28)
    font_cta = get_font(36)
    font_footer = get_font(18)

    # --- TOP BRAND HEADER BAR ---
    draw.rectangle([(0, 0), (width, 160)], fill="#2563EB")
    draw.text((width // 2, 40), "CLEAR WHOLESALE PROPERTY VENTURES", fill="#FEF08A", font=font_brand, anchor="mm")
    draw.text((width // 2, 85), "🔥 EXCLUSIVE OFF-MARKET DEAL 🔥", fill="#FFFFFF", font=font_title, anchor="mm")
    draw.text((width // 2, 130), "EQUITABLE CONTRACT ASSIGNMENT | CASH BUYERS ONLY", fill="#E0F2FE", font=font_sub, anchor="mm")

    # --- PROPERTY PHOTO PLACEHOLDER BOX ---
    draw.rectangle([(40, 180), (width - 40, 600)], fill="#F1F5F9", outline="#E2E8F0", width=3)
    draw.text((width // 2, 390), "[ PROPERTY PHOTO / MAP LOCATION ]", fill="#0F172A", font=font_sub, anchor="mm")

    # --- ADDRESS BAR OVERLAY ---
    draw.rectangle([(40, 530), (width - 40, 600)], fill="#0F172A")
    draw.text((width // 2, 565), str(property_address).upper(), fill="#FEF08A", font=font_addr, anchor="mm")

    # --- HERO METRICS (GREEN & BLUE) ---
    draw.rectangle([(40, 620), (520, 800)], fill="#10B981")
    draw.text((280, 665), "INVESTOR ASSIGNMENT PRICE", fill="#ECFDF5", font=font_label, anchor="mm")
    draw.text((280, 735), f"${price:,}", fill="#FFFFFF", font=font_price, anchor="mm")

    draw.rectangle([(560, 620), (1040, 800)], fill="#1D4ED8")
    draw.text((800, 665), "AFTER REPAIR VALUE (ARV)", fill="#E0F2FE", font=font_label, anchor="mm")
    draw.text((800, 735), f"${arv:,}", fill="#FEF08A", font=font_price, anchor="mm")

    # --- FINANCIAL BREAKDOWN CARD ---
    draw.rectangle([(40, 820), (1040, 1080)], fill="#F8FAFC", outline="#CBD5E1", width=3)
    
    y = 860
    metrics = [
        ("Estimated Repair Budget:", f"${est_repairs:,}", "#0F172A"),
        ("Estimated Spread / Potential Profit:", f"${est_profit:,}", "#047857"),
        ("Contract Assignment:", "Equitable Interest Assignment", "#0F172A"),
        ("Access Status:", "Vacant / Lockbox Available", "#0F172A"),
    ]

    for label, val, val_color in metrics:
        draw.text((80, y), label, fill="#475569", font=font_body)
        draw.text((1000, y), val, fill=val_color, font=font_body, anchor="ra")
        draw.line([(80, y + 48), (1000, y + 48)], fill="#E2E8F0", width=2)
        y += 60

    # --- CALL TO ACTION BOX ---
    draw.rectangle([(40, 1100), (1040, 1260)], fill="#DC2626")
    draw.text((width // 2, 1145), "LOCK IN THIS DEAL TODAY!", fill="#FFFFFF", font=font_cta, anchor="mm")
    draw.text((width // 2, 1205), f"Email: {contact_info}  |  Web: {website}", fill="#FEF08A", font=font_sub, anchor="mm")

    # --- FOOTER ---
    disclaimer = (
        "Clear Wholesale Property Ventures | CWPVentures.com\n"
        "DISCLAIMER: Marketing equitable interest in purchase contract. Not acting as a licensed real estate broker.\n"
        "Property offered as-is. Cash or hard money buyers only. Buyer to conduct independent due diligence."
    )
    draw.text((width // 2, 1300), disclaimer, fill="#64748B", font=font_footer, anchor="mm", align="center")

    canvas.save(output_path, "PNG")
    print(f"🎨 Generated professional deal flyer: {output_path}")
