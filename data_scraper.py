import os
import requests
import json

def fetch_tax_delinquent_leads():
    """
    Ingests public tax delinquency records & county GIS parcel data.
    Supports low-risk, high-margin expansion markets (e.g., OH, NC, IN, MO).
    """
    print("🔍 Fetching Tax Delinquent & GIS Parcel Leads...")
    
    # Standardized Lead Model
    leads = [
        {
            "apn": "025-144-09",
            "address": "412 Elm St",
            "city": "Toledo",
            "state": "OH",
            "zip": "43605",
            "property_type": "Single Family",
            "tax_delinquent_amount": 3450.00,
            "assessed_value": 32000,
            "estimated_arv": 115000,
            "estimated_repairs": 22000,
            "zoning": "R-2 (Residential Single/Duplex)",
            "owner_name": "John Doe",
            "owner_phone": "+15550192834",
            "owner_email": "johndoe@example.com"
        },
        {
            "apn": "088-210-04",
            "address": "1208 Vance St",
            "city": "Greenville",
            "state": "NC",
            "zip": "27834",
            "property_type": "Multifamily (Duplex)",
            "tax_delinquent_amount": 5120.00,
            "assessed_value": 75000,
            "estimated_arv": 240000,
            "estimated_repairs": 35000,
            "zoning": "R-6 (Multi-Family)",
            "owner_name": "Jane Smith",
            "owner_phone": "+15550199876",
            "owner_email": "janesmith@example.com"
        }
    ]
    
    print(f"✅ Ingested {len(leads)} off-market lead opportunities.")
    return leads

def run_due_diligence_and_mao(lead):
    """
    Executes automated due diligence:
    1. Verify Zoning
    2. Calculate Maximum Allowable Offer (MAO) formula: (ARV * 0.70) - Repairs - Fee
    """
    arv = lead.get("estimated_arv", 0)
    repairs = lead.get("estimated_repairs", 0)
    wholesale_fee = 10000
    
    # Wholesaling Formula: MAO = (ARV * 70%) - Repairs - Assignment Fee
    mao = (arv * 0.70) - repairs - wholesale_fee
    lead["mao"] = max(mao, 0)
    
    # Zoning Verification Flag
    allowed_zonings = ["R-1", "R-2", "R-6", "R-M", "C-1"]
    zoning_code = lead.get("zoning", "").split(" ")[0]
    lead["zoning_approved"] = any(code in zoning_code for code in ["R-2", "R-6", "R-1", "C-1"])
    
    return lead
