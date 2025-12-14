# zci_calculator.py - Logic principale extraite du notebook

import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
from constants import *

class ZCICalculator:
    """
    Zeta Carbon Intelligence Calculator
    Convertit ta logique de notebook en classe réutilisable
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.results = {}
        self.mappings = {}
        
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    @staticmethod
    def safe_float(val):
        """Convertir safely en float"""
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        try:
            return float(str(val).replace(",", ".").replace(" ", "").strip())
        except:
            return 0.0
    
    @staticmethod
    def safe_get_tier(exchange):
        """Get exchange tier"""
        if pd.isna(exchange):
            return "Tier 3"
        norm = str(exchange).lower().strip().replace(" ", "")
        return EXCHANGE_TIER_MAPPING.get(norm, "Tier 3")
    
    @staticmethod
    def safe_get_grid_intensity(country, default=300.0):
        """Get grid carbon intensity by country"""
        if pd.isna(country):
            return default
        norm = str(country).upper().strip()
        return GRID_INTENSITY.get(norm, default)
    
    @staticmethod
    def infer_format_from_row(row, format_priority_cols):
        """Infer format from row data"""
        texts_checked = []
        for col in format_priority_cols:
            if col in row.index and pd.notna(row[col]):
                val = str(row[col]).strip()
                if val:
                    texts_checked.append(val)
        
        if not texts_checked:
            return "Display"
        
        # 1. Size match 300x250, 728x90, etc.
        for txt in texts_checked:
            m = AD_SIZE_PATTERN.search(txt)
            if m:
                w, h = m.groups()
                return f"{w}x{h}"
        
        # 2. Strong keywords
        for txt in texts_checked:
            lower = txt.lower()
            for kw, label in STRONG_KEYWORDS.items():
                if kw in lower:
                    return label
        
        # 3. Generic keywords
        for txt in texts_checked:
            lower = txt.lower()
            for kw, label in GENERIC_KEYWORDS.items():
                if kw in lower:
                    return label
        
        return texts_checked[0] if texts_checked else "Display"
    
    # ========================================================================
    # STEP 1 : DETECT & MAP COLUMNS
    # ========================================================================
    
    def detect_columns(self):
        """Auto-detect important columns"""
        cols = {col.lower(): col for col in self.df.columns}
        
        self.mappings = {
            "impressions": self._find_col(["impressions", "imps", "imp", "adserving impressions"]),
            "country": self._find_col(["country", "geo", "location"]),
            "state": self._find_col(["state", "us_state"]),
            "device": self._find_col(["device", "device_type"]),
            "network": self._find_col(["network", "connection", "connection_type"]),
            "exchange": self._find_col(["exchange", "ssp", "dsp"]),
            "deal_type": self._find_col(["deal_type", "deal", "pmp", "guaranteed"]),
            "creative": self._find_col(["creative", "creative_type", "format"]),
            "creative_size": self._find_col(["creative_size", "size", "ad_size"]),
            "site": self._find_col(["site", "domain", "url"]),
        }
        return self
    
    def _find_col(self, keywords):
        """Find column by keywords"""
        cols_lower = {col.lower(): col for col in self.df.columns}
        for kw in keywords:
            if kw in cols_lower:
                return cols_lower[kw]
        return None
    
    # ========================================================================
    # STEP 2 : DATA CLEANING & PREPARATION
    # ========================================================================
    
    def prepare_data(self):
        """Clean and prepare data"""
        col_imps = self.mappings["impressions"]
        
        if not col_imps or col_imps not in self.df.columns:
            raise ValueError(f"Impressions column not found. Mapped to: {col_imps}")
        
        # Clean impressions
        self.df["ImpsClean"] = pd.to_numeric(self.df[col_imps], errors='coerce').fillna(0).astype(int)
        
        # Infer format
        col_creative = self.mappings["creative"]
        col_creative_size = self.mappings["creative_size"]
        format_cols = [c for c in [col_creative, col_creative_size] if c]
        
        if format_cols:
            self.df["InferredFormat"] = self.df.apply(
                lambda row: self.infer_format_from_row(row, format_cols),
                axis=1
            )
        else:
            self.df["InferredFormat"] = "Display"
        
        return self
    
    # ========================================================================
    # STEP 3 : CARBON CALCULATION
    # ========================================================================
    
    def calculate_carbon(self):
        """Main carbon calculation"""
        col_imps = self.mappings["impressions"]
        col_device = self.mappings["device"]
        col_network = self.mappings["network"]
        col_exchange = self.mappings["exchange"]
        col_country = self.mappings["country"]
        col_state = self.mappings["state"]
        
        # 1. Creative weight
        self.df["CreativeWeightMB"] = self.df["InferredFormat"].apply(
            lambda fmt: CREATIVE_WEIGHTS.get(fmt, CREATIVE_WEIGHTS["Unknown"])
        )
        
        # 2. Data volume
        self.df["DataPerImpMB"] = self.df["CreativeWeightMB"] / 1000.0
        
        # 3. Network type & emissions
        self.df["NetworkType"] = self.df.apply(
            lambda row: self._infer_network_type(row, col_device, col_network),
            axis=1
        )
        
        self.df["NetworkgCO2"] = self.df.apply(
            lambda row: row["ImpsClean"] * row["DataPerImpMB"] * 
                       NETWORK_FACTORS.get(row["NetworkType"], NETWORK_FACTORS["Unknown"]),
            axis=1
        )
        
        # 4. AdTech factor
        self.df["AdTechFactor"] = self.df.apply(
            lambda row: self._get_adtech_factor(row, col_exchange),
            axis=1
        )
        
        self.df["AdTechgCO2"] = self.df["ImpsClean"] * 0.01 * self.df["AdTechFactor"]
        
        # 5. Grid intensity
        self.df["GridIntensity"] = self.df.apply(
            lambda row: self._get_grid_intensity(row, col_country, col_state),
            axis=1
        )
        
        # 6. Device factor
        self.df["DeviceFactor"] = self.df.apply(
            lambda row: self._get_device_factor(row, col_device),
            axis=1
        )
        
        # 7. Total emissions
        imps_safe = self.df["ImpsClean"].replace(0, 1)
        self.df["TotalgCO2PerImp"] = (
            self.df["NetworkgCO2"] / imps_safe +
            self.df["AdTechgCO2"] / imps_safe +
            self.df["GridIntensity"] * 0.0001 * self.df["DeviceFactor"]
        )
        
        self.df["TotalEmissionskgCO2"] = self.df["TotalgCO2PerImp"] * self.df["ImpsClean"] / 1000000.0
        
        # 8. gCO2PM per format
        format_gco2pm = {}
        for fmt in self.df["InferredFormat"].unique():
            fmt_data = self.df[self.df["InferredFormat"] == fmt]
            total_emissions_g = fmt_data["TotalEmissionskgCO2"].sum() * 1000000.0
            total_imps = fmt_data["ImpsClean"].sum()
            if total_imps > 0:
                format_gco2pm[fmt] = total_emissions_g / total_imps * 1000.0
            else:
                format_gco2pm[fmt] = 0.0
        
        self.df["gCO2PM"] = self.df["InferredFormat"].map(format_gco2pm)
        
        # 9. Data volume GB
        self.df["DataVolumeGB"] = self.df["DataPerImpMB"] * self.df["ImpsClean"] / 1024.0
        
        return self
    
    def _infer_network_type(self, row, col_device, col_network):
        """Infer network type"""
        if col_network and col_network in row.index and pd.notna(row[col_network]):
            net = str(row[col_network]).lower()
            if any(x in net for x in ["wifi", "wi-fi", "wlan"]):
                return "WiFi"
            if any(x in net for x in ["fiber", "fixed", "home"]):
                return "Fiber"
            if "5g" in net:
                return "5G"
            if any(x in net for x in ["4g", "lte"]):
                return "4G"
            if any(x in net for x in ["cellular", "3g", "mobile"]):
                return "Cellular"
        
        if col_device and col_device in row.index and pd.notna(row[col_device]):
            device = str(row[col_device]).lower()
            if any(x in device for x in ["mobile", "phone", "smartphone"]):
                return "Cellular"
            if any(x in device for x in ["desktop", "laptop"]):
                return "WiFi"
        
        return "WiFi"
    
    def _get_adtech_factor(self, row, col_exchange):
        """Get AdTech supply path factor"""
        if col_exchange and col_exchange in row.index and pd.notna(row[col_exchange]):
            exch = str(row[col_exchange]).lower()
            
            for platform, factor in [("google", 1.0), ("facebook", 1.0), ("amazon", 1.0)]:
                if platform in exch:
                    return ADTECH_FACTORS.get(platform.capitalize(), 1.0)
            
            if "pubmatic" in exch:
                return ADTECH_FACTORS["PubMatic"]
            if "openx" in exch:
                return ADTECH_FACTORS["OpenX"]
            if "tier 1" in exch:
                return ADTECH_FACTORS["Tier 1"]
            if "tier 2" in exch:
                return ADTECH_FACTORS["Tier 2"]
        
        return ADTECH_FACTORS["Unknown"]
    
    def _get_grid_intensity(self, row, col_country, col_state):
        """Get grid carbon intensity"""
        if col_state and col_state in row.index and pd.notna(row[col_state]):
            state = str(row[col_state]).upper().strip()
            if state.startswith("US-"):
                state = state[3:]
            if state in US_STATE_GRID_INTENSITY:
                return US_STATE_GRID_INTENSITY[state]
        
        if col_country and col_country in row.index and pd.notna(row[col_country]):
            country = str(row[col_country]).upper().strip()
            return GRID_INTENSITY.get(country, GRID_INTENSITY["GLOBAL"])
        
        return GRID_INTENSITY["GLOBAL"]
    
    def _get_device_factor(self, row, col_device):
        """Get device power consumption factor"""
        if col_device and col_device in row.index and pd.notna(row[col_device]):
            device = str(row[col_device]).lower()
            
            if any(x in device for x in ["desktop", "laptop"]):
                return DEVICE_FACTORS["Desktop"]
            if any(x in device for x in ["mobile", "phone", "smartphone"]):
                return DEVICE_FACTORS["Mobile"]
            if any(x in device for x in ["tablet", "ipad"]):
                return DEVICE_FACTORS["Tablet"]
            if any(x in device for x in ["ctv", "connected", "smart tv"]):
                return DEVICE_FACTORS["CTV"]
        
        return DEVICE_FACTORS["Unknown"]
    
    # ========================================================================
    # STEP 4 : GENERATE SUMMARY REPORTS
    # ========================================================================
    
    def generate_summary(self):
        """Generate summary metrics"""
        total_imps = float(self.df["ImpsClean"].sum())
        total_emissions_kg = float(self.df["TotalEmissionskgCO2"].sum())
        avg_score = float(self.df["gCO2PM"].iloc[0] if len(self.df) > 0 else 0.0)
        total_data_gb = float(self.df["DataVolumeGB"].sum())
        
        # Benchmark rating
        if avg_score < 50:
            rating = "Excellent"
        elif avg_score < 100:
            rating = "Good"
        elif avg_score < 200:
            rating = "Moderate"
        elif avg_score < 400:
            rating = "High"
        else:
            rating = "Critical"
        
        summary = {
            "Total Impressions": int(total_imps),
            "Total Emissions kg CO2": round(total_emissions_kg, 2),
            "Global Intensity gCO2PM": round(avg_score, 2),
            "Data Volume GB": round(total_data_gb, 2),
            "Avg Network Factor": round(float(self.df["NetworkgCO2"].sum() / total_imps if total_imps > 0 else 0), 4),
            "Benchmark Rating": rating,
        }
        
        self.results["summary"] = summary
        return self
    
    def generate_format_breakdown(self):
        """Generate format breakdown"""
        format_summary = self.df.groupby("InferredFormat", as_index=False).agg({
            "ImpsClean": "sum",
            "TotalEmissionskgCO2": "sum",
            "gCO2PM": "first",
        })
        
        format_summary.columns = ["Format", "Impressions", "Emissions kg", "gCO2PM"]
        format_summary = format_summary[format_summary["Impressions"] > 0]
        
        self.results["format_breakdown"] = format_summary
        return self
    
    def generate_insights(self):
        """Generate AI insights"""
        insights = []
        
        # Find top emitting format
        if len(self.results["format_breakdown"]) > 0:
            top_format = self.results["format_breakdown"].loc[
                self.results["format_breakdown"]["Emissions kg"].idxmax()
            ]
            
            total_emis = self.results["format_breakdown"]["Emissions kg"].sum()
            share = (top_format["Emissions kg"] / total_emis * 100) if total_emis > 0 else 0
            
            insights.append({
                "Finding": "Highest Emission Format",
                "Details": f"{top_format['Format']} accounts for {share:.1f}% of total emissions",
                "Action": f"Reduce volume or creative weight for {top_format['Format']}"
            })
        
        self.results["insights"] = insights
        return self
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def run(self):
        """Run full pipeline"""
        self.detect_columns()
        self.prepare_data()
        self.calculate_carbon()
        self.generate_summary()
        self.generate_format_breakdown()
        self.generate_insights()
        
        return self.results