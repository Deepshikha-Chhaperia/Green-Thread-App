import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_innovative_textile(base_material, desired_properties, sustainability_goals, additional_requirements, production_method, target_market):
    prompt = f"""Create a completely new and unique innovative textile based on the following inputs:

    Base Material: {base_material}
    Desired Properties: {', '.join(desired_properties)}
    Sustainability Goals: {', '.join(sustainability_goals)}
    Additional Requirements: {additional_requirements}
    Production Method: {production_method}
    Target Market: {target_market}

    Generate a detailed description of a novel, never-before-seen textile that:
    1. Uses the base material as a starting point but transforms it in an unprecedented way
    2. Incorporates the desired properties through innovative techniques
    3. Meets and exceeds the specified sustainability goals
    4. Significantly improves durability and reduces environmental impact beyond current standards
    5. Requires fewer resources in production through groundbreaking processes
    6. Includes cutting-edge biodegradable materials or treatments that cause minimal environmental damage
    7. Addresses the additional requirements provided with unique solutions
    8. Revolutionizes the specified production method
    9. Sets new standards for sustainability and performance in the target market

    Provide the following information:
    - Unique composition and structure of the new textile
    - Innovative features and the novel methods used to achieve them
    - Groundbreaking environmental benefits and resource usage reduction techniques
    - Potential applications in fashion or other industries, highlighting its versatility
    - Any special care or end-of-life considerations that set this textile apart
    - Specific, unique treatments or processes that enhance biodegradability or reduce environmental damage
    - How the textile meets and exceeds the needs of the target market while setting new sustainability benchmarks

    Additionally, provide a step-by-step guide on how to create this innovative textile:
    1. Detailed instructions for preparing the base material
    2. Specific processes for incorporating the unique properties
    3. Novel techniques for achieving the sustainability goals
    4. Step-by-step explanation of the innovative production method
    5. Guidelines for quality control and testing to ensure the textile meets its groundbreaking standards

    Format the response as a detailed, well-structured description of the innovative textile, followed by the step-by-step creation guide. Ensure that every aspect of this textile is presented as a new and unique innovation in the field of sustainable textiles."""

    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    return response.text

def sustainable_textile_generator():
    st.markdown("""
    <style>
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

    st.markdown('<h1>SUSTAINABLE <span> TEXTILE GENERATOR </span></h1>', unsafe_allow_html=True)
    st.write("Create your own innovative, sustainable textile that performs better in terms of durability and environmental impact!")

    base_materials = ["Organic Cotton", "Recycled Polyester", "Organic Hemp", "Bamboo", "Lyocell (Tencel)", "Recycled Nylon", "Organic Linen", "Pineapple Leather", "Mushroom Leather", "Seaweed Fiber", "Other"]
    property_options = ["Water-resistant", "Breathable", "Stretchy", "Wrinkle-resistant", "UV-protective", "Antibacterial", "Moisture-wicking", "Thermal-regulating", "Odor-resistant", "Quick-drying", "Biodegradable", "Hypoallergenic", "Other"]
    sustainability_options = ["Biodegradable", "Low water usage", "Energy-efficient production", "Recyclable", "Zero-waste manufacturing", "Non-toxic dyes", "Carbon-neutral", "Locally sourced", "Closed-loop production", "Regenerative agriculture", "Other"]
    production_methods = ["Weaving", "Knitting", "Non-woven", "3D Printing", "Electrospinning", "Nanotechnology", "Biotechnology", "Other"]
    target_markets = ["Activewear", "Casual wear", "Formal wear", "Outdoor gear", "Medical textiles", "Industrial use", "Home furnishings", "Other"]

    base_material = st.selectbox("Select Base Material:", base_materials)
    if base_material == "Other":
        base_material = st.text_input("Please specify the base material:")

    desired_properties = st.multiselect("Select Desired Properties (up to 4):", property_options, max_selections=4)
    if "Other" in desired_properties:
        other_property = st.text_input("Please specify the other desired property:")
        desired_properties = [prop if prop != "Other" else other_property for prop in desired_properties]

    sustainability_goals = st.multiselect("Select Sustainability Goals (up to 4):", sustainability_options, max_selections=4)
    if "Other" in sustainability_goals:
        other_goal = st.text_input("Please specify the other sustainability goal:")
        sustainability_goals = [goal if goal != "Other" else other_goal for goal in sustainability_goals]

    production_method = st.selectbox("Select Production Method:", production_methods)
    if production_method == "Other":
        production_method = st.text_input("Please specify the production method:")

    target_market = st.selectbox("Select Target Market:", target_markets)
    if target_market == "Other":
        target_market = st.text_input("Please specify the target market:")

    additional_requirements = st.text_area("Any additional requirements or specific challenges to address:")

    if st.button("Generate Innovative Textile"):
        if base_material and desired_properties and sustainability_goals and production_method and target_market:
            with st.spinner("Generating your innovative, sustainable textile..."):
                textile_description = generate_innovative_textile(base_material, desired_properties, sustainability_goals, additional_requirements, production_method, target_market)
                #st.subheader("Your Innovative Sustainable Textile:")
                st.write(textile_description)
                
                st.markdown("""
                <div h2 style="text-align: left; font-size: 2.0rem; font-weight: bold; color: #333333;">
                Next Steps:
                </div>
                """, unsafe_allow_html=True)
                st.write("1. Review the step-by-step creation guide provided above.")
                st.write("2. Consult with material scientists to refine and validate the concept.")
                st.write("3. Conduct feasibility studies and small-scale prototyping.")
                st.write("4. Assess the lifecycle impact of this new textile.")
                st.write("5. Explore partnerships with innovative sustainable manufacturers.")
                st.write("6. Test the textile's performance and sustainability claims for the target market.")
                st.write("7. Consider patenting unique aspects of your innovative textile.")
        else:
            st.warning("Please make selections for all required fields before generating.")
if __name__ == "__main__":
    sustainable_textile_generator()