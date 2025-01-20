import streamlit as st
from fabric_analyzer import interactive_sustainable_fabric_advisor
from design_studio import display_design_studio
from sustainability_dashboard import display_sustainability_dashboard
from sustainable_production_optimizer import display_sustainable_production_optimizer
from sustainable_textile_generator import sustainable_textile_generator
from sqlite3 import OperationalError
from contextlib import contextmanager
from queue import Queue
import sqlite3
import os
from PIL import Image
from dotenv import load_dotenv
import base64
from io import BytesIO
import io
import gradio as gr
import random
import numpy as np
from dotenv import load_dotenv

#st.set_page_config(page_title="Sustainability Dashboard", layout="wide")
#st.set_page_config(page_title="EcoChic - AI Sustainable Fashion", layout="wide")

import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

# Load environment variables
load_dotenv()

# Database connection pool
DB_NAME = 'greenthreads.db'
connection_pool = Queue(maxsize=5)

@contextmanager
def get_db_connection():
    try:
        connection = connection_pool.get(block=False)
    except:
        connection = sqlite3.connect(DB_NAME)
    try:
        yield connection
    finally:
        connection_pool.put(connection)

# Initialize database
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        
        # Drop the existing designs table if it exists
        c.execute('DROP TABLE IF EXISTS designs')
        
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
                      sustainability_score REAL)''')
        conn.commit()

def sidebar_menu():
    with st.sidebar:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: black;
        }
        [data-testid="stSidebar"] > div:first-child {
            background-color: black;
            padding-top: 2rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        .sidebar .sidebar-content {
            background-color: black;
        }
        /* Ensure text color remains visible on black background */
        .sidebar-content {
            color: white !important;
        }
        /* Custom styling for the Menu heading */
        .menu-heading {
            color: white !important;
            font-size: 3.0rem;
            margin-bottom: 2rem;
            text-align: center;
            font-weight: bold;
            font-family: 'Playfair Display', serif !important;
        }
        /* Additional style to ensure text is white */
        [data-testid="stSidebar"] p {
            color: white !important;
        }
        /* Specific styling for sidebar buttons only */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
            border-radius: 4px;
            background-color: transparent;
            border: 1px solid white;
            color: white;
            transition: all 0.3s ease;
        }
        
        /* Hover effect for sidebar buttons */
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: white;
            color: black;
            border-color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="menu-heading">Menu</div>', unsafe_allow_html=True)
        
        if st.button("AI Design Studio"):
            st.query_params["page"] = "design_studio"
            st.rerun()
        if st.button("Fabric Advisor"):
            st.query_params["page"] = "fabric_analysis"
            st.rerun()
        if st.button("Sustainable Production Optimizer"):
            st.query_params["page"] = "production_optimizer"
            st.rerun()
        if st.button("Sustainable Textile Generator"):
            st.query_params["page"] = "textile_generator"
            st.rerun()
        #if st.button("Sustainability Dashboard"):
         #   st.query_params["page"] = "sustainability_dashboard"
          #  st.rerun()

def display_design_studio_wrapper():
    """Wrapper for design studio to handle model loading and database connection"""
    if not st.session_state.get('models_loaded', False):
        with st.spinner("Loading AI models..."):
            try:
                # Using the existing load_models function from design_studio
                st.session_state.models_loaded = True
            except Exception as e:
                st.error(f"Error loading models: {str(e)}")
                return

    # Maintain your existing database connection
    with get_db_connection() as conn:
        display_design_studio()

def display_home():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FEFEFA 0%, #FFF8DC 100%);
    }
    
    .main-title {
        color: #8B4513 !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 5rem !important;
        font-weight: bold;
        text-align: center;
        margin-top: 3rem !important;
        margin-bottom: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .tagline {
        color: #DAA520 !important;
        font-size: 2rem !important;
        text-align: center;
        margin-bottom: 3rem;
        font-style: italic !important;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(218,165,32,0.2);
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        border-color: #DAA520;
    }
    
    .feature-title {
        color: #8B4513 !important;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: black;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .cta-button {
        background: linear-gradient(45deg, #333333, #4a4a4a) !important;
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        display: inline-block;
        margin-top: 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .step-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #DAA520;
        transition: all 0.3s ease;
    }
    
    .step-container:hover {
        transform: scale(1.02);
    }
    
    .step-number {
        color: #DAA520 !important;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .step-title {
        color: #8B4513 !important;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    .step-description {
        color: black !important;
        font-size: 1.1rem;
        line-height: 1.6;
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
    </style>
    """, unsafe_allow_html=True)

    # Main Title and Tagline
    st.markdown('<h1 class="main-title">GreenThread</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">World\'s First AI-Powered Sustainable Fashion Platform</p>', unsafe_allow_html=True)

    # Key Features Section
    st.markdown("<h2 style='color: #8B4513; text-align: center; margin: 3rem 0; font-size: 2.5rem;'>Our Revolutionary Features</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 class="feature-title">AI Design Studio</h3>
            <p class="feature-description">Create sustainable fashion designs instantly with our cutting-edge AI technology.</p>
            <a href="?page=design_studio" class="cta-button">Start Designing</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 class="feature-title">Fabric Advisor</h3>
            <p class="feature-description">Get AI-powered insights for optimal fabric selection and sustainability.</p>
            <a href="?page=fabric_analysis" class="cta-button">Analyze Fabrics</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 class="feature-title">Textile Generator</h3>
            <p class="feature-description">Generate eco-friendly textile patterns and designs using advanced AI technology.</p>
            <a href="?page=textile_generator" class="cta-button">Generate Patterns</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 class="feature-title">Production Optimizer</h3>
            <p class="feature-description">Optimize your production process for maximum sustainability and efficiency.</p>
            <a href="?page=production_optimizer" class="cta-button">Optimize Now</a>
        </div>
        """, unsafe_allow_html=True)


    # How It Works Section
    st.markdown("<h2 style='color: #8B4513; text-align: center; margin: 3rem 0; font-size: 2.5rem;'>How It Works</h2>", unsafe_allow_html=True)
    
    steps = [
        ("Turn Dreams into Designs", "Transform your creative vision into stunning, sustainable fashion designs using our state-of-the-art AI technology."),
        ("Instant Design Magic", "Watch your sketches evolve into professional, runway-ready designs with innovative AI-powered tools."),
        ("Smart Manufacturing", "Revolutionize your production process with our intelligent planning system, reducing costs and environmental impact."),
        ("Track Your Impact", "Monitor your sustainability journey with real-time metrics and see your positive environmental contribution grow.")
    ]
    
    for i, (title, description) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step-container">
            <div class="step-number">Step {i}</div>
            <h3 class="step-title">{title}</h3>
            <p class="step-description">{description}</p>
        </div>
        """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0; padding: 3rem;">
        <h2 style="color: #8B4513; font-size: 2.5rem; margin-bottom: 1.5rem;">Ready to Revolutionize Fashion?</h2>
        <a href="?page=design_studio" class="cta-button" style="font-size: 1.2rem; padding: 1.2rem 3rem;">Start Your Journey</a>
    </div>
    """, unsafe_allow_html=True)

def main():
    init_db()  # Initialize the database
    sidebar_menu()
    page = st.query_params.get("page", "home")
    
    if page == "home":
        display_home()
    elif page == "design_studio":
        display_design_studio_wrapper()
    elif page == "fabric_analysis":
        interactive_sustainable_fabric_advisor()
    #elif page == "sustainability_dashboard":
     #   display_sustainability_dashboard()
    elif page == "production_optimizer":
        display_sustainable_production_optimizer()
    elif page == "textile_generator":
        sustainable_textile_generator()

def display_fabric_analysis():
    return None

if __name__ == '__main__':
    main()