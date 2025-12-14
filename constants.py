"""
Constants et facteurs d'émission pour Zeta Carbon Intelligence
Version 5.0.0 - Aligné GMSF 2024
"""

# ============================================
# CREATIVE WEIGHTS (MB) - Poids des créatifs
# ============================================

CREATIVE_WEIGHTS = {
    # Display Desktop/Tablet - Rectangles
    '200x200': 0.12,  # Small square
    '250x250': 0.15,  # Square
    '300x250': 0.35,  # Medium Rectangle (MPU) - très commun
    '336x280': 0.40,  # Large Rectangle
    '728x90': 0.25,   # Leaderboard
    '970x90': 0.30,   # Super Leaderboard/Pushdown
    '970x250': 0.50,  # Billboard - grand format
    '160x600': 0.28,  # Wide Skyscraper
    '120x600': 0.18,  # Skyscraper
    '300x600': 0.45,  # Half Page
    '300x1050': 0.65, # Portrait - très grand

    # Mobile
    '320x50': 0.12,   # Mobile Leaderboard
    '320x100': 0.18,  # Large Mobile Banner
    '300x50': 0.12,   # Mobile Banner
    '480x320': 0.30,  # Mobile Horizontal
    '320x480': 0.32,  # Mobile Vertical
    '640x1136': 0.60, # Mobile Phone Interstitial
    '750x1334': 0.65, # iPhone Interstitial
    '1080x1920': 0.80, # Android Interstitial

    # Feature Phones (legacy)
    '120x20': 0.03,
    '168x28': 0.04,
    '216x36': 0.05,

    # Generic Fallbacks par type
    'Video': 3.0,
    'Video HD': 4.5,
    'Video SD': 1.5,
    'Display': 0.25,
    'Banner': 0.25,
    'Native': 0.15,
    'Audio': 1.0,
    'Podcast': 1.5,
    'DOOH': 0.01,
    'Digital Out-of-Home': 0.01,
    'Masthead': 4.0,
    'Instream Video': 3.0,
    'Outstream Video': 2.5,
    'Bumper Video': 1.0,
    'TrueView Video': 2.5,
    'Rewarded Video': 3.5,
    'Unknown': 0.3
}

# ============================================
# NETWORK FACTORS (gCO2/MB) - Facteurs réseau
# ============================================

NETWORK_FACTORS = {
    'WiFi': 0.018,      # 18 gCO2/GB
    'Fiber': 0.018,
    'Fixed': 0.018,
    '4G': 0.050,        # 50 gCO2/GB
    '5G': 0.035,
    'Cellular': 0.050,
    'Mobile': 0.050,
    'Unknown': 0.025
}

# ============================================
# DEVICE FACTORS - Multiplicateurs device
# ============================================

DEVICE_FACTORS = {
    'Desktop': 1.0,
    'Laptop': 1.0,
    'Mobile': 0.6,
    'Tablet': 0.75,
    'CTV': 2.5,
    'TV': 2.5,
    'Unknown': 0.8
}

# ============================================
# GRID INTENSITY (gCO2/kWh) - Par pays
# Source: Ember Climate, IEA, NESO 2024
# ============================================

