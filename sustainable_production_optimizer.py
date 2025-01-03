import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_sustainable_recommendations(production_details):
    prompt = f"""
    Based on the following production details for a fashion item:
    {production_details}
    
    Provide comprehensive, location-specific recommendations for improving sustainability in the following areas:
    1. Energy Usage: Suggest renewable energy alternatives and energy-efficient practices specific to the production location.
    2. Water Conservation: Recommend water-saving techniques and water treatment methods considering local water scarcity issues.
    3. Material Sourcing: Propose sustainable alternatives to traditional materials, considering local availability and climate conditions.
    4. Supply Chain Optimization: Suggest ways to reduce transportation emissions and improve logistics based on the factory location.
    5. Waste Reduction: Recommend strategies for minimizing waste in the production process, including local recycling and upcycling opportunities.
    6. Chemical Usage: Suggest eco-friendly alternatives to harmful chemicals used in production, considering local regulations.
    7. Labor Practices: Provide recommendations for ensuring fair and safe working conditions, taking into account local labor laws and cultural contexts.
    8. Packaging: Suggest sustainable packaging alternatives and reduction strategies, considering local recycling infrastructure.
    9. Certifications: Recommend relevant sustainability certifications to pursue, including any region-specific certifications.
    10. Technology Integration: Propose innovative technologies that can enhance sustainability, considering local technological infrastructure and availability.
    11. Climate Resilience: Suggest strategies to make the production process more resilient to local climate change impacts.
    12. Community Engagement: Recommend ways to engage with and benefit the local community through sustainable practices.

    For each area, provide specific, actionable recommendations tailored to the given production details and location.
    Include potential environmental benefits and, where possible, estimated cost implications of implementing these changes.
    Highlight the most important and impactful recommendations using **bold text**.
    Consider local regulations, climate, resources, and cultural factors in your recommendations.
    """

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def display_sustainable_production_optimizer():
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
    /* Ensure all labels, including slider labels, are black */
    .stSlider label, .stSlider .stMarkdown p {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1>SUSTAINABLE <span> PRODUCTION OPTIMIZER </span></h1>', unsafe_allow_html=True)
    st.markdown('Optimize your fashion production with tailored sustainability tips—our tool analyzes everything from energy use to community engagement for a greener process!')
    st.write("Optimize your fashion production for sustainability by providing details about your current processes")

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
        "Main Transportation Methods for Materials and Products",
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

    if st.button("Get Sustainability Recommendations"):
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

        with st.spinner("Analyzing and generating recommendations..."):
            recommendations = get_sustainable_recommendations(production_details)

        st.subheader("Sustainability Recommendations")
        st.markdown(recommendations)

if __name__ == "__main__":
    display_sustainable_production_optimizer()