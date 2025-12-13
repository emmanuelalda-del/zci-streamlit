"""
═══════════════════════════════════════════════════════════════════════════════
ZETA CARBON INTELLIGENCE v5.3 - CONSTANTS & FACTORS
═══════════════════════════════════════════════════════════════════════════════
All GMSF-aligned carbon factors, grid data, and conversion coefficients
"""

import pandas as pd

# ═══════════════════════════════════════════════════════════════════════════
# CREATIVE WEIGHTS (MB) - OPTIMIZED v5.3
# ═══════════════════════════════════════════════════════════════════════════

CREATIVE_WEIGHTS = {
    # Video formats
    "Instream Video HD": 4.5,
    "Instream Video SD": 1.8,
    "Outstream Video": 3.2,
    "Video": 3.5,
    "Video HD": 4.0,
    "Video SD": 1.5,
    "CTV Video": 5.5,
    
    # Display & formats
    "Display": 0.25,
    "Banner": 0.15,
    "Masthead": 0.8,
    "Skinned": 0.35,
    "Rich Media": 0.45,
    
    # Native & social
    "Native": 0.35,
    "Sponsored Content": 0.40,
    "In-Feed": 0.30,
    
    # Audio & DOOH
    "Audio": 0.08,
    "Podcast": 0.10,
    "DOOH": 2.5,
    "OOH": 2.5,
    "Digital Billboard": 3.0,
    
    # Default
    "Unknown": 0.30,
}

# ═══════════════════════════════════════════════════════════════════════════
# NETWORK CARBON INTENSITY (gCO₂ per MB)
# ═══════════════════════════════════════════════════════════════════════════

NETWORK_FACTORS = {
    "WiFi": 0.015,      # gCO₂/MB
    "Fixed": 0.012,     # Fixed broadband
    "4G": 0.035,        # Cellular
    "5G": 0.025,        # 5G (more efficient)
    "LTE": 0.035,
    "Cellular": 0.032,
    "Unknown": 0.025,
}

# ═══════════════════════════════════════════════════════════════════════════
# DEVICE POWER FACTORS (relative to 1W baseline)
# ═══════════════════════════════════════════════════════════════════════════

DEVICE_FACTORS = {
    "Desktop": 1.2,      # High power consumption
    "Laptop": 1.0,
    "Mobile": 0.15,      # Low power
    "Smartphone": 0.15,
    "iPhone": 0.12,
    "Android": 0.16,
    "Tablet": 0.25,
    "CTV": 1.5,          # Connected TV (high)
    "Set-Top Box": 1.2,
    "Wearable": 0.05,
    "SmartWatch": 0.05,
    "Unknown": 0.8,      # Default assumption
}

# ═══════════════════════════════════════════════════════════════════════════
# ADTECH PATH EFFICIENCY FACTORS
# ═══════════════════════════════════════════════════════════════════════════

ADTECH_FACTORS = {
    "Direct": 0.8,              # Tier 1 - Most efficient
    "Direct-Sold": 0.9,
    "Private Marketplace": 1.2,  # PMP
    "PMP": 1.2,
    "Preferred Deals": 1.3,
    "Programmatic": 1.5,        # Tier 2 - Standard
    "Open Auction": 1.8,        # Tier 3 - Less efficient
    "Real-Time Bidding": 1.8,
    "RTB": 1.8,
    "Guaranteed": 1.1,
    "Unknown": 1.5,
}

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL GRID CARBON INTENSITY (gCO₂ per kWh)
# Source: IVA, National Grid Operators, 2024
# ═══════════════════════════════════════════════════════════════════════════

GRID_INTENSITY = {
    # Europe - Low carbon
    "FR": 50,           # France (hydro/nuclear)
    "FRANCE": 50,
    "NO": 10,           # Norway (hydro)
    "NORWAY": 10,
    "IS": 20,           # Iceland (geothermal/hydro)
    "ICELAND": 20,
    "AT": 80,           # Austria
    "AUSTRIA": 80,
    "ES": 200,          # Spain
    "SPAIN": 200,
    "PT": 150,          # Portugal
    "PORTUGAL": 150,
    "IT": 280,          # Italy
    "ITALY": 280,
    "SE": 120,          # Sweden
    "SWEDEN": 120,
    "CH": 90,           # Switzerland
    "SWITZERLAND": 90,
    
    # Europe - Medium carbon
    "DE": 350,          # Germany (renewable transition)
    "GERMANY": 350,
    "NL": 300,          # Netherlands
    "NETHERLANDS": 300,
    "BE": 200,          # Belgium
    "BELGIUM": 200,
    "DK": 250,          # Denmark
    "DENMARK": 250,
    "UK": 250,          # United Kingdom
    "UNITED KINGDOM": 250,
    "GB": 250,
    "PL": 700,          # Poland (coal heavy)
    "POLAND": 700,
    "CZ": 450,          # Czechia
    "CZECHIA": 450,
    "HU": 400,          # Hungary
    "HUNGARY": 400,
    
    # Americas - Low-Medium
    "CA": 150,          # Canada (hydro-rich)
    "CANADA": 150,
    "US": 350,          # USA (varies by region)
    "UNITED STATES": 350,
    "BR": 100,          # Brazil (hydro)
    "BRAZIL": 100,
    "MX": 300,          # Mexico
    "MEXICO": 300,
    "AR": 250,          # Argentina
    "ARGENTINA": 250,
    
    # Asia-Pacific - Variable
    "CN": 450,          # China
    "CHINA": 450,
    "IN": 650,          # India (coal heavy)
    "INDIA": 650,
    "JP": 350,          # Japan
    "JAPAN": 350,
    "AU": 550,          # Australia (coal)
    "AUSTRALIA": 550,
    "NZ": 150,          # New Zealand (hydro)
    "NEW ZEALAND": 150,
    "SG": 350,          # Singapore
    "SINGAPORE": 350,
    "TH": 450,          # Thailand
    "THAILAND": 450,
    "ID": 600,          # Indonesia
    "INDONESIA": 600,
    "KR": 400,          # South Korea
    "SOUTH KOREA": 400,
    
    # Middle East & Africa
    "AE": 500,          # UAE
    "UNITED ARAB EMIRATES": 500,
    "SA": 550,          # Saudi Arabia
    "SAUDI ARABIA": 550,
    "EG": 600,          # Egypt
    "EGYPT": 600,
    "ZA": 850,          # South Africa (coal)
    "SOUTH AFRICA": 850,
    "NG": 700,          # Nigeria
    "NIGERIA": 700,
    
    # US States (regional variation)
    "CA-US": 250,       # California
    "NY-US": 200,       # New York
    "TX-US": 400,       # Texas
    "WA-US": 100,       # Washington
    "OR-US": 150,       # Oregon
    "CO-US": 300,       # Colorado
}

