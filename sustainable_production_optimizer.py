import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from google.api_core.exceptions import NotFound, ResourceExhausted
import logging

# Set up logging to file for private debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log to a file
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

def get_sustainable_recommendations(production_details):
    prompt = f"""
    For a fashion item with these production details:
    {production_details}
    
    Provide location-specific sustainability recommendations for:
    1. **Energy Usage**: Renewable energy and efficiency practices.
    2. **Water Conservation**: Water-saving and treatment methods.
    3. **Material Sourcing**: Sustainable materials based on local availability.
    4. **Supply Chain**: Emission reduction and logistics optimization.
    5. **Waste Reduction**: Recycling and upcycling strategies.
    6. **Chemical Usage**: Eco-friendly chemical alternatives.
    7. **Labor Practices**: Fair and safe working conditions.
    8. **Packaging**: Sustainable packaging options.
    9. **Certifications**: Relevant sustainability certifications.
    10. **Technology**: Innovative tech for sustainability.
    11. **Climate Resilience**: Strategies for local climate impacts.
    12. **Community Engagement**: Local community benefits.

    Tailor recommendations to the location, regulations, and climate. Highlight **key recommendations** in bold. Include environmental benefits and estimated cost implications where possible. Keep concise and actionable.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            logger.info("Successfully generated sustainability recommendations.")
            return response.text
        except NotFound as e:
            logger.error(f"Model not found error: {e}")
            st.error("Unable to generate recommendations due to a configuration issue. Please contact support.")
            return None
        except ResourceExhausted as e:
            logger.warning(f"ResourceExhausted error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("Max retries reached for ResourceExhausted error.")
                st.error("Unable to generate recommendations due to a temporary issue. Please try again later or contact support.")
                return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error("An unexpected issue occurred. Please try again later or contact support.")
            return None

def display_sustainable_production_optimizer():
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
    .stMarkdown, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label, .stSlider label {
        color: black !important;
    }
    /* Style slider tick marks and labels to be black with high specificity */
    .stSlider [data-testid="stTickBar"] div, .stSlider [data-testid="stTickBar"] span {
        color: black !important;
        fill: black !important;
    }
    .stSlider [data-testid="stTickBar"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1>SUSTAINABLE <span>PRODUCTION OPTIMIZER</span></h1>', unsafe_allow_html=True)
    st.markdown('Optimize your fashion production with tailored sustainability tips—our tool analyzes everything from energy use to community engagement for a greener process!')
    st.write("Provide details about your current processes to get sustainability recommendations.")

    # Production Location
    location = st.text_input("Production Location (City, Country)", "")

    # Climate Zone
    climate_zone = st.selectbox(
        "Climate Zone",
        ["Tropical", "Dry (Arid and Semi-arid)", "Temperate", "Continental", "Polar"]
    )

    # Manufacturing Method
    manufacturing_method = st.selectbox(
        "Manufacturing Method",
        ["Traditional Mass Production", "Automated/Smart Factory", "Slow Fashion", "Artisanal/Handmade", "On-Demand Production", "Semi-Automated", "Modular Production"]
    )

    # Production Scale
    production_scale = st.selectbox(
        "Production Scale",
        ["Small (< 1,000 units/month)", "Medium (1,000 - 10,000 units/month)", "Large (10,000 - 100,000 units/month)", "Very Large (> 100,000 units/month)"]
    )

    # Energy Source
    energy_source = st.multiselect(
        "Current Energy Sources",
        ["Grid Electricity", "Natural Gas", "Coal", "Solar", "Wind", "Hydroelectric", "Biomass", "Geothermal", "Nuclear", "Diesel Generators"]
    )

    # Water Usage
    water_usage = st.slider("Daily Water Usage (in liters)", 0, 1000000, 10000)

    # Water Source
    water_source = st.multiselect(
        "Water Sources",
        ["Municipal Supply", "Groundwater", "Rainwater Harvesting", "Recycled Water", "Surface Water (Rivers/Lakes)", "Desalination"]
    )

    # Main Materials
    materials = st.multiselect(
        "Main Materials Used",
        ["Cotton", "Organic Cotton", "Recycled Cotton", "Polyester", "Recycled Polyester", "Nylon", "Recycled Nylon", "Wool", "Recycled Wool", 
         "Leather", "Vegan Leather", "Silk", "Peace Silk", "Linen", "Hemp", "Bamboo", "Viscose", "Lyocell", "Modal", "Acrylic", "Elastane", 
         "Recycled Plastics", "Bioplastics", "Cork", "Piñatex (Pineapple Leather)", "Mushroom Leather", "Seacell", "Econyl"]
    )

    # Chemical Usage
    chemicals = st.multiselect(
        "Chemicals Used in Production",
        ["Synthetic Dyes", "Natural Dyes", "Bleaches", "Solvents", "Finishes", "Adhesives", "Tanning Agents", "Fixing Agents", "Softeners", 
         "Water Repellents", "Flame Retardants", "Enzyme Treatments", "None"]
    )

    # Waste Management
    waste_management = st.multiselect(
        "Current Waste Management Practices",
        ["Recycling", "Composting", "Landfill", "Incineration", "Upcycling", "Zero-waste initiatives", "Wastewater Treatment", 
         "Hazardous Waste Management", "Fabric Scrap Reuse", "Donate Excess Materials"]
    )

    # Transportation
    transportation = st.multiselect(
        "Main Transportation Methods",
        ["Truck", "Ship", "Air Freight", "Rail", "Local suppliers (minimal transportation)", "Electric Vehicles", "Hybrid Vehicles", 
         "Cargo Bikes (for local delivery)", "Consolidated Shipping"]
    )

    # Certifications
    certifications = st.multiselect(
        "Current Sustainability Certifications",
        ["GOTS (Global Organic Textile Standard)", "Fairtrade", "OEKO-TEX", "Bluesign", "Cradle to Cradle", "ISO 14001", "SA8000", 
         "Better Cotton Initiative (BCI)", "Leather Working Group (LWG)", "Forest Stewardship Council (FSC)", "REACH Compliance", 
         "Fair Wear Foundation", "Carbon Trust Standard", "B Corp Certification", "None"]
    )

    # Packaging
    packaging = st.multiselect(
        "Current Packaging Materials",
        ["Plastic", "Recycled Plastic", "Cardboard", "Recycled Cardboard", "Paper", "Recycled Paper", "Biodegradable Plastics", 
         "Compostable Materials", "Reusable Packaging", "Minimal Packaging", "Fabric Bags", "Plant-based Packaging"]
    )

    # Worker Welfare
    worker_welfare = st.multiselect(
        "Worker Welfare Initiatives",
        ["Fair Wages", "Safe Working Conditions", "Regular Health Check-ups", "Worker Education Programs", "Child Care Facilities", 
         "Mental Health Support", "Freedom of Association", "Grievance Mechanisms", "Diversity and Inclusion Programs", "None"]
    )

    # Technology Usage
    technology_usage = st.multiselect(
        "Technology Used in Production",
        ["3D Design Software", "AI for Demand Forecasting", "IoT for Equipment Monitoring", "Blockchain for Supply Chain Transparency", 
         "Digital Printing", "Laser Cutting", "Automated Cutting Machines", "Robotic Sewing", "Virtual Sampling", "ERP Systems", "None"]
    )

    # Local Community Engagement
    community_engagement = st.multiselect(
        "Local Community Engagement Initiatives",
        ["Local Hiring", "Skills Training Programs", "Educational Partnerships", "Community Recycling Programs", "Local Sourcing Initiatives", 
         "Environmental Clean-up Events", "Open Factory Days", "Sponsorship of Local Events", "None"]
    )

    # Cache results to avoid redundant API calls
    production_details = f"""
    Production Location: {location}
    Climate Zone: {climate_zone}
    Manufacturing Method: {manufacturing_method}
    Production Scale: {production_scale}
    Energy Sources: {', '.join(energy_source)}
    Daily Water Usage: {water_usage} liters
    Water Sources: {', '.join(water_source)}
    Main Materials: {', '.join(materials)}
    Chemicals Used: {', '.join(chemicals)}
    Waste Management: {', '.join(waste_management)}
    Transportation Methods: {', '.join(transportation)}
    Current Certifications: {', '.join(certifications)}
    Packaging Materials: {', '.join(packaging)}
    Worker Welfare Initiatives: {', '.join(worker_welfare)}
    Technology Used: {', '.join(technology_usage)}
    Community Engagement: {', '.join(community_engagement)}
    """
    cache_key = production_details
    if "recommendations_cache" not in st.session_state:
        st.session_state.recommendations_cache = {}

    if st.button("Get Sustainability Recommendations"):
        if not location or not energy_source or not water_source or not materials:
            st.warning("Please complete all required fields (Location, Energy Sources, Water Sources, Materials).")
        else:
            with st.spinner("Analyzing and generating recommendations..."):
                if cache_key in st.session_state.recommendations_cache:
                    recommendations = st.session_state.recommendations_cache[cache_key]
                    logger.info("Retrieved recommendations from cache.")
                else:
                    recommendations = get_sustainable_recommendations(production_details)
                    if recommendations:
                        st.session_state.recommendations_cache[cache_key] = recommendations
                        logger.info("Generated new recommendations and cached them.")

                if recommendations:
                    st.markdown(recommendations)
                else:
                    st.error("Unable to generate recommendations at this time. Please try again later or contact support.")

if __name__ == "__main__":
    display_sustainable_production_optimizer()