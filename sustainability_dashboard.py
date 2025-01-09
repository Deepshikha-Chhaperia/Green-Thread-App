import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
import os
from queue import Queue
from contextlib import contextmanager

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Database configuration
DB_NAME = 'greenthreads.db'
connection_pool = Queue(maxsize=5)

@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    try:
        connection = connection_pool.get(block=False)
    except:
        connection = sqlite3.connect(DB_NAME)
    try:
        yield connection
    finally:
        try:
            connection_pool.put(connection)
        except:
            connection.close()

def init_db():
    """Initialize database tables"""
    with get_db_connection() as conn:
        c = conn.cursor()
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        
        # Create designs table
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
                      sustainability_score REAL)''')
        conn.commit()

def fetch_designs_from_db():
    """Fetch designs data from database"""
    try:
        with get_db_connection() as conn:
            query = """
            SELECT style, materials, clothing_type, production_method, packaging,
                   shipping_method, base_color, sustainability_score, timestamp
            FROM designs
            """
            df = pd.read_sql_query(query, conn)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['sustainability_score'] = pd.to_numeric(df['sustainability_score'], errors='coerce')
            return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()
    
def estimate_environmental_impact(df):
    # Calculate impact based on sustainability score and number of designs
    total_score = df['sustainability_score'].sum()
    num_designs = len(df)
    
    # Adjust impact calculations based on sustainability score
    water_saved = total_score * 10  # Liters
    co2_reduced = total_score * 0.5  # kg
    waste_reduction = total_score * 0.2  # kg
    energy_savings = total_score * 5  # kWh
    
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
    fig.update_traces(marker=dict(sizemin=5)) #min size of markers/data points
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
#margins around the plotting area to prevent labels or data points from overlapping with the edges.
    )
    fig.update_traces(
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="black")
    )
    return fig

def create_materials_chart(df):
    materials = df['materials'].str.split(',', expand=True).stack().value_counts()
    #stack the column into single series, creating a list of materials used in designs
    #value_count: counts the occurence of each unique material
    fig = px.pie(
        values=materials.values, #count
        names=materials.index,
        title="Sustainable Materials Usage",
        hole=0.4, #donut chart
        height=500, #height of chart in pixels
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10, textfont_color='black')
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12, color="#000000"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)', #figure bg
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50) #to prevent overlapping
    )
    fig.update_traces(
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="black")
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
    fig.update_traces(textfont_color='black')
    fig.update_traces(
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="black")
    )
    return fig

def create_sustainability_trend_chart(df):
    df_grouped = df.groupby('timestamp').agg({'sustainability_score': 'mean'}).reset_index()
    fig = go.Figure() #emply plotly figure
    fig.add_trace(go.Scatter(
        x=df_grouped['timestamp'],
        y=df_grouped['sustainability_score'],
        mode='lines+markers',
        name='Average Score',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title='Average Sustainability Score Trend',
        xaxis_title="Date",
        yaxis_title="Average Sustainability Score",
        font=dict(family="Arial, sans-serif", size=12, color="#000000"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        yaxis_range=[0, 100]
    )
    fig.update_traces(
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="black")
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
    else:  # All Time
        return df
    
    return df[df['timestamp'].dt.date >= start_date]

def create_sustainability_score_chart(df):
    """Create scatter plot of sustainability scores"""
    fig = px.scatter(
        df,
        x='timestamp',
        y='sustainability_score',
        color='clothing_type',
        size='sustainability_score',
        hover_data=['style', 'materials', 'production_method'],
        title='Sustainability Scores Over Time'
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sustainability Score",
        yaxis_range=[0, 100],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def generate_sustainability_tips():
    """Generate sustainability tips using Gemini AI"""
    try:
        prompt = """Generate 5 actionable tips for promoting sustainable fashion,
                   focusing on eco-friendly materials, ethical production,
                   reducing waste, and conscious consumer choices."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Unable to generate tips at the moment. Please try again later."

def display_sustainability_dashboard(conn):
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
    /* Ensure graph text and numbers are black */
    .stPlotlyChart text {
        fill: black !important;
    }
    h2, h3 {
        color: #000000;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stSelectbox > label {
        color: black !important;
    }
    /* Set background color to a warm, subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #FEFEFA 0%, #FFF8DC 100%); 
    }

    /* Updated main heading style with 'AI SUSTAINABLE FASHION DESIGN STUDIO' on one line */
    .stApp h1 {
        color: #8B4513; /* SaddleBrown for main text */
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
        color: #DAA520; /* GoldenRod for 'DESIGN STUDIO' */
        font-family: 'Playfair Display', serif;
    }
                    
    /* Set main content color to black for better contrast */
    body, .stApp {
        color: black;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }

    /* Modern dropdown style with dark gray background and white text */
    .stSelectbox > div > div {
        background-color: #333333;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        color: white;
    }

    .custom-header {
        color: #8B4513; /* SaddleBrown */
        font-size: 2rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #DAA520; /* GoldenRod */
        padding-bottom: 5px;
    }

    /* Make "AI Generated Sustainable Design" black */
    .main .block-container h2 {
        color: black;
    }

    .stMarkdown {
        color: black !important;
    }

    .stSelectbox > div > div > div {
        background-color: #333333;
        color: white;
    }

    /* Style for dropdown options */
    .stSelectbox [role="listbox"] {
        background-color: #333333;
        color: white;
    }

    .stSelectbox [role="option"]:hover {
        background-color: #4a4a4a;
    }

    /* Ensure text inputs and text areas have black text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        color: black !important;
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }

    /* Ensure multiselect dropdown text is white on dark gray background */
    .stMultiSelect div[role="button"] {
        color: white !important;
        background-color: #333333;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }

    /* Make labels above dropdowns black */
    .stSelectbox label, .stMultiSelect label {
        color: black !important;
    }

    /* Style for custom input fields */
    .stTextInput input, .stTextArea textarea {
        color: black !important;
        background-color: white !important;
    }

    /* Ensure visibility of all text */
    .stMarkdown, .stMarkdown p, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        opacity: 1 !important;
        color: black !important;
    }

    /* Fix for custom design text area */
    .stTextArea textarea {
        color: black !important;
        background-color: white !important;
    }

    /* Ensure all text in the main content area is black */
    .main .block-container {
        color: black;
    }

    /* Updated style for buttons, including download button */
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

    /* Hover effect for buttons */
    .stButton>button:hover, .stDownloadButton>button:hover {
        opacity: 0.8;
    }

    /* Ensure download button text is white */
    .stDownloadButton>button {
        color: white !important;
    }

    /* Add a subtle golden glow to the page */
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
    /* Make specific elements black */
    .stMarkdown, .stMarkdown p, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        color: black !important;
    }

    /* Ensure file uploader text is black */
    .stFileUploader label {
        color: black !important;
    }

    /* Make subheaders black */
    .stApp h2, .stApp h3 {
        color: black !important;
    }

    /* Ensure dropdown text is black when not focused */
    .stSelectbox > div > div {
        color: black;
    }

    /* Keep dropdown options white on dark background when expanded */
    .stSelectbox [role="listbox"] {
        background-color: #333333;
        color: white;
    }

    /* Ensure custom question input text is black */
    .stTextInput input {
        color: black !important;
    }
    </style>
                
    """, unsafe_allow_html=True)

    st.markdown('<h1>SUSTAINABILITY DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown("Empowering sustainable fashion choices for a greener future!")
    
    try:
        # Initialize database if needed
        init_db()
        
        # Fetch and process data
        df = fetch_designs_from_db()
        if df.empty:
            st.info("No designs available. Start creating sustainable designs to see the impact!")
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
            
        st.plotly_chart(create_sustainability_trend_chart(filtered_df), use_container_width=True)
        
        # Leaderboard
        st.header("Top Sustainable Designs")
        top_designs = filtered_df.nlargest(5, 'sustainability_score')
        for _, design in top_designs.iterrows():
            st.markdown(f"""
                **{design['style']} {design['clothing_type']}**
                - Score: {design['sustainability_score']:.1f}/100
                - Materials: {design['materials']}
                - Production: {design['production_method']}
            """)
            
        # Sustainability Tips
        st.header("Sustainable Fashion Tips")
        tips = generate_sustainability_tips()
        st.write(tips)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    display_sustainability_dashboard()