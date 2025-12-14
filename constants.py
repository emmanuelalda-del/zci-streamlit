"""
Zeta Carbon Intelligence v5.3 - CONSTANTS & FACTORS

Tous les facteurs GMSF-alignés : créas, devices, network, AdTech,
grid intensity, benchmarks + helpers numériques et Excel styles.
"""

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


# ═══════════════════════════════════════════════════════════════════════════
# CREATIVE WEIGHTS (MB) - OPTIMISÉS v5.3
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

    # Display
    "Display": 0.25,
    "Banner": 0.15,
    "Masthead": 0.80,
    "Skinned": 0.35,
    "Rich Media": 0.45,

    # Native & social
    "Native": 0.35,
    "Sponsored Content": 0.40,
    "In-Feed": 0.30,

    # Audio & DOOH
    "Audio": 0.08,
    "Podcast": 0.10,
    "DOOH": 2.50,
    "OOH": 2.50,
    "Digital Billboard": 3.0,

    # Default
    "Unknown": 0.30,
}


# ═══════════════════════════════════════════════════════════════════════════
# NETWORK CARBON INTENSITY (gCO2 / MB)
# ═══════════════════════════════════════════════════════════════════════════

NETWORK_FACTORS = {
    "WiFi": 0.015,      # gCO2/MB
    "Fixed": 0.012,     # Fibre / câble
    "4G": 0.035,
    "LTE": 0.035,
    "5G": 0.025,
    "Cellular": 0.032,
    "Unknown": 0.025,
}


# ═══════════════════════════════════════════════════════════════════════════
# DEVICE POWER FACTORS (facteur relatif)
# ═══════════════════════════════════════════════════════════════════════════

DEVICE_FACTORS = {
    "Desktop": 1.2,
    "Laptop": 1.0,
    "Mobile": 0.15,
    "Smartphone": 0.15,
    "iPhone": 0.12,
    "Android": 0.16,
    "Tablet": 0.25,
    "CTV": 1.5,
    "Set-Top Box": 1.2,
    "Wearable": 0.05,
    "SmartWatch": 0.05,
    "Unknown": 0.8,
}


# ═══════════════════════════════════════════════════════════════════════════
# ADTECH PATH EFFICIENCY FACTORS
# ═══════════════════════════════════════════════════════════════════════════

ADTECH_FACTORS = {
    "Direct": 0.8,
    "Direct-Sold": 0.9,
    "Guaranteed": 1.1,
    "Private Marketplace": 1.2,
    "PMP": 1.2,
    "Preferred Deals": 1.3,
    "Programmatic": 1.5,
    "Open Auction": 1.8,
    "Real-Time Bidding": 1.8,
    "RTB": 1.8,
    "Unknown": 1.5,
}


# ═══════════════════════════════════════════════════════════════════════════
# GRID CARBON INTENSITY (gCO2 / kWh) - Sélection principale
# ═══════════════════════════════════════════════════════════════════════════

GRID_INTENSITY = {
    # Europe low
    "FR": 50, "FRANCE": 50,
    "NO": 10, "NORWAY": 10,
    "IS": 20, "ICELAND": 20,
    "AT": 80, "AUSTRIA": 80,
    "SE": 120, "SWEDEN": 120,
    "CH": 90, "SWITZERLAND": 90,
    "PT": 150, "PORTUGAL": 150,
    "ES": 200, "SPAIN": 200,
    "BE": 200, "BELGIUM": 200,
    "DK": 250, "DENMARK": 250,
    "UK": 250, "GB": 250, "UNITED KINGDOM": 250,

    # Europe higher
    "DE": 350, "GERMANY": 350,
    "NL": 300, "NETHERLANDS": 300,
    "CZ": 450, "CZECHIA": 450,
    "HU": 400, "HUNGARY": 400,
    "PL": 700, "POLAND": 700,

    # Americas
    "CA": 150, "CANADA": 150,
    "US": 350, "UNITED STATES": 350,
    "BR": 100, "BRAZIL": 100,
    "MX": 300, "MEXICO": 300,
    "AR": 250, "ARGENTINA": 250,

    # Asia-Pacific
    "CN": 450, "CHINA": 450,
    "IN": 650, "INDIA": 650,
    "JP": 350, "JAPAN": 350,
    "AU": 550, "AUSTRALIA": 550,
    "NZ": 150, "NEW ZEALAND": 150,
    "SG": 350, "SINGAPORE": 350,
    "TH": 450, "THAILAND": 450,
    "ID": 600, "INDONESIA": 600,
    "KR": 400, "SOUTH KOREA": 400,

    # Middle East & Africa
    "AE": 500, "UNITED ARAB EMIRATES": 500,
    "SA": 550, "SAUDI ARABIA": 550,
    "EG": 600, "EGYPT": 600,
    "ZA": 850, "SOUTH AFRICA": 850,
    "NG": 700, "NIGERIA": 700,

    # US regional overrides (optionnel)
    "CA-US": 250,
    "NY-US": 200,
    "TX-US": 400,
    "WA-US": 100,
    "OR-US": 150,
    "CO-US": 300,
}


