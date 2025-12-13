# constants.py - ZETA CARBON INTELLIGENCE v5.0
# Complete constants mapping with all countries, factors, and formulas
# Last updated: December 2025

import re
import pandas as pd

# ============================================================================
# CREATIVE WEIGHTS (MB) - Par format de publicité
# ============================================================================

CREATIVE_WEIGHTS = {
    # Desktop - Rectangles
    "200x200": 0.12,
    "250x250": 0.15,
    "300x250": 0.35,
    "336x280": 0.40,
    "728x90": 0.25,
    "970x90": 0.30,
    "970x250": 0.50,
    "160x600": 0.28,
    "120x600": 0.18,
    "300x600": 0.45,
    "300x1050": 0.65,
    
    # Mobile
    "320x50": 0.12,
    "320x100": 0.18,
    "300x50": 0.12,
    "480x320": 0.30,
    "320x480": 0.32,
    "640x1136": 0.60,
    "750x1334": 0.65,
    "1080x1920": 0.80,
    
    # Generic formats
    "Video": 3.0,
    "Video HD": 4.5,
    "Video SD": 1.5,
    "Display": 0.25,
    "Banner": 0.25,
    "Native": 0.15,
    "Audio": 1.0,
    "Podcast": 1.5,
    "DOOH": 0.01,
    "Digital Out-of-Home": 0.01,
    "Masthead": 4.0,
    "Instream Video": 3.0,
    "Outstream Video": 2.5,
    "Bumper Video": 1.0,
    "TrueView Video": 2.5,
    "Rewarded Video": 3.5,
    "Unknown": 0.3,
}

# ============================================================================
# NETWORK FACTORS (gCO2/MB)
# ============================================================================

NETWORK_FACTORS = {
    "WiFi": 0.018,      # 18 gCO2/GB
    "Fiber": 0.018,
    "Fixed": 0.018,
    "4G": 0.050,        # 50 gCO2/GB
    "5G": 0.035,
    "Cellular": 0.050,
    "Mobile": 0.050,
    "Unknown": 0.025,
}

# ============================================================================
# DEVICE FACTORS (Power consumption multipliers)
# ============================================================================

DEVICE_FACTORS = {
    "Desktop": 1.0,
    "Laptop": 1.0,
    "Mobile": 0.6,
    "Tablet": 0.75,
    "CTV": 2.5,
    "TV": 2.5,
    "Unknown": 0.8,
}

# ============================================================================
# ADTECH FACTORS (Supply path efficiency multipliers)
# ============================================================================

ADTECH_FACTORS = {
    "Direct": 1.0,
    "Google": 1.0,
    "Facebook": 1.0,
    "Amazon": 1.0,
    "Tier 1": 1.0,
    "PubMatic": 1.5,
    "OpenX": 1.5,
    "Magnite": 1.5,
    "Tier 2": 1.5,
    "Tier 3": 2.5,
    "Other": 2.0,
    "Unknown": 1.8,
}

# ============================================================================
# BENCHMARK BANDS (gCO2PM par format)
# ============================================================================

BENCHMARK_BANDS = {
    "Video": {"green": 80, "good": 150, "high": 250},
    "Display": {"green": 50, "good": 150, "high": 300},
    "Native": {"green": 40, "good": 100, "high": 200},
    "Audio": {"green": 45, "good": 120, "high": 250},
    "DOOH": {"green": 0.05, "good": 0.15, "high": 0.5},
    "Default": {"green": 100, "good": 300, "high": 600},
}

# ============================================================================
# US STATE GRID INTENSITY (gCO2/kWh) - 2024 data
# ============================================================================

US_STATE_GRID_INTENSITY = {
    "AL": 450, "AK": 180, "AZ": 420, "AR": 520, "CA": 220,
    "CO": 480, "CT": 280, "DE": 350, "FL": 450, "GA": 420,
    "HI": 600, "ID": 150, "IL": 280, "IN": 520, "IA": 450,
    "KS": 480, "KY": 620, "LA": 550, "ME": 280, "MD": 350,
    "MA": 300, "MI": 420, "MN": 380, "MS": 520, "MO": 520,
    "MT": 280, "NE": 500, "NV": 380, "NH": 350, "NJ": 320,
    "NM": 480, "NY": 180, "NC": 420, "ND": 400, "OH": 580,
    "OK": 450, "OR": 200, "PA": 380, "RI": 300, "SC": 420,
    "SD": 450, "TN": 450, "TX": 420, "UT": 380, "VT": 220,
    "VA": 380, "WA": 180, "WV": 650, "WI": 400, "WY": 550,
    "DC": 350,
}

# ============================================================================
# GRID INTENSITY BY COUNTRY (gCO2/kWh) - 2024 data from Ember, IEA, NESO
# ============================================================================

