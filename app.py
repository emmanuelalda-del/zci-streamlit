# app.py - Streamlit Application

import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from zci_calculator import ZCICalculator

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Zeta Carbon Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.5em;
        font-weight: 700;
        color: #134252;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1em;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: 700;
        color: #134252;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Status badges */
    .status-excellent { color: #10b981; }
    .status-good { color: #3b82f6; }
    .status-moderate { color: #f59e0b; }
    .status-high { color: #ef4444; }
    
    /* Table styling */
    .dataframe {
        font-size: 0.95em;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    show_debug = st.checkbox("Debug Mode", value=False)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 Help
    
    **How to use ZCI:**
    1. Upload your CSV/Excel file
    2. Map columns (auto-detection)
    3. Review results
    4. Download report
    
    **Supported formats:**
    - CSV, TSV, Excel (.xlsx)
    - Max 500MB
    
    **Required columns:**
    - Impressions count
    """)
    
    st.markdown("---")
    st.markdown("""
    **Version:** 5.0.0  
    **GMRF-Aligned**  
    *Powered by Zeta Global*
    """)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="header-title">🌍 Zeta Carbon Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">GMSF-Aligned Carbon Footprint Calculator for Digital Advertising</div>', unsafe_allow_html=True)

with col2:
    st.write("**v5.0.0**")

st.markdown("---")

# ============================================================================
# FILE UPLOAD SECTION
# ============================================================================

st.markdown("### 📤 Upload Your Campaign Data")

uploaded_file = st.file_uploader(
    "Choose a CSV, TSV, or Excel file",
    type=["csv", "tsv", "xlsx", "xls"],
    help="Your DV360, programmatic, or media platform report"
)

if uploaded_file is not None:
    
    # ========================================================================
    # LOAD DATA
    # ========================================================================
    
    try:
        # Read file
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.tsv'):
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            df = pd.read_csv(uploaded_file)
        
        if show_debug:
            st.write(f"✅ File loaded: {uploaded_file.name}")
            st.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # ====================================================================
        # COLUMN MAPPING SECTION
        # ====================================================================
        
        st.markdown("### 🔗 Column Mapping")
        st.write("Select which columns contain your data:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            col_imps = st.selectbox(
                "Impressions Column",
                [None] + list(df.columns),
                help="Number of impressions served"
            )
        
        with col2:
            col_device = st.selectbox(
                "Device Column",
                [None] + list(df.columns),
                help="Device type (Desktop, Mobile, Tablet, CTV)"
            )
        
        with col3:
            col_country = st.selectbox(
                "Country/Geography Column",
                [None] + list(df.columns),
                help="Country code (FR, US, DE, etc.)"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            col_network = st.selectbox(
                "Network Type Column",
                [None] + list(df.columns),
                help="Network (WiFi, 4G, 5G, Cellular)"
            )
        
        with col2:
            col_exchange = st.selectbox(
                "Exchange/SSP Column",
                [None] + list(df.columns),
                help="Ad exchange or DSP"
            )
        
        with col3:
            col_format = st.selectbox(
                "Creative Format Column",
                [None] + list(df.columns),
                help="Ad format (Video, Display, Native)"
            )
        
        # ====================================================================
        # VALIDATE & CALCULATE
        # ====================================================================
        
        if col_imps:
            
            st.markdown("---")
            
            # Manually set mappings in calculator
            calculator = ZCICalculator(df)
            calculator.mappings = {
                "impressions": col_imps,
                "country": col_country,
                "state": None,
                "device": col_device,
                "network": col_network,
                "exchange": col_exchange,
                "deal_type": None,
                "creative": col_format,
                "creative_size": None,
                "site": None,
            }
            
            # Run calculation with progress indicator
            with st.spinner("🔄 Calculating carbon emissions..."):
                try:
                    results = calculator.run()
                    
                    # ========================================================
                    # DISPLAY RESULTS
                    # ========================================================
                    
                    st.markdown("### 📊 Results")
                    
                    # KPI Metrics
                    summary = results["summary"]
                    
                    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                    
                    with kpi_col1:
                        st.metric(
                            "Total Impressions",
                            f"{summary['Total Impressions']:,}",
                            help="Billable impressions"
                        )
                    
                    with kpi_col2:
                        st.metric(
                            "Total Emissions",
                            f"{summary['Total Emissions kg CO2']:.2f} kg",
                            help="kg CO₂ equivalent"
                        )
                    
                    with kpi_col3:
                        score = summary['Global Intensity gCO2PM']
                        st.metric(
                            "Global Score",
                            f"{score:.2f}",
                            help="grams CO₂ per 1,000 impressions"
                        )
                    
                    with kpi_col4:
                        rating = summary['Benchmark Rating']
                        status_class = f"status-{rating.lower()}"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem;">
                            <div style="font-size: 0.9em; color: #666;">Benchmark</div>
                            <div class="{status_class}" style="font-size: 1.5em; font-weight: 700;">
                                {rating}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Format Breakdown
                    st.markdown("### 📈 Breakdown by Format")
                    format_df = results["format_breakdown"].copy()
                    format_df["Emissions kg"] = format_df["Emissions kg"].round(2)
                    format_df["gCO2PM"] = format_df["gCO2PM"].round(2)
                    st.dataframe(format_df, use_container_width=True, hide_index=True)
                    
                    # Insights
                    st.markdown("### 💡 Key Insights")
                    for insight in results["insights"]:
                        with st.container():
                            st.info(f"""
                            **{insight['Finding']}**
                            
                            {insight['Details']}
                            
                            ➜ {insight['Action']}
                            """)
                    
                    # ========================================================
                    # EXPORT SECTION
                    # ========================================================
                    
                    st.markdown("---")
                    st.markdown("### 📥 Export Results")
                    
                    # Create Excel export
                    excel_buffer = io.BytesIO()
                    
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        
                        # Sheet 1: Summary
                        summary_df = pd.DataFrame(
                            [(k, v) for k, v in summary.items()],
                            columns=['Metric', 'Value']
                        )
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Sheet 2: Format Breakdown
                        format_df.to_excel(writer, sheet_name='Format Breakdown', index=False)
                        
                        # Sheet 3: Detailed Data
                        detail_cols = ['ImpsClean', 'InferredFormat', 'NetworkType', 'GridIntensity', 'TotalEmissionskgCO2', 'gCO2PM']
                        detail_df = calculator.df[[col for col in detail_cols if col in calculator.df.columns]].copy()
                        detail_df.to_excel(writer, sheet_name='Detailed Data', index=False)
                    
                    excel_buffer.seek(0)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=excel_buffer,
                            file_name=f"ZCI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        st.info("✅ Analysis complete! Download your report above.")
                    
                    # Debug info
                    if show_debug:
                        st.markdown("---")
                        with st.expander("🔧 Debug Information"):
                            st.write("**Column Mappings:**")
                            st.json(calculator.mappings)
                            st.write("**Data Sample:**")
                            st.dataframe(calculator.df.head())
                
                except Exception as e:
                    st.error(f"❌ Calculation error: {str(e)}")
                    if show_debug:
                        st.exception(e)
        
        else:
            st.warning("⚠️ Please select the Impressions column to continue")

else:
    # No file uploaded - show welcome screen
    st.info("""
    ### 👋 Welcome to Zeta Carbon Intelligence
    
    Upload a CSV, TSV, or Excel file to get started.
    
    **What we calculate:**
    - 🌍 Network emissions by connection type
    - 🖥️ Device power consumption impact
    - ⚡ AdTech supply path efficiency
    - 🌱 Grid carbon intensity by geography
    
    **Output includes:**
    - Global gCO₂PM score
    - Format-by-format breakdown
    - Emissions by geography & device
    - Optimization recommendations
    """)
    
    # Example data structure
    with st.expander("📋 Expected Data Structure"):
        st.write("""
        Your file should have columns like:
        
        | impressions | device | country | format | network |
        |-------------|--------|---------|--------|---------|
        | 1000000 | Mobile | FR | Display | WiFi |
        | 500000 | Desktop | US | Video | Fiber |
        | 750000 | Tablet | DE | Native | 4G |
        """)