# ═══════════════════════════════════════════════════════════════════════════
# US STATE GRID INTENSITY (gCO2 / kWh)
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
# TRANSPORT EQUIVALENTS
# ═══════════════════════════════════════════════════════════════════════════

TRANSPORT_EQUIVALENTS = {
    "car_km": 0.12,      # kg CO2e / km voiture
    "plane_km": 0.255,   # kg CO2e / km avion
    "train_km": 0.04,
    "bus_km": 0.08,
    "trees_needed": 25,  # kg CO2e absorbés / arbre / an
}


# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARK BANDS (gCO2PM)
# ═══════════════════════════════════════════════════════════════════════════

BENCHMARK_BANDS = {
    "Excellent": (0, 50),
    "Good": (50, 150),
    "High": (150, 400),
    "Critical": (400, 9999),
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS NUMÉRIQUES
# ═══════════════════════════════════════════════════════════════════════════

def safe_float(val, default: float = 0.0) -> float:
    """Convertit en float de manière robuste."""
    try:
        if pd.isna(val):
            return default
        # gérer les formats type "1 234,56" ou "€1,234.56"
        s = str(val)
        # enlever symboles monétaires
        for sym in ["€", "$", "£"]:
            s = s.replace(sym, "")
        s = s.replace(" ", "").replace("\u00a0", "")
        # si virgule comme séparateur décimal
        if "," in s and s.count(",") == 1 and "." not in s:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
        return float(s)
    except Exception:
        return default


def safe_get_grid_intensity(country_or_state) -> float:
    """
    Retourne une grid intensity robuste :
    - code pays exact
    - nom de pays
    - code état US
    - fallback moyenne globale 350.
    """
    if country_or_state is None or pd.isna(country_or_state):
        return 350.0

    lookup = str(country_or_state).upper().strip()

    # État US direct
    if lookup in US_STATE_GRID_INTENSITY:
        return US_STATE_GRID_INTENSITY[lookup]

    # Pays direct
    if lookup in GRID_INTENSITY:
        return GRID_INTENSITY[lookup]

    # Recherche partielle (noms longs)
    for code, val in GRID_INTENSITY.items():
        if lookup == code or lookup in code or code in lookup:
            return val

    return 350.0


def get_benchmark_label(gco2pm: float) -> str:
    """Retourne le label de benchmark (Excellent, Good, High, Critical)."""
    for label, (min_v, max_v) in BENCHMARK_BANDS.items():
        if min_v <= gco2pm < max_v:
            return label
    return "Critical"


def format_number(num, decimals: int = 2, fallback: str = "N/A") -> str:
    """Formate un nombre avec séparateur de milliers."""
    try:
        if pd.isna(num):
            return fallback
        return f"{float(num):,.{decimals}f}"
    except Exception:
        return fallback


# ═══════════════════════════════════════════════════════════════════════════
# EXCEL EXPORT STYLES
# ═══════════════════════════════════════════════════════════════════════════

EXCEL_HEADER_STYLE = {
    "fill": PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid"),
    "font": Font(bold=True, color="FFFFFF", size=11),
    "alignment": Alignment(horizontal="center", vertical="center", wrap_text=True),
    "border": Border(
        left=Side(style="thin", color="FFFFFF"),
        right=Side(style="thin", color="FFFFFF"),
        top=Side(style="thin", color="FFFFFF"),
        bottom=Side(style="thin", color="FFFFFF"),
    ),
}

EXCEL_ACCENT_COLOR = "2E8B8B"
EXCEL_LIGHT_BG = "F0F9FB"