GRID_INTENSITY = {
    # Europe - Low carbon
    "NO": 12, "NORWAY": 12,
    "IS": 25, "ICELAND": 25,
    "SE": 55, "SWEDEN": 55,
    "FI": 80, "FINLAND": 80,
    "LU": 85, "LUXEMBOURG": 85,
    "FR": 50, "FRANCE": 50,
    "AT": 120, "AUSTRIA": 120,
    "CH": 35, "SWITZERLAND": 35,
    "PT": 220, "PORTUGAL": 220,
    "DK": 150, "DENMARK": 150,
    "ES": 250, "SPAIN": 250,
    
    # Europe - Medium carbon
    "GB": 124, "UK": 124, "UNITED KINGDOM": 124,
    "IT": 380, "ITALY": 380,
    "GR": 380, "GREECE": 380,
    "TR": 500, "TURKEY": 500,
    "PL": 680, "POLAND": 680,
    "DE": 350, "GERMANY": 350,
    "NL": 380, "NETHERLANDS": 380,
    "BE": 200, "BELGIUM": 200,
    "CZ": 380, "CZECHIA": 380, "CZECH REPUBLIC": 380,
    "SK": 350, "SLOVAKIA": 350,
    "RO": 420, "ROMANIA": 420,
    "HR": 300, "CROATIA": 300,
    "HU": 380, "HUNGARY": 380,
    "SI": 280, "SLOVENIA": 280,
    "BG": 750, "BULGARIA": 750,
    "EE": 900, "ESTONIA": 900,
    "LV": 180, "LATVIA": 180,
    "LT": 280, "LITHUANIA": 280,
    "IE": 200, "IRELAND": 200,
    
    # North America
    "CA": 180, "CANADA": 180,
    "US": 384, "USA": 384, "UNITED STATES": 384,
    "MX": 420, "MEXICO": 420,
    
    # Latin America
    "BR": 103, "BRAZIL": 103,
    "AR": 380, "ARGENTINA": 380,
    "CL": 280, "CHILE": 280,
    "CO": 250, "COLOMBIA": 250,
    "PE": 320, "PERU": 320,
    "EC": 200, "ECUADOR": 200,
    "VE": 180, "VENEZUELA": 180,
    "BO": 350, "BOLIVIA": 350,
    "PY": 45, "PARAGUAY": 45,
    "UY": 80, "URUGUAY": 80,
    
    # Asia Pacific
    "AU": 680, "AUSTRALIA": 680,
    "NZ": 180, "NEW ZEALAND": 180,
    "JP": 482, "JAPAN": 482,
    "SG": 420, "SINGAPORE": 420,
    "KR": 450, "SOUTH KOREA": 450, "KOREA": 450,
    "TH": 550, "THAILAND": 550,
    "MY": 580, "MALAYSIA": 580,
    "ID": 700, "INDONESIA": 700,
    "PH": 450, "PHILIPPINES": 450,
    "VN": 600, "VIETNAM": 600,
    "TW": 520, "TAIWAN": 520,
    "HK": 580, "HONG KONG": 580,
    "PK": 650, "PAKISTAN": 650,
    "BD": 650, "BANGLADESH": 650,
    "LK": 450, "SRI LANKA": 450,
    "TH": 550, "THAILAND": 550,
    
    # China & India
    "CN": 640, "CHINA": 640,
    "IN": 708, "INDIA": 708,
    
    # Middle East & Africa
    "SA": 700, "SAUDI ARABIA": 700,
    "AE": 650, "UNITED ARAB EMIRATES": 650,
    "IL": 500, "ISRAEL": 500,
    "ZA": 900, "SOUTH AFRICA": 900,
    "EG": 550, "EGYPT": 550,
    "NG": 600, "NIGERIA": 600,
    "KE": 400, "KENYA": 400,
    "MA": 450, "MOROCCO": 450,
    "TN": 550, "TUNISIA": 550,
    "KW": 650, "KUWAIT": 650,
    "QA": 650, "QATAR": 650,
    "BH": 600, "BAHRAIN": 600,
    "OM": 700, "OMAN": 700,
    "JO": 480, "JORDAN": 480,
    "LB": 500, "LEBANON": 500,
    
    # Russia & Central Asia
    "RU": 449, "RUSSIA": 449,
    "KZ": 550, "KAZAKHSTAN": 550,
    "UZ": 420, "UZBEKISTAN": 420,
    "TK": 500, "TURKMENISTAN": 500,
    "KG": 350, "KYRGYZSTAN": 350,
    
    # Eastern Europe
    "UA": 380, "UKRAINE": 380,
    "BY": 320, "BELARUS": 320,
    "MD": 400, "MOLDOVA": 400,
    "RS": 450, "SERBIA": 450,
    "BA": 380, "BOSNIA": 380,
    "MK": 400, "MACEDONIA": 400,
    "AL": 350, "ALBANIA": 350,
    "ME": 350, "MONTENEGRO": 350,
    "XK": 400, "KOSOVO": 400,
    
    # Africa
    "CI": 350, "IVORY COAST": 350,
    "GH": 400, "GHANA": 400,
    "TZ": 350, "TANZANIA": 350,
    "UG": 300, "UGANDA": 300,
    "RW": 150, "RWANDA": 150,
    "ET": 200, "ETHIOPIA": 200,
    "SD": 500, "SUDAN": 500,
    "DZ": 450, "ALGERIA": 450,
    
    # Southeast Asia
    "MM": 650, "MYANMAR": 650,
    "KH": 600, "CAMBODIA": 600,
    "LA": 700, "LAOS": 700,
    
    # South Asia
    "NP": 250, "NEPAL": 250,
    "BT": 100, "BHUTAN": 100,
    "AF": 550, "AFGHANISTAN": 550,
    "IR": 650, "IRAN": 650,
    "IQ": 700, "IRAQ": 700,
    "SY": 600, "SYRIA": 600,
    
    # Europe additional
    "GE": 400, "GEORGIA": 400,
    "AM": 350, "ARMENIA": 350,
    "AZ": 450, "AZERBAIJAN": 450,
    
    # Global fallback
    "DEFAULT": 473,
    "WORLD": 473,
    "GLOBAL": 473,
}

