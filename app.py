import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
from datetime import datetime
import time
from zci_calculator import ZCICalculator
from constants import *
import plotly.graph_objects as go
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Zeta Carbon Intelligence",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour charger le logo
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# CSS personnalisé avec thème light/dark
def load_custom_css(theme="light"):
    if theme == "dark":
        primary_bg = "#1A1A2E"
        secondary_bg = "#16213E"
        text_color = "#EAEAEA"
        accent_color = "#00D9FF"
        card_bg = "#0F3460"
    else:
        primary_bg = "#FFFFFF"
        secondary_bg = "#F8F9FA"
        text_color = "#1A365D"
        accent_color = "#00A8CC"
        card_bg = "#E8F4F8"

    css = f"""
    <style>
    .main {{
        background-color: {primary_bg};
        color: {text_color};
    }}
    .stApp {{
        background: linear-gradient(135deg, {primary_bg} 0%, {secondary_bg} 100%);
    }}
    .metric-card {{
        background: {card_bg};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }}
    .metric-value {{
        font-size: 2.5em;
        font-weight: 700;
        color: {accent_color};
    }}
    .metric-label {{
        font-size: 0.9em;
        color: {text_color};
        opacity: 0.8;
    }}
    h1, h2, h3 {{
        color: {text_color} !important;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #00A8CC 0%, #00D9FF 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,168,204,0.3);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Initialisation de la session
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'data_processed' not in st.session_state:
    st.session_state.data_processed = False
if 'calculator' not in st.session_state:
    st.session_state.calculator = None

# Sidebar
with st.sidebar:
    st.image("FINAL_ZCI_LOGO_SQUARE.jpg" if 'FINAL_ZCI_LOGO_SQUARE.jpg' else None, use_container_width=True)

    st.title("⚙️ Settings")

    # Toggle theme
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("☀️ Light"):
            st.session_state.theme = 'light'
            st.rerun()
    with theme_col2:
        if st.button("🌙 Dark"):
            st.session_state.theme = 'dark'
            st.rerun()

    st.divider()

    st.markdown("### 📋 Navigation")
    page = st.radio(
        "Select page",
        ["🏠 Home", "📊 Analysis", "📈 Scenarios", "📥 Export"],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### ℹ️ About ZCI")
    st.info("""
    **Zeta Carbon Intelligence** measures and optimizes the carbon footprint 
    of digital advertising campaigns using the gCO₂PM standard.

    Version: 5.0.0
    """)

# Charger le CSS
load_custom_css(st.session_state.theme)

# Header avec logo
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("🍃 Zeta Carbon Intelligence")
    st.markdown("### *Measure, Analyze, Optimize your Digital Carbon Footprint*")

st.divider()

# ==================== PAGE HOME ====================
if page == "🏠 Home":
    st.header("Welcome to Zeta Carbon Intelligence")

    # Présentation en 3 colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
        <h3>🎯 Unified Framework</h3>
        <p>Single gCO₂PM metric across all formats, devices, and supply paths</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
        <h3>🔬 Comprehensive Factors</h3>
        <p>File size, format, AdTech path, device, network, grid intensity, DOOH specs</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
        <h3>📊 Actionable Optimization</h3>
        <p>12 what-if scenarios to reduce your carbon footprint</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📤 Upload Your Campaign Data")

    uploaded_file = st.file_uploader(
        "Choose your file (CSV, TSV, Excel)",
        type=['csv', 'tsv', 'xlsx', 'xls', 'txt'],
        help="Maximum size: 10GB. Supports files with millions of rows."
    )

    if uploaded_file is not None:
        try:
            with st.spinner('🔄 Loading data... This may take a few minutes for large files.'):
                # Détecter le type de fichier
                file_extension = uploaded_file.name.split('.')[-1].lower()

                if file_extension in ['csv', 'tsv', 'txt']:
                    # Lecture par chunks pour les gros fichiers
                    chunks = []
                    chunksize = 100000

                    # Détecter le séparateur
                    sample = uploaded_file.read(10000).decode('utf-8', errors='ignore')
                    uploaded_file.seek(0)

                    if '\t' in sample or file_extension == 'tsv':
                        sep = '\t'
                    elif '|' in sample:
                        sep = '|'
                    else:
                        sep = ','

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, chunk in enumerate(pd.read_csv(uploaded_file, sep=sep, chunksize=chunksize, low_memory=False)):
                        chunks.append(chunk)
                        progress = min((i + 1) * chunksize / 1000000, 0.95)  # Limite à 95%
                        progress_bar.progress(progress)
                        status_text.text(f'Loading chunk {i+1}... ({len(chunks) * chunksize:,} rows)')

                    df = pd.concat(chunks, ignore_index=True)
                    progress_bar.progress(1.0)
                    status_text.text(f'✅ Loaded {len(df):,} rows successfully!')

                else:  # Excel
                    df = pd.read_excel(uploaded_file)

                # Initialiser le calculateur
                st.session_state.calculator = ZCICalculator(df)
                st.session_state.data_processed = True

                st.success(f"✅ File loaded: **{uploaded_file.name}** ({len(df):,} rows, {df.shape[1]} columns)")

                # Aperçu des données
                with st.expander("👁️ Preview data (first 100 rows)"):
                    st.dataframe(df.head(100), use_container_width=True)

                st.info("👉 Go to **Analysis** page to view carbon metrics!")

        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.exception(e)

# ==================== PAGE ANALYSIS ====================
elif page == "📊 Analysis":
    if not st.session_state.data_processed or st.session_state.calculator is None:
        st.warning("⚠️ Please upload a file on the Home page first!")
    else:
        calc = st.session_state.calculator

        st.header("📊 Carbon Footprint Analysis")

        # Bouton pour lancer le calcul
        if st.button("🚀 Calculate Carbon Footprint", type="primary"):
            with st.spinner('⚡ Processing carbon calculations...'):
                try:
                    calc.process_data()
                    st.success("✅ Calculation complete!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.exception(e)
                    st.stop()

        # Vérifier si les données ont été calculées
        if 'gCO2PM' not in calc.df.columns:
            st.info("👆 Click the button above to start analysis")
            st.stop()

        # Métriques principales
        st.subheader("🎯 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_imps = calc.df['ImpsClean'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Impressions</div>
                <div class="metric-value">{total_imps:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_kg = calc.df['TotalEmissions_kgCO2'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Emissions</div>
                <div class="metric-value">{total_kg:.2f} kg</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            avg_score = calc.df['gCO2PM'].mean()
            benchmark = calc.get_benchmark(avg_score)
            color = {"🟢 Excellent": "#10B981", "🟡 Good": "#F59E0B", "🟠 Average": "#F97316", "🔴 Poor": "#EF4444"}.get(benchmark, "#6B7280")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Global Score</div>
                <div class="metric-value" style="color: {color}">{avg_score:.2f}</div>
                <div class="metric-label">gCO₂PM - {benchmark}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            data_gb = calc.df['DataVolume_GB'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Data Volume</div>
                <div class="metric-value">{data_gb:.2f} GB</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Breakdown par format
        st.subheader("📱 Breakdown by Creative Format")

        format_summary = calc.df.groupby('InferredFormat').agg({
            'ImpsClean': 'sum',
            'TotalEmissions_kgCO2': 'sum',
            'gCO2PM': 'mean'
        }).reset_index()
        format_summary.columns = ['Format', 'Impressions', 'Emissions (kg)', 'gCO₂PM']
        format_summary = format_summary.sort_values('Emissions (kg)', ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Graphique
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=format_summary['Format'],
                y=format_summary['Emissions (kg)'],
                marker_color='#00A8CC',
                text=format_summary['Emissions (kg)'].round(2),
                textposition='auto',
            ))
            fig.update_layout(
                title='Emissions by Format',
                xaxis_title='Format',
                yaxis_title='Emissions (kg CO₂)',
                height=400,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(format_summary, use_container_width=True, hide_index=True)

        st.divider()

        # Top sites
        if 'Site' in calc.df.columns:
            st.subheader("🔝 Top 30 High-Carbon Sites")

            top_sites = calc.df.groupby('Site').agg({
                'ImpsClean': 'sum',
                'TotalEmissions_kgCO2': 'sum',
                'gCO2PM': 'mean'
            }).reset_index()
            top_sites.columns = ['Site', 'Impressions', 'Emissions (kg)', 'gCO₂PM']
            top_sites = top_sites.sort_values('gCO₂PM', ascending=False).head(30)

            st.dataframe(top_sites, use_container_width=True, hide_index=True)

# ==================== PAGE SCENARIOS ====================
elif page == "📈 Scenarios":
    if not st.session_state.data_processed or st.session_state.calculator is None:
        st.warning("⚠️ Please upload and process a file first!")
    else:
        calc = st.session_state.calculator

        if 'gCO2PM' not in calc.df.columns:
            st.warning("⚠️ Please calculate carbon footprint in the Analysis page first!")
        else:
            st.header("📈 What-If Optimization Scenarios")

            st.markdown("""
            Explore 12 strategies to reduce your carbon footprint. Each scenario shows 
            the potential impact on your gCO₂PM score.
            """)

            if st.button("🔮 Generate Scenarios", type="primary"):
                with st.spinner('Computing scenarios...'):
                    scenarios = calc.compute_whatif_scenarios()
                    st.session_state.scenarios = scenarios

            if 'scenarios' in st.session_state and st.session_state.scenarios:
                scenarios = st.session_state.scenarios

                # Créer un DataFrame pour affichage
                scenario_df = pd.DataFrame([
                    {
                        'Scenario': name,
                        'New gCO₂PM': f"{score:.2f}",
                        'Reduction %': f"{reduction:.1f}%",
                        'Details': details
                    }
                    for name, (score, reduction, details) in scenarios.items()
                ])
                scenario_df = scenario_df.sort_values('Reduction %', ascending=False)

                st.dataframe(scenario_df, use_container_width=True, hide_index=True)

                # Graphique des réductions
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=[name for name, _ in sorted(scenarios.items(), key=lambda x: x[1][1], reverse=True)],
                    x=[reduction for _, (_, reduction, _) in sorted(scenarios.items(), key=lambda x: x[1][1], reverse=True)],
                    orientation='h',
                    marker_color='#00D9FF',
                    text=[f"{reduction:.1f}%" for _, (_, reduction, _) in sorted(scenarios.items(), key=lambda x: x[1][1], reverse=True)],
                    textposition='auto',
                ))
                fig.update_layout(
                    title='Potential Carbon Reduction by Scenario',
                    xaxis_title='Reduction (%)',
                    yaxis_title='Scenario',
                    height=600,
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE EXPORT ====================
elif page == "📥 Export":
    if not st.session_state.data_processed or st.session_state.calculator is None:
        st.warning("⚠️ Please upload and process a file first!")
    else:
        calc = st.session_state.calculator

        if 'gCO2PM' not in calc.df.columns:
            st.warning("⚠️ Please calculate carbon footprint in the Analysis page first!")
        else:
            st.header("📥 Export Results")

            st.markdown("### Choose your export format:")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("📊 Excel Report")
                st.markdown("Complete workbook with 9 sheets")
                if st.button("📊 Generate Excel", type="primary"):
                    with st.spinner('Generating Excel file...'):
                        excel_file = calc.generate_excel_export()
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=excel_file,
                            file_name=f"ZCI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            with col2:
                st.subheader("📄 CSV Export")
                st.markdown("Full enriched dataset")
                if st.button("📄 Generate CSV", type="primary"):
                    csv = calc.df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"ZCI_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

            with col3:
                st.subheader("📑 PDF Report")
                st.markdown("Client-ready document")
                if st.button("📑 Generate PDF", type="primary"):
                    with st.spinner('Generating PDF...'):
                        pdf_file = calc.generate_pdf_export()
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_file,
                            file_name=f"ZCI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <p><strong>Zeta Carbon Intelligence v5.0.0</strong></p>
    <p>GMSF-Aligned • Production-Ready</p>
    <p style='font-size: 0.85em; opacity: 0.8;'>© 2025 Zeta Global • Powered by Carbon Intelligence Engine</p>
</div>
""", unsafe_allow_html=True)
