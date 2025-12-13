"""
ZETA CARBON INTELLIGENCE - Streamlit Web App v5.1 ENHANCED
Production-ready carbon accounting calculator for digital advertising
Based on ZCI v4.9.9 notebook with complete calculations and visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO

# Import constants
from constants import (
    CREATIVE_WEIGHTS, NETWORK_FACTORS, DEVICE_FACTORS, ADTECH_FACTORS,
    BENCHMARK_BANDS, US_STATE_GRID_INTENSITY, GRID_INTENSITY,
    TRANSPORT_EQUIVALENTS, safe_float, safe_get_grid_intensity
)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="ZCI - Carbon Intelligence v5.1",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1A365D 0%, #2E8B8B 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value { font-size: 32px; font-weight: 700; }
    .metric-label { font-size: 14px; opacity: 0.8; }
    
    .benchmark-excellent { background-color: #E0F4F4; color: #10B981; }
    .benchmark-good { background-color: #FEF3C7; color: #F59E0B; }
    .benchmark-high { background-color: #FFE8CC; color: #FF9F43; }
    .benchmark-critical { background-color: #FEE2E2; color: #DC2626; }
    
    .insight-box {
        background: #F8FAFB;
        border-left: 4px solid #2E8B8B;
        padding: 15px;
        border-radius: 6px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS - CARBON CALCULATIONS
# ============================================================================

def get_benchmark_class(score):
    """Classify carbon score with emoji and color"""
    if score <= 50:
        return ("🟢 Excellent", "excellent", "#10B981")
    elif score <= 150:
        return ("🟡 Good", "good", "#F59E0B")
    elif score <= 400:
        return ("🟠 High", "high", "#FF9F43")
    else:
        return ("🔴 Critical", "critical", "#DC2626")

def infer_format(row, col_creative_size, col_creative_type):
    """Infer ad format from available columns"""
    texts_checked = []
    
    if col_creative_size and col_creative_size in row.index and pd.notna(row[col_creative_size]):
        val = str(row[col_creative_size]).lower().strip()
        if val:
            texts_checked.append(val)
    
    if col_creative_type and col_creative_type in row.index and pd.notna(row[col_creative_type]):
        val = str(row[col_creative_type]).lower().strip()
        if val:
            texts_checked.append(val)
    
    if not texts_checked:
        return "Display"
    
    # Size pattern check FIRST
    for txt in texts_checked:
        match = re.search(r"(\d{2,4})x(\d{2,4})", txt)
        if match:
            w, h = match.groups()
            return f"{w}x{h}"
    
    # Strong keywords check
    for txt in texts_checked:
        lower = txt.lower()
        if "instream" in lower or "in-stream" in lower:
            return "Instream Video"
        if "outstream" in lower:
            return "Outstream Video"
        if "video" in lower and "instream" not in lower and "outstream" not in lower:
            return "Video"
        if "masthead" in lower:
            return "Masthead"
    
    # Generic check
    for txt in texts_checked:
        lower = txt.lower()
        if "native" in lower:
            return "Native"
        if "audio" in lower or "podcast" in lower:
            return "Audio"
        if "dooh" in lower or "ooh" in lower:
            return "DOOH"
    
    return "Display"

def get_creative_weight(fmt):
    """Get creative weight in MB for format"""
    if fmt in CREATIVE_WEIGHTS:
        return CREATIVE_WEIGHTS[fmt]
    
    fmt_lower = fmt.lower()
    for key, val in CREATIVE_WEIGHTS.items():
        if key.lower() in fmt_lower:
            return val
    
    return CREATIVE_WEIGHTS.get("Unknown", 0.3)

def calculate_carbon(df, col_imps, col_device, col_country, col_network, col_exchange, col_dealtype, col_creative_size, col_creative_type):
    """
    Calculate carbon emissions using ZCI v4.9.9 formulas
    """
    # Clean impressions
    df["Imps_Clean"] = pd.to_numeric(df[col_imps], errors="coerce").fillna(0).astype(int)
    df = df[df["Imps_Clean"] > 0].reset_index(drop=True)
    
    # 1. Infer format
    df["Inferred_Format"] = df.apply(
        lambda row: infer_format(row, col_creative_size, col_creative_type),
        axis=1
    )
    
    # 2. Creative weight (MB)
    df["Creative_Weight_MB"] = df["Inferred_Format"].apply(get_creative_weight)
    
    # 3. Network type
    def infer_network(row):
        if col_network and col_network in row.index and pd.notna(row[col_network]):
            net = str(row[col_network]).lower()
            if any(x in net for x in ["wifi", "wi-fi", "wlan", "fiber"]):
                return "WiFi"
            if "5g" in net:
                return "5G"
            if any(x in net for x in ["4g", "lte"]):
                return "4G"
        
        if col_device and col_device in row.index and pd.notna(row[col_device]):
            device = str(row[col_device]).lower()
            if any(x in device for x in ["mobile", "phone"]):
                return "Cellular"
        
        return "WiFi"
    
    df["Network_Type"] = df.apply(infer_network, axis=1)
    
    # 4. Device factor
    def get_device_factor(device_str):
        if pd.isna(device_str):
            return DEVICE_FACTORS.get("Unknown", 0.8)
        device_lower = str(device_str).lower()
        if device_lower in [k.lower() for k in DEVICE_FACTORS.keys()]:
            for k, v in DEVICE_FACTORS.items():
                if k.lower() == device_lower:
                    return v
        for k, v in DEVICE_FACTORS.items():
            if k.lower() in device_lower:
                return v
        return DEVICE_FACTORS.get("Unknown", 0.8)
    
    df["Device_Factor"] = df[col_device].apply(get_device_factor) if col_device else 0.8
    
    # 5. Grid intensity
    df["Grid_Intensity"] = df[col_country].apply(
        lambda x: safe_get_grid_intensity(str(x).upper().strip()) if pd.notna(x) else 300.0
    ) if col_country else 300.0
    
    # 6. AdTech factor
    def get_adtech_factor(exchange_str, dealtype_str):
        if pd.notna(dealtype_str):
            deal = str(dealtype_str).lower()
            if any(x in deal for x in ["direct", "pmp", "private", "guaranteed"]):
                return ADTECH_FACTORS.get("Direct", 1.0)
        
        if pd.notna(exchange_str):
            exch = str(exchange_str).lower()
            for key in ADTECH_FACTORS.keys():
                if key.lower() in exch:
                    return ADTECH_FACTORS[key]
        
        return ADTECH_FACTORS.get("Unknown", 1.8)
    
    df["AdTech_Factor"] = df.apply(
        lambda row: get_adtech_factor(
            row.get(col_exchange) if col_exchange else None,
            row.get(col_dealtype) if col_dealtype else None
        ),
        axis=1
    )
    
    # 7. Calculate carbon emissions (based on ZCI v4.9.9 formulas)
    # Network emissions: Imps * Creative_Weight_MB * Network_Factor
    df["Network_gCO2"] = (
        df["Imps_Clean"] * 
        df["Creative_Weight_MB"] * 
        df["Network_Type"].map(NETWORK_FACTORS).fillna(0.025)
    )
    
    # Grid emissions: Imps * Grid_Intensity * device_factor * 0.0001
    df["Grid_gCO2"] = (
        df["Imps_Clean"] * 
        df["Grid_Intensity"] * 
        df["Device_Factor"] * 
        0.0001
    )
    
    # AdTech overhead
    df["AdTech_gCO2"] = (
        df["Imps_Clean"] * 
        0.01 * 
        df["AdTech_Factor"]
    )
    
    # Total
    df["Total_gCO2"] = df["Network_gCO2"] + df["Grid_gCO2"] + df["AdTech_gCO2"]
    df["Total_Emissions_kgCO2"] = df["Total_gCO2"] / 1000000
    df["gCO2PM"] = (df["Total_gCO2"] / df["Imps_Clean"]) * 1000
    
    return df

def detect_columns(df):
    """Auto-detect critical columns from dataframe"""
    cols_lower = {col.lower(): col for col in df.columns}
    
    col_imps = None
    for term in ["billable impressions", "impressions", "delivered", "imps"]:
        if term in cols_lower:
            col_imps = cols_lower[term]
            break
    
    col_device = None
    for term in ["device", "device type", "device category"]:
        if term in cols_lower:
            col_device = cols_lower[term]
            break
    
    col_country = None
    for term in ["country", "countryregion", "geo", "geography"]:
        if term in cols_lower:
            col_country = cols_lower[term]
            break
    
    col_creative_size = None
    for term in ["creative size", "asset size", "file size", "weight"]:
        if term in cols_lower:
            col_creative_size = cols_lower[term]
            break
    
    col_creative_type = None
    for term in ["creative type", "format", "ad type", "media type"]:
        if term in cols_lower:
            col_creative_type = cols_lower[term]
            break
    
    col_network = None
    for term in ["network", "network type", "connection", "carrier"]:
        if term in cols_lower:
            col_network = cols_lower[term]
            break
    
    col_exchange = None
    for term in ["exchange", "inventory source", "supply source", "ssp"]:
        if term in cols_lower:
            col_exchange = cols_lower[term]
            break
    
    col_dealtype = None
    for term in ["deal type", "buy type", "source type"]:
        if term in cols_lower:
            col_dealtype = cols_lower[term]
            break
    
    return col_imps, col_device, col_country, col_creative_size, col_creative_type, col_network, col_exchange, col_dealtype

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1A365D 0%, #2E8B8B 100%); 
                border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>🌱 Zeta Carbon Intelligence</h1>
        <p style='color: #E0F4F4; margin: 5px 0; font-size: 16px;'><strong>GMSF-Aligned Carbon Footprint Calculator for Digital Advertising</strong></p>
        <p style='color: #E0F4F4; margin: 0; font-size: 14px;'>v5.1 Enhanced | Production-Ready | Powered by ZCI v4.9.9</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📤 Upload Your Campaign Data")
        uploaded_file = st.file_uploader(
            "Select CSV or Excel file",
            type=["csv", "xlsx", "xls", "tsv"],
            help="Minimum: Impressions + Device + Country columns"
        )
        
        st.markdown("---")
        st.markdown("""
        ### ✅ Required Columns
        - **Impressions** (Billable, Delivered, Imps)
        - **Device** (Device Type, Device Category)
        - **Country** (Geography, Geo)
        
        ### ⭐ Optional (for better accuracy)
        - Creative Size (300x250, 728x90, etc.)
        - Creative Type (Video, Display, Native)
        - Network Type (WiFi, 4G, 5G, Cellular)
        - Exchange (Google, Rubicon, PubMatic)
        - Deal Type (Direct, PMP, Open)
        """)
    
    # Main content
    if uploaded_file is None:
        # Welcome screen
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 👋 Welcome to ZCI v5.1!
            
            **Zeta Carbon Intelligence** is the world's first GMSF-aligned carbon accounting framework 
            for digital advertising campaigns. Measure, analyze, and optimize your media's carbon footprint 
            with precision.
            
            #### 🎯 What We Do
            - ✅ Calculate **gCO₂PM** (grams CO₂ per 1,000 impressions)
            - ✅ Support **all formats**: Video, Display, Native, Audio, DOOH
            - ✅ Map **130+ countries** with real grid intensity data
            - ✅ Model **optimization scenarios** for carbon reduction
            - ✅ Benchmark against industry standards
            
            #### 📊 Key Metrics
            We calculate emissions based on:
            - **Network type** (WiFi, 4G, 5G, Cellular)
            - **Device power** (Desktop, Mobile, CTV)
            - **Creative file size** (in MB)
            - **Grid intensity** (by country/region)
            - **AdTech supply path** (Tier 1, Tier 2, Tier 3)
            
            ---
            
            **👉 Start by uploading your campaign data (CSV or Excel)**
            """)
        
        with col2:
            st.markdown("### 📈 Demo Metrics")
            with st.container():
                st.markdown("""
                <div class='metric-card'>
                    <div class='metric-value'>19.8M</div>
                    <div class='metric-label'>Total Impressions</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>0.43</div>
                    <div class='metric-label'>kg CO₂ Total</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>21.6</div>
                    <div class='metric-label'>gCO₂PM (Excellent)</div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Load and process file
        try:
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
            
            # Detect columns
            col_imps, col_device, col_country, col_creative_size, col_creative_type, col_network, col_exchange, col_dealtype = detect_columns(df)
            
            # Column mapping section
            with st.expander("🔧 Column Mapping", expanded=False):
                st.write("**Auto-detected columns (adjust if needed):**")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    col_imps = st.selectbox(
                        "Impressions",
                        [None] + list(df.columns),
                        index=([None] + list(df.columns)).index(col_imps) if col_imps in df.columns else 0,
                        key="col_imps_new"
                    )
                
                with col2:
                    col_device = st.selectbox(
                        "Device",
                        [None] + list(df.columns),
                        index=([None] + list(df.columns)).index(col_device) if col_device in df.columns else 0,
                        key="col_device_new"
                    )
                
                with col3:
                    col_country = st.selectbox(
                        "Country",
                        [None] + list(df.columns),
                        index=([None] + list(df.columns)).index(col_country) if col_country in df.columns else 0,
                        key="col_country_new"
                    )
                
                with col4:
                    col_creative_type = st.selectbox(
                        "Creative Type (optional)",
                        [None] + list(df.columns),
                        index=([None] + list(df.columns)).index(col_creative_type) if col_creative_type in df.columns else 0,
                        key="col_type_new"
                    )
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    col_creative_size = st.selectbox(
                        "Creative Size (optional)",
                        [None] + list(df.columns),
                        key="col_size_new"
                    )
                
                with col2:
                    col_network = st.selectbox(
                        "Network Type (optional)",
                        [None] + list(df.columns),
                        key="col_network_new"
                    )
                
                with col3:
                    col_exchange = st.selectbox(
                        "Exchange (optional)",
                        [None] + list(df.columns),
                        key="col_exchange_new"
                    )
                
                with col4:
                    col_dealtype = st.selectbox(
                        "Deal Type (optional)",
                        [None] + list(df.columns),
                        key="col_dealtype_new"
                    )
            
            # Calculate
            if col_imps and col_imps in df.columns:
                with st.spinner("🧮 Calculating carbon emissions..."):
                    df_calc = calculate_carbon(
                        df.copy(),
                        col_imps, col_device, col_country, col_network,
                        col_exchange, col_dealtype, col_creative_size, col_creative_type
                    )
                
                st.success("✅ Calculations complete!")
                
                # KPIs
                total_imps = df_calc["Imps_Clean"].sum()
                total_emissions_kg = df_calc["Total_Emissions_kgCO2"].sum()
                global_gco2pm = (df_calc["Total_gCO2"].sum() / total_imps * 1000) if total_imps > 0 else 0
                total_data_gb = (df_calc["Creative_Weight_MB"].sum() * total_imps / 1024 / 1024 / 1024)
                
                # Display KPIs
                st.markdown("### 📊 Campaign Emissions Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Impressions", f"{total_imps:,.0f}", delta="billable")
                with col2:
                    st.metric("Total Emissions", f"{total_emissions_kg:.2f} kg", delta="CO₂e")
                with col3:
                    st.metric("Global gCO₂PM", f"{global_gco2pm:.2f}", delta="g/1k imps")
                with col4:
                    st.metric("Data Volume", f"{total_data_gb:.1f} GB", delta="transferred")
                
                # Benchmark
                bench_label, bench_class, bench_color = get_benchmark_class(global_gco2pm)
                
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: #f0f9fb; border-radius: 8px; 
                            border: 2px solid {bench_color}; margin: 20px 0;'>
                    <h3>Carbon Intensity Benchmark</h3>
                    <p style='font-size: 28px; font-weight: 700; color: {bench_color}; margin: 10px 0;'>{global_gco2pm:.2f} gCO₂PM</p>
                    <p style='font-size: 18px; font-weight: 600; color: {bench_color};'>{bench_label}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Breakdown by format
                st.markdown("### 📈 Emissions by Format")
                
                format_summary = df_calc.groupby("Inferred_Format").agg({
                    "Imps_Clean": "sum",
                    "Total_Emissions_kgCO2": "sum",
                    "Creative_Weight_MB": "mean",
                    "gCO2PM": "mean"
                }).reset_index()
                
                format_summary.columns = ["Format", "Impressions", "Emissions (kg CO₂)", "Avg File Size (MB)", "gCO2PM"]
                format_summary = format_summary.sort_values("Emissions (kg CO₂)", ascending=False)
                format_summary["Emissions (kg CO₂)"] = format_summary["Emissions (kg CO₂)"].round(4)
                format_summary["gCO2PM"] = format_summary["gCO2PM"].round(2)
                format_summary["% of Total"] = (format_summary["Emissions (kg CO₂)"] / total_emissions_kg * 100).round(1).astype(str) + "%"
                
                st.dataframe(format_summary, use_container_width=True, hide_index=True)
                
                # Breakdown by device
                if col_device:
                    st.markdown("### 📱 Emissions by Device")
                    
                    device_summary = df_calc.groupby(col_device).agg({
                        "Imps_Clean": "sum",
                        "Total_Emissions_kgCO2": "sum",
                        "gCO2PM": "mean"
                    }).reset_index()
                    
                    device_summary.columns = ["Device", "Impressions", "Emissions (kg CO₂)", "gCO2PM"]
                    device_summary = device_summary.sort_values("Emissions (kg CO₂)", ascending=False)
                    device_summary["Emissions (kg CO₂)"] = device_summary["Emissions (kg CO₂)"].round(4)
                    device_summary["gCO2PM"] = device_summary["gCO2PM"].round(2)
                    
                    st.dataframe(device_summary, use_container_width=True, hide_index=True)
                
                # Transport context
                st.markdown("### 🚗✈️ Real-world Context")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    km_car = total_emissions_kg / 0.12
                    st.info(f"**Your emissions equal {km_car:,.0f} km by car**")
                
                with col2:
                    km_plane = total_emissions_kg / 0.255
                    st.info(f"**Your emissions equal {km_plane:,.0f} km by plane**")
                
                # Export section
                st.markdown("### 💾 Export Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv = df_calc.to_csv(index=False)
                    st.download_button(
                        label="📥 Full Data (CSV)",
                        data=csv,
                        file_name=f"zci_full_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Summary
                    summary_df = pd.DataFrame({
                        "Metric": ["Total Impressions", "Total Emissions (kg CO₂)", "Global gCO₂PM", "Data Volume (GB)"],
                        "Value": [f"{total_imps:,.0f}", f"{total_emissions_kg:.2f}", f"{global_gco2pm:.2f}", f"{total_data_gb:.1f}"]
                    })
                    csv_summary = summary_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Summary (CSV)",
                        data=csv_summary,
                        file_name=f"zci_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    st.info("✅ Excel & PDF exports coming next!")
            
            else:
                st.error("❌ Please select an Impressions column in Column Mapping")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check that your file is valid CSV/Excel with proper headers")

if __name__ == "__main__":
    main()