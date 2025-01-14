import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
import os
import threading
from functools import wraps

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Database configuration
DB_NAME = 'greenthreads.db'
thread_local = threading.local()

# Define options for dropdowns
STYLES = ["Casual", "Formal", "Sporty", "Vintage", "Bohemian", "Minimalist", 
          "Avant-garde", "Streetwear", "Romantic", "Preppy", "Other"]

MATERIALS = ["Organic Cotton", "Recycled Polyester", "Hemp", "Tencel", "Bamboo", 
            "Cork", "Recycled Nylon", "Piñatex", "Econyl", "Recycled Wool", 
            "Organic Linen", "Soy Fabric", "Qmilk", "Orange Fiber", 
            "Recycled Denim", "Other"]

CLOTHING_TYPES = ["Shirt", "Dress", "Pants", "Jacket", "Skirt", "Sweater", 
                 "Jumpsuit", "Coat", "Blouse", "Shorts", "Cardigan", "Hoodie", 
                 "T-Shirt", "Crop Top", "Other"]

PRODUCTION_METHODS = ["Cut-and-Sew", "Fully Fashioned Knitting", 
                     "Seamless Knitting", "3D Printing", 
                     "Zero Waste Pattern Cutting", "Upcycling", "Other"]

PACKAGING_OPTIONS = ["Recycled Cardboard", "Compostable Mailers", 
                    "Reusable Fabric Bags", "Minimal Packaging", 
                    "Plastic-free Packaging", "Other"]

PRODUCTION_LOCATIONS = ["Local (within 100 miles)", "Domestic", "Nearshore", 
                       "Offshore", "Other"]

SHIPPING_METHODS = ["Ground Shipping", "Air Freight", "Sea Freight", 
                   "Hybrid (Sea + Ground)", "Other"]

BASE_COLORS = ["White", "Black", "Red", "Blue", "Green", "Yellow", "Purple", 
               "Pink", "Orange", "Brown", "Gray", "Other"]

def get_db_connection():
    """Get a thread-local database connection"""
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DB_NAME, check_same_thread=False)
    return thread_local.connection

