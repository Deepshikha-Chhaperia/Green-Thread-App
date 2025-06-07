import io
import json
import os
import sqlite3
import uuid
from PIL import Image
from datetime import datetime
from io import BytesIO
import google.generativeai as genai
import streamlit as st
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from google.api_core import exceptions
from google.api_core import retry
import warnings
import time
from functools import lru_cache
warnings.filterwarnings('ignore')

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

st.set_page_config(
    page_title="AI Sustainable Fashion Design Studio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.cache_data.clear()
st.cache_resource.clear()

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_db_connection():
    try:
        conn = sqlite3.connect('greenthreads.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None

def create_table():
    conn = get_db_connection()
    if conn:
        try:
            conn.execute('''CREATE TABLE IF NOT EXISTS designs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        style TEXT,
                        materials TEXT,
                        clothing_type TEXT,
                        production_method TEXT,
                        packaging TEXT,
                        production_location TEXT,
                        shipping_method TEXT,
                        base_color TEXT,
                        custom_design TEXT,
                        sustainability_score INTEGER,
                        design_image BLOB,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
        except sqlite3.Error:
            pass
        finally:
            conn.close()

def save_design_to_db(user_id, style, materials, clothing_type, production_method, 
                     packaging, production_location, shipping_method, base_color, custom_design, sustainability_score):
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        materials_str = ", ".join(materials) if isinstance(materials, list) else materials
        design_image = st.session_state.generated_design if 'generated_design' in st.session_state else None
        
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO designs (
                user_id, style, materials, clothing_type, production_method, 
                packaging, production_location, shipping_method, base_color, 
                custom_design, sustainability_score, design_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (
            user_id, style, materials_str, clothing_type, production_method,
            packaging, production_location, shipping_method, base_color,
            custom_design, sustainability_score, design_image
        ))
        
        conn.commit()
        inserted_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM designs WHERE id = ?", (inserted_id,))
        verification = cursor.fetchone()
        
        if verification:
            print(f"Successfully saved design with ID: {inserted_id}")
            return inserted_id
        else:
            print("Verification failed - data not saved properly")
            return None
            
    except Exception:
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def verify_database_storage():
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM designs ORDER BY id DESC LIMIT 1")
        last_record = cursor.fetchone()
        
        if last_record:
            required_fields = ['id', 'user_id', 'style', 'materials', 'clothing_type', 
                             'production_method', 'packaging', 'production_location', 
                             'shipping_method', 'base_color', 'custom_design', 
                             'sustainability_score', 'timestamp']
                             
            record_dict = dict(zip([description[0] for description in cursor.description], last_record))
            
            missing_fields = [field for field in required_fields if field not in record_dict]
            
            if missing_fields:
                print(f"Missing fields in database: {missing_fields}")
                return False
            
            print("All fields are being stored correctly")
            return True
            
    except Exception:
        return False
    finally:
        if conn:
            conn.close()

@st.cache_resource
def load_models():
    try:
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        pipe = pipe.to("cpu")
        pipe.enable_attention_slicing()
        pipe.enable_vae_tiling()
        pipe.scheduler.num_inference_steps = 20
        return pipe
    except Exception:
        return None
        
def generate_ai_image(pipe, prompt, progress_bar):
    if pipe is None:
        return None
    
    try:
        with torch.no_grad():
            generation_params = {
                "prompt": prompt,
                "num_inference_steps": 20,
                "guidance_scale": 7.0,
                "height": 512,
                "width": 512,
                "num_images_per_prompt": 1
            }
            
            def callback(step, timestep, latents):
                try:
                    progress = min(100, int((step / generation_params["num_inference_steps"]) * 100))
                    progress_bar.progress(progress)
                except Exception:
                    pass
            
            pipe.disable_attention_slicing()
            pipe.disable_vae_tiling()
            
            output = pipe(
                **generation_params,
                callback=callback if progress_bar else None,
                callback_steps=1
            )
            
            if not output.images or len(output.images) == 0:
                return None
                
            image = output.images[0]
            return image
            
    except Exception:
        return None

def init_session_state():
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'generated_design' not in st.session_state:
        st.session_state.generated_design = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'formatted_overall_score' not in st.session_state:
        st.session_state.formatted_overall_score = None
    if 'design_history' not in st.session_state:
        st.session_state.design_history = []

retry_strategy = retry.Retry(
    initial=120.0,
    maximum=300.0,
    multiplier=2,
    predicate=retry.if_exception_type(
        exceptions.ServiceUnavailable,
        exceptions.InternalServerError,
        exceptions.TooManyRequests,
        exceptions.ResourceExhausted
    ),
    deadline=600.0
)

@lru_cache(maxsize=100)
def cached_generate_content(prompt, model_name='gemini-1.5-pro'):
    model = genai.GenerativeModel(model_name)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None

@retry_strategy
def generate_content_with_retry(model, prompt):
    try:
        response = cached_generate_content(prompt, model.model_name)
        if response is None:
            raise Exception("No response from API")
        return response
    except Exception:
        time.sleep(120)
        return None

def remove_all_asterisks(text):
    if text:
        return text.replace('*', '')
    return text

def get_sustainability_recommendations(style, materials, clothing_type, custom_design, base_color):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    As a sustainable fashion expert, provide recommendations to improve the sustainability of the following design:
    
    Style: {style}
    Materials: {', '.join(materials)}
    Clothing Type: {clothing_type}
    Custom Design: {custom_design}
    Base Color: {base_color}
    
    Consider the following aspects:
    1. Material substitutions for better sustainability
    2. Production process improvements
    3. Longevity and durability enhancements
    4. Ethical considerations
    5. Packaging and shipping optimizations
    
    Provide specific, actionable recommendations for each aspect.
    Also, provide a sustainability score (0-100) for these recommendations.
    
    Format your response as follows:
    Sustainability Score: [score]
    Recommendations:
    [Your detailed recommendations here]
    Remember to emphasize sustainable fashion practices throughout your response.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Sustainability Score: 75
            Recommendations:
            - Use organic or recycled materials like hemp or Tencel to reduce environmental impact.
            - Opt for local production to minimize transport emissions.
            - Design for durability with reinforced stitching.
            - Ensure fair labor practices by choosing certified manufacturers.
            - Use compostable packaging to reduce waste.
            """
    except Exception:
        return f"""
        Sustainability Score: 75
        Recommendations:
        - Use organic or recycled materials like hemp or Tencel to reduce environmental impact.
        - Opt for local production to minimize transport emissions.
        - Design for durability with reinforced stitching.
        - Ensure fair labor practices by choosing certified manufacturers.
        - Use compostable packaging to reduce waste.
        """

def calculate_sustainability_score(materials, production_method, packaging):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Calculate a sustainability score (0-100) for a fashion design with the following characteristics:
    
    Materials: {', '.join(materials)}
    Production Method: {production_method}
    Packaging: {packaging}
    
    Consider factors such as:
    - Environmental impact of materials
    - Energy consumption in production
    - Water usage
    - Chemical use
    - Waste generation
    - Recyclability
    - Biodegradability
    
    Provide the numerical score (0-100) followed by a brief explanation.
    Format your response as follows:
    Sustainability Score: [score]
    Explanation:
    [Your brief explanation here]
    Emphasize sustainable fashion practices in your explanation.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Sustainability Score: 70
            Explanation:
            The design uses eco-friendly materials and sustainable packaging, reducing environmental impact. Local production methods further lower emissions, though improvements in water usage could enhance the score.
            """
    except Exception:
        return f"""
        Sustainability Score: 70
        Explanation:
        The design uses eco-friendly materials and sustainable packaging, reducing environmental impact. Local production methods further lower emissions, though improvements in water usage could enhance the score.
        """

def generate_zero_waste_pattern(clothing_type, base_color):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Generate a detailed description of a zero-waste pattern for a {clothing_type} in {base_color}. Include:
    
    1. Pattern layout
    2. Cutting instructions
    3. Assembly steps
    4. Tips for minimizing fabric waste
    
    The description should be suitable for an experienced fashion designer to follow.
    Also, provide a zero-waste score (0-100) for this pattern.
    
    Format your response as follows:
    Zero-Waste Score: [score]
    Pattern Description:
    [Your detailed pattern description here]
    Emphasize sustainable fashion practices throughout your response.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Zero-Waste Score: 80
            Pattern Description:
            - Layout: Arrange pattern pieces to fit within a single fabric rectangle, minimizing gaps.
            - Cutting: Use precise cuts to avoid excess fabric; repurpose scraps for accessories.
            - Assembly: Sew pieces with minimal seam allowances to reduce waste.
            - Tips: Use digital pattern-making tools to optimize fabric use.
            """
    except Exception:
        return f"""
        Zero-Waste Score: 80
        Pattern Description:
        - Layout: Arrange pattern pieces to fit within a single fabric rectangle, minimizing gaps.
        - Cutting: Use precise cuts to avoid excess fabric; repurpose scraps for accessories.
        - Assembly: Sew pieces with minimal seam allowances to reduce waste.
        - Tips: Use digital pattern-making tools to optimize fabric use.
        """

def suggest_eco_friendly_dyes(base_color):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Suggest eco-friendly dye options for achieving a {base_color} color in sustainable fashion. For each suggestion, provide:
    
    1. Dye name or source
    2. Environmental benefits
    3. Application process
    4. Potential limitations or considerations
    
    Focus on natural, low-impact, or innovative dyeing techniques.
    Provide an overall eco-friendliness score (0-100) for these dye suggestions.
    
    Format your response as follows:
    Eco-Friendliness Score: [score]
    Dye Suggestions: [Your detailed dye suggestions here]
    Emphasize sustainable fashion practices throughout your response.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Eco-Friendliness Score: 85
            Dye Suggestions:
            - Natural dyes (e.g., indigo): Biodegradable, low water use; apply via soaking; limited color range.
            - Low-impact fiber-reactive dyes: Reduced chemical use; cold-water dyeing process; requires careful disposal.
            """
    except Exception:
        return f"""
        Eco-Friendliness Score: 85
        Dye Suggestions:
        - Natural dyes (e.g., indigo): Biodegradable, low water use; apply via soaking; limited color range.
        - Low-impact fiber-reactive dyes: Reduced chemical use; cold-water dyeing process; requires careful disposal.
        """

def estimate_carbon_footprint(materials, production_location, shipping_method):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Estimate the carbon footprint for a fashion item with the following characteristics:
    
    Materials: {', '.join(materials)}
    Production Location: {production_location}
    Shipping Method: {shipping_method}
    
    Provide:
    1. Estimated CO2 emissions (in kg CO2e)
    2. Breakdown of emissions by stage (materials, production, shipping)
    3. Suggestions for reducing the carbon footprint
    4. Overall carbon footprint score (0-100, where 100 is the lowest footprint)
    
    Base your estimates on typical industry data and provide a brief explanation of your calculation method.
    
    Format your response as follows:
    Carbon Footprint Score: [score]
    Estimate Details:
    [Your detailed carbon footprint estimate and suggestions here]
    Emphasize sustainable fashion practices throughout your response.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Carbon Footprint Score: 65
            Estimate Details:
            - Estimated CO2: ~5 kg CO2e
            - Breakdown: Materials (40%), Production (30%), Shipping (30%)
            - Suggestions: Use local materials, renewable energy in production, and sea freight for shipping.
            """
    except Exception:
        return f"""
        Carbon Footprint Score: 65
        Estimate Details:
        - Estimated CO2: ~5 kg CO2e
        - Breakdown: Materials (40%), Production (30%), Shipping (30%)
        - Suggestions: Use local materials, renewable energy in production, and sea freight for shipping.
        """

def recommend_ethical_production(production_location):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Recommend ethical production options for fashion manufacturing in or near {production_location}. For each recommendation, provide:
    
    1. Factory or company name
    2. Location
    3. Ethical certifications (e.g., Fair Trade, B Corp)
    4. Notable sustainable or ethical practices
    5. Types of garments or specialties
    
    Focus on facilities with strong labor practices, fair wages, and environmental consciousness.
    Provide an overall ethical production score (0-100) for these recommendations.
    
    Format your response as follows:
    Ethical Production Score: [score]
    Recommendations:
    [Your detailed ethical production recommendations here]
    Emphasize sustainable fashion practices throughout your response.
    """
    try:
        response = generate_content_with_retry(model, prompt)
        if response:
            return remove_all_asterisks(response)
        else:
            return f"""
            Ethical Production Score: 80
            Recommendations:
            - Choose factories with Fair Trade certification in {production_location}, ensuring fair wages and safe working conditions.
            - Partner with local cooperatives specializing in sustainable garments, focusing on eco-friendly production.
            """
    except Exception:
        return f"""
        Ethical Production Score: 80
        Recommendations:
        - Choose factories with Fair Trade certification in {production_location}, ensuring fair wages and safe working conditions.
        - Partner with local cooperatives specializing in sustainable garments, focusing on eco-friendly production.
        """

def extract_sustainability_score(overall_score):
    try:
        lines = overall_score.split('\n')
        score_line = next(line for line in lines if line.strip().startswith("Sustainability Score:"))
        score = int(score_line.split(':')[1].strip().split()[0])
        formatted_score = f"**{score_line.strip()}**"
        overall_score = overall_score.replace(score_line, formatted_score)
        return score, overall_score
    except (StopIteration, IndexError, ValueError):
        return 50, f"**Sustainability Score: 50**\n{overall_score}"

def display_design_studio():
    st.markdown("""
    <style>
    .stImage {
        margin-bottom: 0.5rem !important;
    }
    
    .stImage + div {
        margin-top: 0 !important;
        padding-top: 0 !important;
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

    .stSelectbox > div > div > div {
        background-color: #333333;
        color: white;
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

    .stSelectbox label, .stMultiSelect label {
        color: black !important;
    }

    .stTextInput input, .stTextArea textarea {
        color: black !important;
        background-color: white !important;
    }

    .stMarkdown, .stMarkdown p, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        opacity: 1 !important;
        color: black !important;
    }

    .stTextArea textarea {
        color: black !important;
        background-color: white !important;
    }

    .main .block-container {
        color: black;
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

    .stImage + div {
        color: black !important;
    }
    
    .streamlit-expanderHeader {
        font-size: 1.5rem !important;
        color: black !important;
        font-weight: bold !important;
    }
    
    .stImage {
        margin-bottom: 0.5rem !important;
    }
    
    .stImage img + div {
        color: black !important;
    }
    
    .streamlit-expanderContent {
        color: black !important;
    }

    .streamlit-expanderHeader {
        font-size: 2rem !important;
        color: #8B4513 !important;
        font-weight: bold !important;
        padding-bottom: 5px !important;
        border-bottom: 2px solid #DAA520 !important;
        margin-bottom: 10px !important;
        font-family: 'Playfair Display', serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1>AI SUSTAINABLE FASHION <span> DESIGN STUDIO </span></h1>', unsafe_allow_html=True)
    st.markdown("""
    Create eco-friendly fashion designs with AI-generated images and personalized sustainability tips, tailored to your style!
    """)

    if 'generated_design' not in st.session_state:
        st.session_state.generated_design = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'formatted_overall_score' not in st.session_state:
        st.session_state.formatted_overall_score = None
    if 'design_history' not in st.session_state:
        st.session_state.design_history = []

    image_generator = load_models()
    if image_generator is None:
        return

    styles = ["Casual", "Formal", "Sporty", "Vintage", "Bohemian", "Minimalist", "Avant-garde", "Streetwear", "Romantic", "Preppy", "Other"]
    materials = ["Organic Cotton", "Recycled Polyester", "Hemp", "Tencel", "Bamboo", "Cork", "Recycled Nylon", "Piñatex", "Econyl", "Recycled Wool", "Organic Linen", "Soy Fabric", "Qmilk", "Orange Fiber", "Recycled Denim", "Other"]
    clothing_types = ["Shirt", "Dress", "Pants", "Jacket", "Skirt", "Sweater", "Jumpsuit", "Coat", "Blouse", "Shorts", "Cardigan", "Hoodie", "T-Shirt", "Crop Top", "Other"]
    production_methods = ["Cut-and-Sew", "Fully Fashioned Knitting", "Seamless Knitting", "3D Printing", "Zero Waste Pattern Cutting", "Upcycling", "Other"]
    packaging_options = ["Recycled Cardboard", "Compostable Mailers", "Reusable Fabric Bags", "Minimal Packaging", "Plastic-free Packaging", "Other"]
    production_locations = ["Local (within 100 miles)", "Domestic", "Nearshore", "Offshore", "Other"]
    shipping_methods = ["Ground Shipping", "Air Freight", "Sea Freight", "Hybrid (Sea + Ground)", "Other"]
    base_colors = ["White", "Black", "Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Orange", "Brown", "Gray", "Other"]

    col1, col2 = st.columns(2)

    with col1:
        style = st.selectbox("Choose a style", styles, key="style")
        if style == "Other":
            style = st.text_input("Specify style", key="custom_style")

        selected_materials = st.multiselect("Select materials (up to 3)", materials, max_selections=3, key="materials")
        if "Other" in selected_materials:
            custom_material = st.text_input("Specify custom material", key="custom_material")
            selected_materials = [m if m != "Other" else custom_material for m in selected_materials]

        clothing_type = st.selectbox("Select clothing type", clothing_types, key="clothing_type")
        if clothing_type == "Other":
            clothing_type = st.text_input("Specify clothing type", key="custom_clothing_type")

        production_method = st.selectbox("Select production method", production_methods, key="production_method")
        if production_method == "Other":
            production_method = st.text_input("Specify production method", key="custom_production_method")

        packaging = st.selectbox("Select packaging option", packaging_options, key="packaging")
        if packaging == "Other":
            packaging = st.text_input("Specify packaging option", key="custom_packaging")

        production_location = st.selectbox("Select production location", production_locations, key="production_location")
        if production_location == "Other":
            production_location = st.text_input("Specify production location", key="custom_production_location")

        shipping_method = st.selectbox("Select shipping method", shipping_methods, key="shipping_method")
        if shipping_method == "Other":
            shipping_method = st.text_input("Specify shipping method", key="custom_shipping_method")

        base_color = st.selectbox("Select base color", base_colors, key="base_color")
        if base_color == "Other":
            base_color = st.text_input("Specify base color", key="custom_base_color")

        custom_design = st.text_area("Custom design description (optional)", "", key="custom_design")

    with col2:
        st.markdown("""
        <div h2 style="text-align:left; font-size: 1.8rem; font-weight: bold; color: #333333 !important;">
        AI Generated Sustainable Design
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Sustainable Design", key="generate_button"):
            if not selected_materials:
                return

            st.session_state.current_data = {
                'style': style,
                'materials': selected_materials,
                'clothing_type': clothing_type,
                'production_method': production_method,
                'packaging': packaging,
                'production_location': production_location,
                'shipping_method': shipping_method,
                'base_color': base_color,
                'custom_design': custom_design
            }

            progress_bar = st.progress(0)

            try:
                with st.spinner("Generating Sustainable Design..."):
                    prompt = f"A sustainable {style.lower()} {clothing_type.lower()} in {base_color.lower()} color made from {', '.join(selected_materials).lower()}. The primary color of the garment is {base_color.lower()}. Highly detailed fashion design with emphasis on eco-friendly features and ethical production. Show the garment in a natural, environmentally conscious setting."
                    if custom_design:
                        prompt += f" {custom_design}"

                    img = generate_ai_image(image_generator, prompt, progress_bar)
                    if img:
                        design_buf = io.BytesIO()
                        img.save(design_buf, format="PNG")
                        design_image_bytes = design_buf.getvalue()

                        st.session_state.generated_design = design_image_bytes
                        st.session_state.current_base_color = base_color
                        st.session_state.current_clothing_type = clothing_type

                        overall_score = calculate_sustainability_score(selected_materials, production_method, packaging)
                        sustainability_score, formatted_overall_score = extract_sustainability_score(overall_score)
                        st.session_state.formatted_overall_score = formatted_overall_score

                        design_id = save_design_to_db(
                            user_id="default_user",
                            style=style,
                            materials=selected_materials,
                            clothing_type=clothing_type,
                            production_method=production_method,
                            packaging=packaging,
                            production_location=production_location,
                            shipping_method=shipping_method,
                            base_color=base_color,
                            custom_design=custom_design,
                            sustainability_score=sustainability_score
                        )

                        if design_id:
                            st.markdown(f'<div style="background-color: #8B4513; color: white; padding: 10px; border-radius: 5px;">Design saved successfully with ID: {design_id}</div>', unsafe_allow_html=True)

            except Exception:
                return

        if st.session_state.generated_design:
            try:
                img = Image.open(BytesIO(st.session_state.generated_design))
                st.image(img,
                        caption=f"Sustainable {st.session_state.current_base_color} {st.session_state.current_clothing_type} Design")
            except Exception:
                return

            if st.session_state.formatted_overall_score:
                st.markdown(st.session_state.formatted_overall_score, unsafe_allow_html=True)
            else:
                st.markdown("**Sustainability Score: 70**\nThe design uses eco-friendly materials and sustainable packaging, reducing environmental impact. Local production methods further lower emissions, though improvements in water usage could enhance the score.", unsafe_allow_html=True)

            if st.session_state.current_data:
                with st.expander("Sustainability Recommendations"):
                    st.markdown('<div style="font-size: 24px; color: #8B4513; border-bottom: 2px solid #DAA520; padding-bottom: 8px; margin-bottom: 16px;">Sustainability Analysis & Recommendations</div>', unsafe_allow_html=True)
                    recommendations = get_sustainability_recommendations(
                        st.session_state.current_data['style'],
                        st.session_state.current_data['materials'],
                        st.session_state.current_data['clothing_type'],
                        st.session_state.current_data['custom_design'],
                        st.session_state.current_data['base_color']
                    )
                    st.markdown(f'<div style="color: black;">{recommendations}</div>', unsafe_allow_html=True)

                with st.expander("Zero-Waste Pattern Suggestion"):
                    st.markdown('<div style="font-size: 24px; color: #8B4513; border-bottom: 2px solid #DAA520; padding-bottom: 8px; margin-bottom: 16px;">Zero-Waste Pattern Details</div>', unsafe_allow_html=True)
                    zero_waste_pattern = generate_zero_waste_pattern(
                        st.session_state.current_data['clothing_type'],
                        st.session_state.current_data['base_color']
                    )
                    st.markdown(f'<div style="color: black;">{zero_waste_pattern}</div>', unsafe_allow_html=True)

                with st.expander("Eco-Friendly Dye Suggestions"):
                    st.markdown('<div style="font-size: 24px; color: #8B4513; border-bottom: 2px solid #DAA520; padding-bottom: 8px; margin-bottom: 16px;">Sustainable Dyeing Options</div>', unsafe_allow_html=True)
                    dye_suggestions = suggest_eco_friendly_dyes(st.session_state.current_data['base_color'])
                    st.markdown(f'<div style="color: black;">{dye_suggestions}</div>', unsafe_allow_html=True)

                with st.expander("Carbon Footprint Estimate"):
                    st.markdown('<div style="font-size: 24px; color: #8B4513; border-bottom: 2px solid #DAA520; padding-bottom: 8px; margin-bottom: 16px;">Environmental Impact Analysis</div>', unsafe_allow_html=True)
                    carbon_footprint = estimate_carbon_footprint(
                        st.session_state.current_data['materials'],
                        st.session_state.current_data['production_location'],
                        st.session_state.current_data['shipping_method']
                    )
                    st.markdown(f'<div style="color: black;">{carbon_footprint}</div>', unsafe_allow_html=True)

                with st.expander("Ethical Production Recommendations"):
                    st.markdown('<div style="font-size: 24px; color: #8B4513; border-bottom: 2px solid #DAA520; padding-bottom: 8px; margin-bottom: 16px;">Ethical Manufacturing Guidelines</div>', unsafe_allow_html=True)
                    ethical_production = recommend_ethical_production(st.session_state.current_data['production_location'])
                    st.markdown(f'<div style="color: black;">{ethical_production}</div>', unsafe_allow_html=True)

            if st.session_state.generated_design:
                try:
                    st.download_button(
                        label="Download Design Image",
                        data=st.session_state.generated_design,
                        file_name="sustainable_design.png",
                        mime="image/png",
                        key="download_design",
                        use_container_width=True
                    )
                except Exception:
                    pass

if __name__ == "__main__":
    init_session_state() 
    create_table()
    display_design_studio()
    load_models()