GRID_INTENSITY = {
    # Europe - Low carbon
    'NO': 12, 'NORWAY': 12,           # Hydroelectric
    'IS': 25, 'ICELAND': 25,          # Geothermal/Hydro
    'SE': 55, 'SWEDEN': 55,           # Nuclear/Hydro
    'FI': 80, 'FINLAND': 80,          # Nuclear/Hydro
    'LU': 85, 'LUXEMBOURG': 85,       # Nuclear/Hydro
    'FR': 50, 'FRANCE': 50,           # Nuclear dominant
    'AT': 120, 'AUSTRIA': 120,        # Hydro/Wind
    'CH': 35, 'SWITZERLAND': 35,      # Nuclear/Hydro
    'PT': 220, 'PORTUGAL': 220,       # Renewables
    'DK': 150, 'DENMARK': 150,        # Wind dominant
    'ES': 250, 'SPAIN': 250,          # Renewables/Gas

    # Europe - Medium carbon
    'IT': 280, 'ITALY': 280,
    'BE': 180, 'BELGIUM': 180,
    'NL': 380, 'NETHERLANDS': 380,
    'UK': 220, 'UNITED KINGDOM': 220,
    'GB': 220, 'GREAT BRITAIN': 220,
    'IE': 350, 'IRELAND': 350,
    'RO': 300, 'ROMANIA': 300,
    'SK': 180, 'SLOVAKIA': 180,
    'SI': 220, 'SLOVENIA': 220,
    'HR': 200, 'CROATIA': 200,

    # Europe - High carbon
    'DE': 450, 'GERMANY': 450,        # Coal phase-out
    'PL': 700, 'POLAND': 700,         # Coal dominant
    'CZ': 480, 'CZECH REPUBLIC': 480,
    'BG': 450, 'BULGARIA': 450,
    'EE': 680, 'ESTONIA': 680,
    'GR': 420, 'GREECE': 420,

    # Amérique du Nord
    'CA': 150, 'CANADA': 150,         # Hydro dominant
    'US': 384, 'USA': 384, 'UNITED STATES': 384,  # Mix
    'MX': 450, 'MEXICO': 450,

    # Amérique du Sud
    'BR': 120, 'BRAZIL': 120,         # Hydro
    'AR': 350, 'ARGENTINA': 350,
    'CL': 420, 'CHILE': 420,
    'CO': 180, 'COLOMBIA': 180,
    'PE': 280, 'PERU': 280,

    # Asie-Pacifique - Low/Medium
    'NZ': 120, 'NEW ZEALAND': 120,    # Geothermal/Hydro
    'JP': 480, 'JAPAN': 480,          # Post-nuclear restart
    'KR': 480, 'SOUTH KOREA': 480,
    'TW': 520, 'TAIWAN': 520,
    'SG': 420, 'SINGAPORE': 420,      # Natural gas

    # Asie - High carbon
    'CN': 550, 'CHINA': 550,          # Coal dominant mais en baisse
    'IN': 650, 'INDIA': 650,          # Coal
    'ID': 680, 'INDONESIA': 680,
    'MY': 520, 'MALAYSIA': 520,
    'TH': 480, 'THAILAND': 480,
    'VN': 520, 'VIETNAM': 520,
    'PH': 580, 'PHILIPPINES': 580,

    # Moyen-Orient
    'AE': 480, 'UAE': 480,            # Gas/Solar
    'SA': 580, 'SAUDI ARABIA': 580,
    'IL': 520, 'ISRAEL': 520,
    'QA': 600, 'QATAR': 600,
    'KW': 650, 'KUWAIT': 650,

    # Afrique
    'ZA': 880, 'SOUTH AFRICA': 880,   # Coal très élevé
    'EG': 480, 'EGYPT': 480,
    'MA': 680, 'MOROCCO': 680,
    'NG': 420, 'NIGERIA': 420,        # Gas
    'KE': 320, 'KENYA': 320,          # Geothermal

    # Océanie
    'AU': 680, 'AUSTRALIA': 680,      # Coal

    # Default
    'DEFAULT': 400,  # Moyenne mondiale
}

# ============================================
# US STATE GRID INTENSITY (gCO2/kWh)
# Source: EPA eGRID 2024
# ============================================

US_STATE_GRID_INTENSITY = {
    'AL': 450, 'AK': 180, 'AZ': 420, 'AR': 520, 'CA': 220,
    'CO': 480, 'CT': 280, 'DE': 350, 'FL': 450, 'GA': 420,
    'HI': 600, 'ID': 150, 'IL': 280, 'IN': 520, 'IA': 450,
    'KS': 480, 'KY': 620, 'LA': 550, 'ME': 280, 'MD': 350,
    'MA': 300, 'MI': 420, 'MN': 380, 'MS': 520, 'MO': 520,
    'MT': 280, 'NE': 500, 'NV': 380, 'NH': 350, 'NJ': 320,
    'NM': 480, 'NY': 180, 'NC': 420, 'ND': 400, 'OH': 580,
    'OK': 450, 'OR': 200, 'PA': 380, 'RI': 300, 'SC': 420,
    'SD': 450, 'TN': 450, 'TX': 420, 'UT': 380, 'VT': 220,
    'VA': 380, 'WA': 180, 'WV': 650, 'WI': 400, 'WY': 550,
    'DC': 350,
    'DEFAULT_US': 384
}