# Legacy backward compatibility
GRID_INTENSITY_BY_COUNTRY = GRID_INTENSITY

# ============================================================================
# EXCHANGE TIER MAPPING
# ============================================================================

EXCHANGE_TIER_MAPPING = {
    "googleadx": "Tier 1",
    "doubleclick": "Tier 1",
    "appnexus": "Tier 1",
    "rubicon": "Tier 2",
    "pubmatic": "Tier 2",
    "openx": "Tier 2",
    "taboola": "Tier 3",
    "outbrain": "Tier 3",
}

# ============================================================================
# FORMAT INFERENCE - Patterns and keywords
# ============================================================================

FORMAT_PRIORITY_COLS = ["Creative Size", "Creative", "Creative Type", "Format"]
AD_SIZE_PATTERN = re.compile(r"(\d{2,4})x(\d{2,4})")

STRONG_KEYWORDS = {
    "masthead": "Masthead",
    "instream": "Instream Video",
    "in-stream": "Instream Video",
    "outstream": "Outstream Video",
    "bumper": "Bumper Video",
    "trueview": "TrueView Video",
    "rewarded": "Rewarded Video",
}

GENERIC_KEYWORDS = {
    "video": "Video",
    "display": "Display",
    "banner": "Display",
    "native": "Native",
    "audio": "Audio",
    "podcast": "Audio",
    "dooh": "DOOH",
    "ooh": "DOOH",
}

# ============================================================================
# DOOH FACTORS (Screen types - gCO2)
# ============================================================================

DOOH_FACTORS = {
    "Spectacular": 0.0082,
    "Billboard": 0.0045,
    "Street Furniture": 0.0020,
    "Indoor": 0.0012,
    "Default": 0.0030,
}

# ============================================================================
# MFA DOMAINS (Made-for-Advertising blocklist)
# ============================================================================

MFA_DOMAINS_LIST = [
    "mfa.site",
    "autoblog.site",
    "clickbait.site",
    "traffic.farm",
    "ad-farm.net",
    "impression-farm.com",
]

# ============================================================================
# TRANSPORT EQUIVALENTS (Pour contexte utilisateur)
# ============================================================================

TRANSPORT_EQUIVALENTS = {
    "car_km": 0.12,      # kg CO2 per km by car
    "flight_km": 0.255,  # kg CO2 per km by plane
}

# ============================================================================
# REGIONS MAPPING
# ============================================================================

REGIONS = {
    "Europe": ["FR", "DE", "UK", "IT", "ES", "NL", "BE", "AT", "SE", "NO", "CH", "PT", "DK", "PL"],
    "North America": ["US", "CA", "MX"],
    "APAC": ["JP", "AU", "SG", "KR", "IN", "CN", "NZ"],
    "LATAM": ["BR", "AR", "CL", "CO", "PE"],
    "MENA": ["SA", "AE", "IL", "EG", "TR"],
    "Africa": ["ZA", "NG", "KE", "MA"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_float(val):
    """Safely convert any value to float"""
    if pd.isna(val) or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).replace(",", ".").replace(" ", "").strip())
    except:
        return 0.0

def safe_get_tier(exchange):
    """Get exchange tier from EXCHANGETIERMAPPING"""
    if pd.isna(exchange):
        return "Tier 3"
    norm = str(exchange).lower().strip().replace(" ", "")
    return EXCHANGE_TIER_MAPPING.get(norm, "Tier 3")

def safe_get_grid_intensity(country, default=300.0):
    """Safely get grid carbon intensity by country"""
    if pd.isna(country):
        return default
    norm = str(country).upper().strip()
    return GRID_INTENSITY.get(norm, default)

# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == "__main__":
    print("✓ All constants loaded successfully")
    print(f"✓ US States: {len(US_STATE_GRID_INTENSITY)} states mapped")
    print(f"✓ Countries: {len(GRID_INTENSITY)} countries/regions mapped")
    print(f"✓ Creative Weights: {len(CREATIVE_WEIGHTS)} formats")
    print(f"✓ Network Factors: {len(NETWORK_FACTORS)} types")
    print(f"✓ Device Factors: {len(DEVICE_FACTORS)} devices")
    print(f"✓ AdTech Factors: {len(ADTECH_FACTORS)} exchanges")