def with_db_connection(f):
    """Decorator to handle database connections"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        try:
            return f(conn, *args, **kwargs)
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            raise
    return wrapper

@with_db_connection
def init_db(conn):
    """Initialize database with thread-safe connection"""
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        
        # Create the designs table with all required columns
        c.execute('''CREATE TABLE IF NOT EXISTS designs
                     (id INTEGER PRIMARY KEY, 
                      user_id INTEGER,
                      style TEXT,
                      materials TEXT,
                      clothing_type TEXT,
                      custom_design TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      recycling_instructions TEXT,
                      production_method TEXT,
                      packaging TEXT,
                      shipping_method TEXT,
                      base_color TEXT,
                      production_location TEXT,
                      sustainability_score REAL)''')
        conn.commit()
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        raise

@with_db_connection
def fetch_designs_from_db(conn):
    """Fetch designs data from database with thread-safe connection"""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(designs)")
        available_columns = [column[1] for column in cursor.fetchall()]

        desired_columns = [
            'style', 'materials', 'clothing_type', 'custom_design',
            'timestamp', 'recycling_instructions', 'production_method',
            'packaging', 'shipping_method', 'base_color', 'production_location',
            'sustainability_score'
        ]

        valid_columns = [col for col in desired_columns if col in available_columns]
        
        query = f"SELECT {', '.join(valid_columns)} FROM designs"
        df = pd.read_sql_query(query, conn)
        
        required_columns = {
            'style': 'Unknown Style',
            'materials': 'Not Specified',
            'clothing_type': 'Not Specified',
            'production_method': 'Standard',
            'packaging': 'Standard',
            'shipping_method': 'Standard',
            'base_color': 'Not Specified',
            'production_location': 'Not Specified',
            'sustainability_score': 50.0,
            'timestamp': datetime.now()
        }
        
        for col, default_value in required_columns.items():
            if col not in df.columns:
                df[col] = default_value

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['sustainability_score'] = pd.to_numeric(df['sustainability_score'], errors='coerce').fillna(50.0)
        
        return df
            
    except Exception as e:
        st.warning("Some data columns may be missing. Displaying available data with defaults.")
        return pd.DataFrame(columns=required_columns.keys())

def estimate_environmental_impact(df):
    total_score = df['sustainability_score'].sum()
    num_designs = len(df)
    
    water_saved = total_score * 10
    co2_reduced = total_score * 0.5
    waste_reduction = total_score * 0.2
    energy_savings = total_score * 5
    
    return {
        "water_usage_reduction": water_saved,
        "co2_emissions_reduction": co2_reduced,
        "waste_reduction": waste_reduction,
        "energy_savings": energy_savings
    }

def create_sustainability_score_chart(df):
    df_clean = df.dropna(subset=['sustainability_score'])
    
    fig = px.scatter(
        df_clean,
        x='timestamp',
        y='sustainability_score',
        color='clothing_type',
        size='sustainability_score',
        hover_data=['style', 'materials', 'production_method', 'packaging'],
        title='Sustainability Scores Over Time',
        labels={'sustainability_score': 'Score', 'timestamp': 'Date'},
        height=500
    )
    fig.update_traces(marker=dict(sizemin=5))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sustainability Score",
        yaxis_range=[0, 100],
        font=dict(family="Arial, sans-serif", size=12, color="#000000"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_color="#000000",
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

def create_materials_chart(df):
    materials = df['materials'].str.split(',', expand=True).stack().value_counts()
    fig = px.pie(
        values=materials.values,
        names=materials.index,
        title="Sustainable Materials Usage",
        hole=0.4,
        height=500,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12, color="#000000"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

def create_production_method_chart(df):
    production_methods = df['production_method'].value_counts()
    fig = px.bar(
        x=production_methods.index,
        y=production_methods.values,
        title="Sustainable Production Methods",
        labels={'x': 'Method', 'y': 'Count'},
        height=500,
        color=production_methods.index,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(
        xaxis_title="Production Method",
        yaxis_title="Number of Designs",
        font=dict(family="Arial, sans-serif", size=12, color="#000000"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis_tickangle=-45
    )
    return fig

def get_available_time_ranges(df):
    current_date = datetime.now().date()
    min_date = df['timestamp'].min().date()
    date_ranges = ["All Time"]
    
    if (current_date - min_date).days >= 7:
        date_ranges.append("Last Week")
    if (current_date - min_date).days >= 30:
        date_ranges.append("Last Month")
    if (current_date - min_date).days >= 365:
        date_ranges.append("Last Year")
    
    return date_ranges

def filter_data_by_time_range(df, time_range):
    current_date = datetime.now().date()
    if time_range == "Last Week":
        start_date = current_date - timedelta(days=7)
    elif time_range == "Last Month":
        start_date = current_date - timedelta(days=30)
    elif time_range == "Last Year":
        start_date = current_date - timedelta(days=365)
    else:
        return df
    
    return df[df['timestamp'].dt.date >= start_date]

def generate_sustainability_tips():
    try:
        prompt = """Generate 5 actionable tips for promoting sustainable fashion,
                   focusing on eco-friendly materials, ethical production,
                   reducing waste, and conscious consumer choices."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Unable to generate tips at the moment. Please try again later."