# ============================================
# ADTECH FACTORS - Multiplicateurs par tier
# ============================================

ADTECH_FACTORS = {
    'tier1': 1.0,    # Direct, Google, Facebook
    'tier2': 1.5,    # PubMatic, Magnite, etc.
    'tier3': 2.0,    # Long-tail SSPs
    'Unknown': 1.5
}

# ============================================
# TIER MAPPING - Classification des exchanges
# ============================================

TIER_MAPPING = {
    'tier1': [
        'Google Ad Manager', 'Google AdX', 'AdX', 'DV360',
        'Facebook', 'Meta', 'Instagram',
        'Amazon', 'Amazon Publisher Services', 'APS',
        'Microsoft', 'Xandr', 'AppNexus',
        'Direct', 'PMP', 'Programmatic Guaranteed'
    ],
    'tier2': [
        'PubMatic', 'Magnite', 'Rubicon', 'Index Exchange',
        'OpenX', 'Sovrn', 'TripleLift', 'Criteo',
        'Improve Digital', 'Smart AdServer', 'Adform'
    ],
    'tier3': [
        'Other', 'Unknown', 'Long-tail', 'Unclassified'
    ]
}

# ============================================
# MFA DOMAINS - Made-for-Advertising sites
# Liste à bloquer pour réduire l'impact carbone
# ============================================

MFA_DOMAINS_LIST = [
    'content-farm', 'clickbait', 'arbitrage',
    'ad-heavy', 'mfa-site', 'low-quality',
    'spam', 'fake-news', 'redirect-farm'
]

# ============================================
# DOOH SCREEN FACTORS
# ============================================

DOOH_SCREEN_FACTORS = {
    'Spectacular': 0.0082,  # gCO2/imp
    'Billboard': 0.0045,
    'Street Furniture': 0.0020,
    'Indoor Mall': 0.0012,
    'Transit': 0.0015,
    'Unknown DOOH': 0.0030
}

# ============================================
# DAYPARTING FACTORS
# Grid intensity varies by time of day
# ============================================

DAYPARTING_FACTORS = {
    # Hours 0-23
    0: 0.85,  # Off-peak night
    1: 0.80,
    2: 0.75,
    3: 0.75,
    4: 0.80,
    5: 0.90,
    6: 1.05,  # Morning ramp
    7: 1.15,
    8: 1.20,  # Peak
    9: 1.15,
    10: 1.10,
    11: 1.10,
    12: 1.15,
    13: 1.10,
    14: 1.05,
    15: 1.05,
    16: 1.10,
    17: 1.20,  # Evening peak
    18: 1.25,  # Highest
    19: 1.20,
    20: 1.10,
    21: 1.00,
    22: 0.95,
    23: 0.90
}

# ============================================
# CARBON PRICING (EUR per kg CO2)
# Pour calcul de dette carbone
# ============================================

CARBON_PRICE_EUR = 0.10  # 100 EUR/tonne = 0.10 EUR/kg

# ============================================
# BENCHMARK THRESHOLDS
# ============================================

BENCHMARKS = {
    'excellent': {'max': 20, 'label': '🟢 Excellent', 'color': '#10B981'},
    'good': {'max': 40, 'label': '🟡 Good', 'color': '#F59E0B'},
    'average': {'max': 60, 'label': '🟠 Average', 'color': '#F97316'},
    'poor': {'max': 999, 'label': '🔴 Poor', 'color': '#EF4444'}
}

# ============================================
# TRANSPORT EQUIVALENTS
# Pour communication avec stakeholders
# ============================================

# gCO2 per km
TRANSPORT_EMISSIONS = {
    'car_petrol': 192,      # gCO2/km - voiture essence moyenne
    'car_diesel': 171,      # gCO2/km - voiture diesel
    'car_electric': 53,     # gCO2/km - voiture électrique (mix EU)
    'plane_short': 254,     # gCO2/km - vol court-courrier
    'plane_long': 195,      # gCO2/km - vol long-courrier
    'train': 14,            # gCO2/km - train électrique
    'bus': 68,              # gCO2/km - bus diesel
}

# ============================================
# VERSION INFO
# ============================================

ZCI_VERSION = "5.0.0"
ZCI_DATE = "2025-12-14"
GMSF_COMPLIANCE = "2024"