# ═══════════════════════════════════════════════════════════════════════════
# TRANSPORT EQUIVALENTS (for context display)
# ═══════════════════════════════════════════════════════════════════════════

TRANSPORT_EQUIVALENTS = {
    "car_km": 0.12,           # gCO₂ per km (avg car)
    "plane_km": 0.255,        # gCO₂ per km (long-haul flight)
    "train_km": 0.04,         # gCO₂ per km (train)
    "bus_km": 0.08,           # gCO₂ per km (bus)
    "trees_needed": 25,       # kg CO₂ per tree per year
}

# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARK BANDS (gCO₂PM)
# ═══════════════════════════════════════════════════════════════════════════

BENCHMARK_BANDS = {
    "Excellent": (0, 50),      # 🟢
    "Good": (50, 150),         # 🟡
    "High": (150, 400),        # 🟠
    "Critical": (400, 9999),   # 🔴
}

# ═══════════════════════════════════════════════════════════════════════════
# US STATE -> GRID INTENSITY MAPPING
# ═══════════════════════════════════════════════════════════════════════════

US_STATE_GRID_INTENSITY = {
    "AL": 500, "AK": 400, "AZ": 350, "AR": 600, "CA": 250, "CO": 300,
    "CT": 250, "DE": 400, "FL": 450, "GA": 450, "HI": 800, "ID": 200,
    "IL": 350, "IN": 500, "IA": 400, "KS": 450, "KY": 600, "LA": 600,
    "ME": 200, "MD": 350, "MA": 250, "MI": 400, "MN": 350, "MS": 600,
    "MO": 500, "MT": 200, "NE": 450, "NV": 350, "NH": 300, "NJ": 400,
    "NM": 400, "NY": 200, "NC": 400, "ND": 300, "OH": 500, "OK": 500,
    "OR": 150, "PA": 350, "RI": 300, "SC": 400, "SD": 350, "TN": 450,
    "TX": 400, "UT": 250, "VT": 150, "VA": 350, "WA": 100, "WV": 700,
    "WI": 350, "WY": 350,
}

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def safe_float(val, default=0.0):
    """Safely convert to float"""
    try:
        if pd.isna(val):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_get_grid_intensity(country_or_state):
    """
    Get grid intensity with fallback logic
    - Try exact country code match
    - Try country name match
    - Try US state match
    - Default to global average (350 gCO₂/kWh)
    """
    if not country_or_state or pd.isna(country_or_state):
        return 350.0
    
    lookup = str(country_or_state).upper().strip()
    
    # Direct country code lookup
    if lookup in GRID_INTENSITY:
        return GRID_INTENSITY[lookup]
    
    # US State lookup
    if lookup in US_STATE_GRID_INTENSITY:
        return US_STATE_GRID_INTENSITY[lookup]
    
    # Partial match
    for code, intensity in GRID_INTENSITY.items():
        if lookup in code or code in lookup:
            return intensity
    
    # Default to global average
    return 350.0

def get_benchmark_class(gco2pm):
    """Classify carbon intensity"""
    for band, (min_val, max_val) in BENCHMARK_BANDS.items():
        if min_val <= gco2pm < max_val:
            return band
    return "Critical"

def format_number(num, decimals=2):
    """Format number with thousand separators"""
    if pd.isna(num):
        return "N/A"
    return f"{num:,.{decimals}f}"

# ═══════════════════════════════════════════════════════════════════════════
# EXPORT CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════

EXCEL_HEADER_STYLE = {
    "fill": PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid"),
    "font": Font(bold=True, color="FFFFFF", size=11),
    "alignment": Alignment(horizontal="center", vertical="center", wrap_text=True),
}

EXCEL_ACCENT_COLOR = "2E8B8B"
EXCEL_LIGHT_BG = "F0F9FB"

# End of constants.py