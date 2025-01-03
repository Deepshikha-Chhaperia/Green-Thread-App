import streamlit as st
from fabric_analyzer import interactive_sustainable_fabric_advisor
from design_studio import display_design_studio, load_models
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
import cv2
import numpy as np

#st.set_page_config(page_title="Sustainability Dashboard", layout="wide")
#st.set_page_config(page_title="EcoChic - AI Sustainable Fashion", layout="wide")


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
        c.execute('''CREATE TABLE IF NOT EXISTS designs
                     (id INTEGER PRIMARY KEY, user_id INTEGER, 
                      style TEXT, materials TEXT, clothing_type TEXT, 
                      custom_design TEXT, timestamp DATETIME, recycling_instructions TEXT)''')
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
        if st.button("Sustainability Dashboard"):
            st.query_params["page"] = "sustainability_dashboard"
            st.rerun()

def display_design_studio_wrapper():
    with get_db_connection() as conn:
        display_design_studio()

def display_home():
    # Add container for better spacing in wide layout
    container = st.container()
    with container:
        st.title("EcoChic - AI Sustainable Fashion")
        st.write("Welcome to EcoChic, your one-stop destination for AI-powered sustainable fashion design!")
        
        # Create two columns for better wide layout
        col1, col2 = st.columns(2)
        with col1:
            st.write("Explore our features to create eco-friendly designs, analyze fabrics, optimize production, and even generate innovative sustainable textiles!")
        with col2:
            st.write("Experience our cutting-edge features with real-time environmental impact analysis. Access all features from the sidebar menu!")


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
    elif page == "sustainability_dashboard":
        with get_db_connection() as conn:
            display_sustainability_dashboard(conn)
    elif page == "production_optimizer":
        display_sustainable_production_optimizer()
    elif page == "textile_generator":
        sustainable_textile_generator()

def display_fabric_analysis():
    return None

if __name__ == '__main__':
    main()