def display_sustainability_dashboard():
    # Custom CSS
    st.markdown("""
    <style>
    .st-ef {
        font-family: 'Arial', sans-serif;
        color: #000000;
    }
    .metric-card {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 30px;
        font-weight: bold;
        color: #000000;
    }
    .metric-label {
        font-size: 18px;
        color: #000000;
        margin-top: 5px;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stPlotlyChart text {
        fill: black !important;
    }
    h2, h3 {
        color: #000000;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .stSelectbox > label {
        color: black !important;
    }
    .stApp {
        background: linear-gradient(135deg, #FEFEFA 0%, #FFF8DC 100%);
    }
    .stApp h1 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-align: center;
        line-height: 1.2;
        margin-bottom: 20px;
    }
    .stApp h1 span {
        color: #DAA520;
        font-family: 'Playfair Display', serif;
    }
    body, .stApp {
        color: black;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .stSelectbox > div > div {
        background-color: #333333;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        color: white;
    }
    .custom-header {
        color: #8B4513;
        font-size: 2rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #DAA520;
        padding-bottom: 5px;
    }
    .main .block-container h2 {
        color: black;
    }
    .stMarkdown {
        color: black !important;
    }
    .stSelectbox [role="listbox"] {
        background-color: #333333;
        color: white;
    }
    .stSelectbox [role="option"]:hover {
        background-color: #4a4a4a;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        color: black !important;
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
    .stMultiSelect div[role="button"] {
        color: white !important;
        background-color: #333333;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
    .stButton>button, .stDownloadButton>button {
        color: white !important;
        background-color: #333333 !important;
        border: none !important;
        padding: 10px 24px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 16px !important;
        margin: 4px 2px !important;
        cursor: pointer !important;
        border-radius: 4px !important;
        transition: opacity 0.3s !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        opacity: 0.8;
    }
    .stDownloadButton>button {
        color: white !important;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at center, rgba(218,165,32,0.1) 0%, rgba(218,165,32,0) 70%);
        pointer-events: none;
        z-index: -1;
    }
    .stMarkdown, .stMarkdown p, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        color: black !important;
    }
    .stFileUploader label {
        color: black !important;
    }
    .stApp h2, .stApp h3 {
        color: black !important;
    }
    .stSelectbox > div > div {
        color: black;
    }
    .stSelectbox [role="listbox"] {
        background-color: #333333;
        color: white;
    }
    .stTextInput input {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    try:
        # Initialize database
        init_db()
        
        # Header
        st.markdown('<h1>SUSTAINABILITY DASHBOARD</h1>', unsafe_allow_html=True)
        st.markdown("Empowering sustainable fashion choices for a greener future!")
        
        # Fetch and process data
        df = fetch_designs_from_db()
        
        if df.empty:
            st.info("No designs available yet. Start creating sustainable designs to see the impact!")
            return
            
        # Display total designs
        st.markdown(f"**Total Designs Created: {len(df)}**")
        
        # Time range selector
        time_ranges = get_available_time_ranges(df)
        time_range = st.selectbox("Select Time Range", time_ranges)
        filtered_df = filter_data_by_time_range(df, time_range)
        
        # Environmental impact metrics
        impact = estimate_environmental_impact(filtered_df)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Water Saved", f"{impact['water_usage_reduction']:,.0f} L")
        with col2:
            st.metric("CO2 Reduced", f"{impact['co2_emissions_reduction']:,.0f} kg")
        with col3:
            st.metric("Waste Reduced", f"{impact['waste_reduction']:,.0f} kg")
        with col4:
            st.metric("Energy Saved", f"{impact['energy_savings']:,.0f} kWh")
        
        # Charts
        st.plotly_chart(create_sustainability_score_chart(filtered_df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_materials_chart(filtered_df), use_container_width=True)
        with col2:
            st.plotly_chart(create_production_method_chart(filtered_df), use_container_width=True)
        
        # Leaderboard
        st.header("Top Sustainable Designs")
        top_designs = filtered_df.nlargest(5, 'sustainability_score')
        for _, design in top_designs.iterrows():
            st.markdown(f"""
                **{design['style']} {design['clothing_type']}**
                - Materials: {design['materials']}
                - Production Method: {design['production_method']}
                - Sustainability Score: {design['sustainability_score']:.1f}/100
            """)
            
        # Sustainability Tips
        st.header("Sustainable Fashion Tips")
        tips = generate_sustainability_tips()
        st.write(tips)
        
    except Exception as e:
        st.error("Unable to load dashboard. Please try again later.")
        st.error(f"Error details: {str(e)}")

if __name__ == "__main__":
    display_sustainability_dashboard()