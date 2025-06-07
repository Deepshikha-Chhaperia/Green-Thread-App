import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from google.api_core.exceptions import ResourceExhausted
import logging

# Set up logging to file for private debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log to a file
        logging.StreamHandler()  # Optional: log to console for local debugging
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables.")
    st.error("Application configuration error. Please contact support.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

def generate_innovative_textile(base_material, desired_properties, sustainability_goals, additional_requirements, production_method, target_market):
    # Simplified prompt to reduce token usage
    prompt = f"""Generate a unique, sustainable textile with:
    Base Material: {base_material}
    Desired Properties: {', '.join(desired_properties)}
    Sustainability Goals: {', '.join(sustainability_goals)}
    Additional Requirements: {additional_requirements}
    Production Method: {production_method}
    Target Market: {target_market}

    Provide:
    - Composition and structure
    - Innovative features and methods
    - Environmental benefits
    - Applications in {target_market}
    - Care and end-of-life considerations
    - Biodegradability enhancements
    - How it meets {target_market} needs

    Include a guide:
    1. Prepare base material
    2. Incorporate properties
    3. Achieve sustainability goals
    4. Apply production method
    5. Ensure quality control

    Keep the response concise and innovative."""

    model = genai.GenerativeModel('gemini-1.5-flash')  # Use lighter model if available
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            logger.info("Successfully generated textile description.")
            return response.text
        except ResourceExhausted as e:
            logger.warning(f"ResourceExhausted error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached for ResourceExhausted error.")
                return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

def sustainable_textile_generator():
    st.markdown("""
    <style>
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
        margin-bottom: 20px;
    }
    .stApp h1 span {
        color: #DAA520;
    }
    /* Ensure h3 headings (used for ###) are black */
    .stApp h3, .main .block-container h3, div[data-testid="stMarkdownContainer"] h3 {
        color: black !important;
    }
    /* Ensure subheaders (h2) are black with high specificity */
    .stApp h2, .main .block-container h2, div[data-testid="stMarkdownContainer"] h2 {
        color: black !important;
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
    .stButton>button, .stDownloadButton>button {
        color: white !important;
        background-color: #333333 !important;
        border-radius: 4px;
        padding: 10px 24px;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        opacity: 0.8;
    }
    .stSelectbox > div > div, .stMultiSelect div[role="button"] {
        background-color: #333333;
        color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
    .stTextInput input, .stTextArea textarea {
        color: black !important;
        background-color: white !important;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
    .stMarkdown, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1>SUSTAINABLE <span>TEXTILE GENERATOR</span></h1>', unsafe_allow_html=True)
    st.write("Create an innovative, sustainable textile with enhanced durability and minimal environmental impact!")

    # Options for dropdowns
    base_materials = ["Organic Cotton", "Recycled Polyester", "Organic Hemp", "Bamboo", "Lyocell (Tencel)", "Recycled Nylon", "Organic Linen", "Pineapple Leather", "Mushroom Leather", "Seaweed Fiber", "Other"]
    property_options = ["Water-resistant", "Breathable", "Stretchy", "Wrinkle-resistant", "UV-protective", "Antibacterial", "Moisture-wicking", "Thermal-regulating", "Odor-resistant", "Quick-drying", "Biodegradable", "Hypoallergenic", "Other"]
    sustainability_options = ["Biodegradable", "Low water usage", "Energy-efficient production", "Recyclable", "Zero-waste manufacturing", "Non-toxic dyes", "Carbon-neutral", "Locally sourced", "Closed-loop production", "Regenerative agriculture", "Other"]
    production_methods = ["Weaving", "Knitting", "Non-woven", "3D Printing", "Electrospinning", "Nanotechnology", "Biotechnology", "Other"]
    target_markets = ["Activewear", "Casual wear", "Formal wear", "Outdoor gear", "Medical textiles", "Industrial use", "Home furnishings", "Other"]

    # Input fields
    base_material = st.selectbox("Select Base Material:", base_materials)
    if base_material == "Other":
        base_material = st.text_input("Specify the base material:")

    desired_properties = st.multiselect("Select Desired Properties (up to 4):", property_options, max_selections=4)
    if "Other" in desired_properties:
        other_property = st.text_input("Specify the other desired property:")
        desired_properties = [prop if prop != "Other" else other_property for prop in desired_properties]

    sustainability_goals = st.multiselect("Select Sustainability Goals (up to 4):", sustainability_options, max_selections=4)
    if "Other" in sustainability_goals:
        other_goal = st.text_input("Specify the other sustainability goal:")
        sustainability_goals = [goal if goal != "Other" else other_goal for goal in sustainability_goals]

    production_method = st.selectbox("Select Production Method:", production_methods)
    if production_method == "Other":
        production_method = st.text_input("Specify the production method:")

    target_market = st.selectbox("Select Target Market:", target_markets)
    if target_market == "Other":
        target_market = st.text_input("Specify the target market:")

    additional_requirements = st.text_area("Additional requirements or challenges:")

    # Cache results to avoid redundant API calls
    cache_key = f"{base_material}_{'_'.join(sorted(desired_properties))}_{'_'.join(sorted(sustainability_goals))}_{additional_requirements}_{production_method}_{target_market}"
    if "textile_result" not in st.session_state:
        st.session_state.textile_result = {}

    if st.button("Generate Innovative Textile"):
        if not all([base_material, desired_properties, sustainability_goals, production_method, target_market]):
            st.warning("Please complete all required fields.")
        else:
            with st.spinner("Generating your innovative, sustainable textile..."):
                # Check cache first
                if cache_key in st.session_state.textile_result:
                    textile_description = st.session_state.textile_result[cache_key]
                    logger.info("Retrieved result from cache.")
                else:
                    textile_description = generate_innovative_textile(base_material, desired_properties, sustainability_goals, additional_requirements, production_method, target_market)
                    if textile_description:
                        st.session_state.textile_result[cache_key] = textile_description
                        logger.info("Generated new textile description and cached it.")

                if textile_description:
                    st.write("### Your Innovative Sustainable Textile")
                    st.write(textile_description)
                    st.markdown("""
                    ### Next Steps:
                    1. Review the creation guide above.
                    2. Consult material scientists to validate the concept.
                    3. Conduct feasibility studies and prototyping.
                    4. Assess lifecycle impact.
                    5. Explore partnerships with sustainable manufacturers.
                    6. Test performance and sustainability claims.
                    7. Consider patenting unique aspects.
                    """, unsafe_allow_html=True)
                else:
                    st.error("Unable to generate textile description due to a temporary issue. Please try again later or contact support.")
                    logger.error("Failed to generate textile description after retries.")

if __name__ == "__main__":
    sustainable_textile_generator()