import pandas as pd
import numpy as np
import re
from io import BytesIO
from datetime import datetime
from constants import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ZCICalculator:
    """Calculateur principal pour Zeta Carbon Intelligence"""

    def __init__(self, df):
        """
        Initialise le calculateur avec un DataFrame

        Args:
            df: DataFrame pandas contenant les données de campagne
        """
        self.df = df.copy()
        self.column_mapping = {}
        self.total_impressions = 0
        self.total_emissions_kg = 0
        self.avg_gco2pm = 0

    def find_column_safe(self, search_terms, available_columns):
        """
        Trouve une colonne dans le DataFrame basé sur des termes de recherche

        Args:
            search_terms: Liste de termes à rechercher
            available_columns: Colonnes disponibles dans le DataFrame

        Returns:
            Nom de la colonne trouvée ou None
        """
        available_cols_lower = {str(col).lower(): col for col in available_columns}

        for term in search_terms:
            term_lower = term.lower()
            # Correspondance exacte
            if term_lower in available_cols_lower:
                return available_cols_lower[term_lower]

        # Correspondance partielle
        for i, col in enumerate(available_columns):
            for term in search_terms:
                if term.lower() in str(col).lower():
                    return col

        return None

    def detect_columns(self):
        """Détecte automatiquement les colonnes du DataFrame"""
        cols = self.df.columns

        self.column_mapping = {
            'impressions': self.find_column_safe(
                ['Billable Impressions', 'Impressions', 'Delivered', 'Imps'], cols
            ),
            'device': self.find_column_safe(
                ['Device', 'Device Type', 'Device Category'], cols
            ),
            'country': self.find_column_safe(
                ['Country', 'Country/Region', 'Geo', 'Geography'], cols
            ),
            'state': self.find_column_safe(
                ['State', 'Region', 'Province', 'DMA', 'US State'], cols
            ),
            'site': self.find_column_safe(
                ['Site', 'App/URL', 'URL', 'Domain', 'App Name'], cols
            ),
            'exchange': self.find_column_safe(
                ['Exchange', 'Inventory Source', 'Supply Source', 'SSP'], cols
            ),
            'deal_type': self.find_column_safe(
                ['Inventory Source Type', 'Source Type', 'Deal Type', 'Buy Type'], cols
            ),
            'network': self.find_column_safe(
                ['Connection Type', 'Network Type', 'Connectivity', 'Carrier'], cols
            ),
            'creative_type': self.find_column_safe(
                ['Creative Type', 'Format', 'Ad Type', 'Media Type'], cols
            ),
            'creative_size': self.find_column_safe(
                ['Creative Size', 'Asset Size', 'File Size', 'Weight'], cols
            ),
            'hour': self.find_column_safe(
                ['Hour', 'Hour of day', 'Time of Day'], cols
            )
        }

        return self.column_mapping

    def clean_data(self):
        """Nettoie et prépare les données"""
        col_imps = self.column_mapping.get('impressions')

        if col_imps:
            # Convertir les impressions en numérique
            self.df[col_imps] = pd.to_numeric(
                self.df[col_imps].astype(str).str.replace(',', '').str.replace(' ', ''),
                errors='coerce'
            )

            # Supprimer les lignes avec impressions nulles ou invalides
            initial_rows = len(self.df)
            self.df = self.df.dropna(subset=[col_imps])
            self.df = self.df[self.df[col_imps] > 0]
            removed_rows = initial_rows - len(self.df)

            if removed_rows > 0:
                print(f"Removed {removed_rows} rows with invalid/zero impressions")

            # Supprimer les doublons
            self.df = self.df.drop_duplicates()

            # Créer colonne standardisée
            self.df['ImpsClean'] = self.df[col_imps]
        else:
            raise ValueError("❌ No Impressions column found. Please check your data.")

    def get_creative_weight(self, creative_type, creative_size=None):
        """
        Détermine le poids du créatif en MB

        Args:
            creative_type: Type de créatif
            creative_size: Taille du créatif (optionnel)

        Returns:
            Poids en MB
        """
        if pd.isna(creative_type):
            return 0.3

        creative_str = str(creative_type).lower()

        # Vérifier d'abord la taille spécifique
        if creative_size and not pd.isna(creative_size):
            size_str = str(creative_size).lower()
            for size_key, weight in CREATIVE_WEIGHTS.items():
                if str(size_key).lower() in size_str:
                    return weight

        # Vérifier le type générique
        for key, weight in CREATIVE_WEIGHTS.items():
            if str(key).lower() in creative_str:
                return weight

        return 0.3  # Default

    def get_network_factor(self, network_type):
        """Retourne le facteur réseau en gCO2/MB"""
        if pd.isna(network_type):
            return NETWORK_FACTORS.get('Unknown', 0.025)

        network_str = str(network_type).lower()

        for key, factor in NETWORK_FACTORS.items():
            if key.lower() in network_str:
                return factor

        return NETWORK_FACTORS.get('Unknown', 0.025)

    def get_device_factor(self, device_type):
        """Retourne le multiplicateur device"""
        if pd.isna(device_type):
            return DEVICE_FACTORS.get('Unknown', 0.8)

        device_str = str(device_type).lower()

        for key, factor in DEVICE_FACTORS.items():
            if key.lower() in device_str:
                return factor

        return DEVICE_FACTORS.get('Unknown', 0.8)

    def get_grid_intensity(self, country, state=None):
        """Retourne l'intensité carbone de la grille électrique"""
        if pd.notna(state) and str(country).upper() in ['US', 'USA', 'UNITED STATES']:
            state_code = str(state).upper()[:2]
            return US_STATE_GRID_INTENSITY.get(state_code, US_STATE_GRID_INTENSITY['DEFAULT_US'])

        if pd.isna(country):
            return 400  # Default global

        country_str = str(country).upper()
        return GRID_INTENSITY.get(country_str, GRID_INTENSITY.get('DEFAULT', 400))

    def get_tier(self, exchange):
        """Détermine le tier de l'exchange"""
        if pd.isna(exchange):
            return 'Unknown'

        exchange_str = str(exchange).lower()

        for tier, exchanges in TIER_MAPPING.items():
            for ex in exchanges:
                if ex.lower() in exchange_str:
                    return tier

        return 'tier3'

    def calculate_carbon(self):
        """Calcule les émissions carbone pour chaque ligne"""

        # Inférer le format
        col_creative = self.column_mapping.get('creative_type')
        col_size = self.column_mapping.get('creative_size')

        if col_creative:
            self.df['InferredFormat'] = self.df.apply(
                lambda row: self.infer_format(row.get(col_creative), row.get(col_size) if col_size else None),
                axis=1
            )
        else:
            self.df['InferredFormat'] = 'Unknown'

        # Calculer le poids créatif
        self.df['CreativeWeight_MB'] = self.df.apply(
            lambda row: self.get_creative_weight(
                row.get(col_creative) if col_creative else None,
                row.get(col_size) if col_size else None
            ),
            axis=1
        )

        # Facteur réseau
        col_network = self.column_mapping.get('network')
        if col_network:
            self.df['NetworkFactor_gCO2_MB'] = self.df[col_network].apply(self.get_network_factor)
        else:
            self.df['NetworkFactor_gCO2_MB'] = 0.025

        # Facteur device
        col_device = self.column_mapping.get('device')
        if col_device:
            self.df['DeviceFactor'] = self.df[col_device].apply(self.get_device_factor)
        else:
            self.df['DeviceFactor'] = 0.8

        # Grid intensity
        col_country = self.column_mapping.get('country')
        col_state = self.column_mapping.get('state')

        if col_country:
            self.df['GridIntensity_gCO2_kWh'] = self.df.apply(
                lambda row: self.get_grid_intensity(
                    row[col_country],
                    row.get(col_state) if col_state else None
                ),
                axis=1
            )
        else:
            self.df['GridIntensity_gCO2_kWh'] = 400

        # Tier AdTech
        col_exchange = self.column_mapping.get('exchange')
        if col_exchange:
            self.df['Tier'] = self.df[col_exchange].apply(self.get_tier)
            self.df['AdTechFactor'] = self.df['Tier'].map(ADTECH_FACTORS)
        else:
            self.df['Tier'] = 'Unknown'
            self.df['AdTechFactor'] = 1.5

        # Volume de données (MB)
        self.df['DataVolume_MB'] = self.df['ImpsClean'] * self.df['CreativeWeight_MB'] / 1000

        # Volume GB
        self.df['DataVolume_GB'] = self.df['DataVolume_MB'] / 1024

        # Emissions réseau (gCO2)
        self.df['NetworkEmissions_gCO2'] = (
            self.df['DataVolume_MB'] * 
            self.df['NetworkFactor_gCO2_MB'] * 
            self.df['DeviceFactor']
        )

        # Emissions AdTech (gCO2) - approximation
        self.df['AdTechEmissions_gCO2'] = (
            self.df['DataVolume_MB'] * 
            0.01 *  # Base AdTech emission
            self.df['AdTechFactor']
        )

        # Emissions totales (gCO2)
        self.df['TotalEmissions_gCO2'] = (
            self.df['NetworkEmissions_gCO2'] + 
            self.df['AdTechEmissions_gCO2']
        )

        # Emissions totales (kg)
        self.df['TotalEmissions_kgCO2'] = self.df['TotalEmissions_gCO2'] / 1000

        # gCO2PM score
        self.df['gCO2PM'] = (self.df['TotalEmissions_gCO2'] / self.df['ImpsClean']) * 1000

        # Remplacer les valeurs infinies/NaN
        self.df = self.df.replace([np.inf, -np.inf], np.nan)
        self.df['gCO2PM'] = self.df['gCO2PM'].fillna(0)

        # Calculer les totaux
        self.total_impressions = self.df['ImpsClean'].sum()
        self.total_emissions_kg = self.df['TotalEmissions_kgCO2'].sum()
        self.avg_gco2pm = self.df['gCO2PM'].mean()

    def infer_format(self, creative_type, creative_size):
        """Infère le format du créatif"""
        if pd.isna(creative_type) and pd.isna(creative_size):
            return 'Unknown'

        creative_str = str(creative_type).lower() if pd.notna(creative_type) else ''
        size_str = str(creative_size).lower() if pd.notna(creative_size) else ''

        if 'video' in creative_str:
            return 'Video'
        elif 'audio' in creative_str:
            return 'Audio'
        elif 'dooh' in creative_str or 'out-of-home' in creative_str:
            return 'DOOH'
        elif 'native' in creative_str:
            return 'Native'
        elif 'display' in creative_str or 'banner' in creative_str:
            return 'Display'
        elif 'x' in size_str or any(char.isdigit() for char in size_str):
            return 'Display'
        else:
            return 'Unknown'

    def get_benchmark(self, gco2pm_score):
        """Retourne le benchmark pour un score gCO2PM"""
        if gco2pm_score < 20:
            return '🟢 Excellent'
        elif gco2pm_score < 40:
            return '🟡 Good'
        elif gco2pm_score < 60:
            return '🟠 Average'
        else:
            return '🔴 Poor'

    def process_data(self):
        """Pipeline complet de traitement"""
        print("🔍 Detecting columns...")
        self.detect_columns()

        print("🧹 Cleaning data...")
        self.clean_data()

        print("⚡ Calculating carbon footprint...")
        self.calculate_carbon()

        print(f"✅ Processing complete: {len(self.df):,} rows")
        print(f"   Total Impressions: {self.total_impressions:,.0f}")
        print(f"   Total Emissions: {self.total_emissions_kg:.2f} kg CO₂")
        print(f"   Average gCO₂PM: {self.avg_gco2pm:.2f}")

    def compute_whatif_scenarios(self):
        """Calcule les 12 scénarios what-if"""
        scenarios = {}

        total_imps = self.total_impressions
        current_score = self.avg_gco2pm

        col_network = self.column_mapping.get('network')
        col_exchange = self.column_mapping.get('exchange')
        col_creative = self.column_mapping.get('creative_type')
        col_country = self.column_mapping.get('country')
        col_site = self.column_mapping.get('site')

        # Scenario 1: 100% WiFi Adoption
        if col_network and col_network in self.df.columns:
            cellular = self.df[col_network].astype(str).str.lower().str.contains('cellular|4g|5g|mobile', na=False)
            cellular_imps = self.df.loc[cellular, 'ImpsClean'].sum()
            if cellular_imps > 0:
                reduction_pct = (cellular_imps / total_imps) * 0.30
                new_score = current_score * (1 - reduction_pct)
                scenarios['100% Wi-Fi Adoption'] = (
                    new_score, 
                    reduction_pct * 100,
                    f"Shift {cellular_imps:,.0f} cellular to WiFi/fixed network"
                )

        # Scenario 2: Tier 1 Supply Path
        if col_exchange and col_exchange in self.df.columns:
            tier23 = self.df['Tier'].isin(['tier2', 'tier3'])
            tier23_imps = self.df.loc[tier23, 'ImpsClean'].sum()
            if tier23_imps > 0:
                reduction_pct = (tier23_imps / total_imps) * 0.35
                new_score = current_score * (1 - reduction_pct)
                scenarios['Tier 1 Supply Path'] = (
                    new_score,
                    reduction_pct * 100,
                    f"Consolidate {tier23_imps:,.0f} imps to Tier 1 exchanges"
                )

        # Scenario 3: Frequency Cap 3/user/day
        scenarios['Frequency Cap 3/user/day'] = (
            current_score * 0.85,
            15.0,
            "Reduce overexposure and redundant impressions"
        )

        # Scenario 4: Video Bitrate 720p
        if col_creative and col_creative in self.df.columns:
            video = self.df[col_creative].astype(str).str.lower().str.contains('video', na=False)
            video_imps = self.df.loc[video, 'ImpsClean'].sum()
            if video_imps > 0:
                reduction_pct = (video_imps / total_imps) * 0.30
                new_score = current_score * (1 - reduction_pct)
                scenarios['Video Bitrate 720p'] = (
                    new_score,
                    reduction_pct * 100,
                    f"Reduce {video_imps:,.0f} video to 720p bitrate"
                )

        # Scenario 5: Green Grid Focus
        if col_country and col_country in self.df.columns:
            high_carbon = self.df['GridIntensity_gCO2_kWh'] > 500
            high_carbon_imps = self.df.loc[high_carbon, 'ImpsClean'].sum()
            if high_carbon_imps > 0:
                reduction_pct = (high_carbon_imps / total_imps) * 0.50
                new_score = current_score * (1 - reduction_pct)
                scenarios['Green Grid Focus'] = (
                    new_score,
                    reduction_pct * 100,
                    f"Geo-target away from {high_carbon_imps:,.0f} high-carbon regions"
                )

        # Scenario 6: MFA Exclusion
        if col_site and col_site in self.df.columns:
            mfa = self.df[col_site].astype(str).apply(
                lambda x: any(mfa_domain in x.lower() for mfa_domain in MFA_DOMAINS_LIST)
            )
            mfa_imps = self.df.loc[mfa, 'ImpsClean'].sum()
            if mfa_imps > 0:
                reduction_pct = (mfa_imps / total_imps) * 0.25
                new_score = current_score * (1 - reduction_pct)
                scenarios['MFA Exclusion'] = (
                    new_score,
                    reduction_pct * 100,
                    f"Exclude {mfa_imps:,.0f} MFA inventory"
                )

        # Scenario 7: 30% DOOH Migration
        scenarios['30% DOOH Migration'] = (
            current_score * 0.75,
            25.0,
            "Migrate 30% of display to DOOH (lowest gCO₂PM)"
        )

        # Scenario 8: Native Format Priority
        scenarios['Native Format Priority'] = (
            current_score * 0.80,
            20.0,
            "Shift to lighter native formats"
        )

        # Scenario 9: Off-Peak Scheduling
        scenarios['Off-Peak Scheduling'] = (
            current_score * 0.90,
            10.0,
            "Schedule 60% of imps during off-peak grid hours"
        )

        # Scenario 10: CTV Reduction
        scenarios['CTV Reduction (-50%)'] = (
            current_score * 0.88,
            12.0,
            "CTV has 2.5x device power draw"
        )

        # Scenario 11: Contextual vs Behavioral
        scenarios['Contextual Targeting'] = (
            current_score * 0.92,
            8.0,
            "Reduce AdTech hops from behavioral data"
        )

        # Scenario 12: All Combined
        max_reduction = sum([v[1] for v in scenarios.values()]) * 0.6  # 60% of sum
        scenarios['🌟 All Combined'] = (
            current_score * (1 - max_reduction/100),
            max_reduction,
            "Implement all 11 strategies together"
        )

        return scenarios

    def generate_excel_export(self):
        """Génère un fichier Excel avec 9 onglets"""
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_data = {
                'Metric': [
                    'Total Impressions',
                    'Total Emissions (kg CO₂)',
                    'Average gCO₂PM',
                    'Total Data Volume (GB)',
                    'Benchmark Classification'
                ],
                'Value': [
                    f"{self.total_impressions:,.0f}",
                    f"{self.total_emissions_kg:.2f}",
                    f"{self.avg_gco2pm:.2f}",
                    f"{self.df['DataVolume_GB'].sum():.2f}",
                    self.get_benchmark(self.avg_gco2pm)
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Sheet 2: Full Data (limité à 1M lignes pour Excel)
            self.df.head(1048576).to_excel(writer, sheet_name='Full Data', index=False)

            # Sheet 3: Format Summary
            format_summary = self.df.groupby('InferredFormat').agg({
                'ImpsClean': 'sum',
                'TotalEmissions_kgCO2': 'sum',
                'gCO2PM': 'mean'
            }).reset_index()
            format_summary.to_excel(writer, sheet_name='Format Breakdown', index=False)

            # Sheet 4: Top Sites
            if 'Site' in self.df.columns:
                top_sites = self.df.groupby('Site').agg({
                    'ImpsClean': 'sum',
                    'TotalEmissions_kgCO2': 'sum',
                    'gCO2PM': 'mean'
                }).reset_index().sort_values('gCO2PM', ascending=False).head(100)
                top_sites.to_excel(writer, sheet_name='Top Sites', index=False)

            # Sheet 5: Country Analysis
            col_country = self.column_mapping.get('country')
            if col_country and col_country in self.df.columns:
                country_summary = self.df.groupby(col_country).agg({
                    'ImpsClean': 'sum',
                    'TotalEmissions_kgCO2': 'sum',
                    'gCO2PM': 'mean',
                    'GridIntensity_gCO2_kWh': 'first'
                }).reset_index().sort_values('TotalEmissions_kgCO2', ascending=False)
                country_summary.to_excel(writer, sheet_name='Country Analysis', index=False)

            # Sheet 6: Device Analysis
            col_device = self.column_mapping.get('device')
            if col_device and col_device in self.df.columns:
                device_summary = self.df.groupby(col_device).agg({
                    'ImpsClean': 'sum',
                    'TotalEmissions_kgCO2': 'sum',
                    'gCO2PM': 'mean'
                }).reset_index()
                device_summary.to_excel(writer, sheet_name='Device Analysis', index=False)

            # Sheet 7: Exchange/Tier Analysis
            tier_summary = self.df.groupby('Tier').agg({
                'ImpsClean': 'sum',
                'TotalEmissions_kgCO2': 'sum',
                'gCO2PM': 'mean'
            }).reset_index()
            tier_summary.to_excel(writer, sheet_name='Tier Analysis', index=False)

            # Sheet 8: What-If Scenarios
            scenarios = self.compute_whatif_scenarios()
            scenario_df = pd.DataFrame([
                {
                    'Scenario': name,
                    'New gCO₂PM': score,
                    'Reduction %': reduction,
                    'Details': details
                }
                for name, (score, reduction, details) in scenarios.items()
            ])
            scenario_df.to_excel(writer, sheet_name='What-If Scenarios', index=False)

            # Sheet 9: Data Quality Report
            qa_data = {
                'Check': [
                    'Total Records',
                    'Valid Impressions',
                    'Valid Country',
                    'Valid Device',
                    'Valid Format'
                ],
                'Result': [
                    len(self.df),
                    len(self.df[self.df['ImpsClean'] > 0]),
                    len(self.df[self.df[col_country].notna()]) if col_country else 0,
                    len(self.df[self.df[col_device].notna()]) if col_device else 0,
                    len(self.df[self.df['InferredFormat'] != 'Unknown'])
                ]
            }
            pd.DataFrame(qa_data).to_excel(writer, sheet_name='Data Quality', index=False)

        output.seek(0)
        return output.getvalue()

    def generate_pdf_export(self):
        """Génère un rapport PDF destiné aux clients"""
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=30,
            alignment=1  # Center
        )

        # Titre
        story.append(Paragraph("Zeta Carbon Intelligence Report", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Date
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Section: Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        summary_text = f"""
        This report analyzes the carbon footprint of your digital advertising campaign 
        using the gCO₂PM (grams of CO₂ per 1,000 impressions) standard.
        <br/><br/>
        <b>Total Impressions:</b> {self.total_impressions:,.0f}<br/>
        <b>Total Emissions:</b> {self.total_emissions_kg:.2f} kg CO₂<br/>
        <b>Global gCO₂PM Score:</b> {self.avg_gco2pm:.2f}<br/>
        <b>Benchmark:</b> {self.get_benchmark(self.avg_gco2pm)}
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Section: Format Breakdown
        story.append(Paragraph("Carbon Emissions by Format", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        format_summary = self.df.groupby('InferredFormat').agg({
            'ImpsClean': 'sum',
            'TotalEmissions_kgCO2': 'sum',
            'gCO2PM': 'mean'
        }).reset_index()

        # Créer un tableau
        table_data = [['Format', 'Impressions', 'Emissions (kg)', 'gCO₂PM']]
        for _, row in format_summary.iterrows():
            table_data.append([
                row['InferredFormat'],
                f"{row['ImpsClean']:,.0f}",
                f"{row['TotalEmissions_kgCO2']:.2f}",
                f"{row['gCO2PM']:.2f}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00A8CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(PageBreak())

        # Section: Recommendations
        story.append(Paragraph("Optimization Recommendations", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        scenarios = self.compute_whatif_scenarios()
        top_scenarios = sorted(scenarios.items(), key=lambda x: x[1][1], reverse=True)[:5]

        reco_text = "Based on our analysis, here are the top 5 opportunities to reduce your carbon footprint:<br/><br/>"
        for i, (name, (score, reduction, details)) in enumerate(top_scenarios, 1):
            reco_text += f"<b>{i}. {name}</b> (-{reduction:.1f}%)<br/>{details}<br/><br/>"

        story.append(Paragraph(reco_text, styles['Normal']))

        # Footer
        story.append(Spacer(1, 1*inch))
        footer_text = """
        <para align=center>
        <b>Zeta Carbon Intelligence v5.0.0</b><br/>
        © 2025 Zeta Global • Powered by Carbon Intelligence Engine
        </para>
        """
        story.append(Paragraph(footer_text, styles['Normal']))

        # Construire le PDF
        doc.build(story)
        output.seek(0)
        return output.getvalue()
