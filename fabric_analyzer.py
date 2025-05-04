import streamlit as st
from PIL import Image #opening, manipulating and saving various image file formats
import torch
import torchvision.transforms as transforms #resizing, cropping
from torchvision.models import resnet50, ResNet50_Weights #dl model for img rec & classi
import os
from dotenv import load_dotenv #securely storing the sensitive info
import google.generativeai as genai
import io

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY) #configures genai lib to use gemini api key

@st.cache_resource
def load_model():
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2) 
    #we want to use pre trained weights for imagenet classification
    #model is loaded with weights from a previous training on ImageNet, 
    # a large dataset of labeled images.
    model.eval()
    return model

def preprocess_image(image):
    #chain multiple transformations together
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(), #scaled from 0-255 to 0.0-1.0. more stable & efficient training
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]) #better model performance. these are the standard values calculated over the ImageNet dataset
    return transform(image).unsqueeze(0)
#PyTorch models often expect input data in batches, even if you're only processing a single image. 
# Adding this dimension effectively creates a batch of size 1. 

def analyze_image(model, image):
    with torch.no_grad(): #when we are using the model for prediction not training
        output = model(preprocess_image(image))
        probabilities = torch.nn.functional.softmax(output[0], dim=0)#raw score to probabilities
#might output predictions for a batch of images, even if you input only one. 
# Selecting the first element extracts the predictions for your single image.
    
    top_prob, top_catid = torch.topk(probabilities, 5)
    categories = ResNet50_Weights.IMAGENET1K_V2.meta["categories"]
    
    return [{"class": categories[top_catid[i]], "probability": top_prob[i].item()} for i in range(5)]

def get_fabric_analysis(image_description):
    prompt = f"""Based on this fabric description: {image_description}
    Provide a brief analysis of the fabric's composition and key properties:
    - Estimated composition (e.g., "70% Cotton, 30% Polyester")
    - Texture
    - Durability
    - Breathability
    Format as a short paragraph, focusing on the most likely characteristics."""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def get_sustainability_answer(question, fabric_analysis):
    prompt = f"""Given this fabric analysis: {fabric_analysis}
    
    Answer the following question about sustainable fashion:
    {question}
    
    Provide a concise, practical answer focusing on sustainability and environmental impact."""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def interactive_sustainable_fabric_advisor():
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

    st.markdown('<h1>SUSTAINABLE <span> FABRIC ADVISOR </span></h1>', unsafe_allow_html=True)
    st.write("Get fabric insights and personalized sustainability tips by uploading images—our Sustainable Fabric Advisor analyzes composition and properties for eco-friendly choices!")
    st.write("Upload a fabric image to get sustainability insights!")

    uploaded_file = st.file_uploader("Choose a fabric image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        try:
            # Load and convert image
            image = Image.open(uploaded_file).convert('RGB')
            
            # Convert PIL Image to bytes for Streamlit
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Display image (removed use_container_width)
            st.image(img_byte_arr, caption="Your Fabric")
            
            model = load_model()
            
            with st.spinner("Analyzing your fabric..."):
                predictions = analyze_image(model, image)
                image_description = ", ".join([f"{pred['class']} ({pred['probability']:.2%})" for pred in predictions])

                fabric_analysis = get_fabric_analysis(image_description)
                st.subheader("Fabric Analysis")
                st.write(fabric_analysis)

            # Predefined sustainability questions
            sustainability_questions = [
                "How can I reuse this fabric?",
                "What are some eco-friendly alternatives to this fabric?",
                "How can I make this fabric more sustainable?",
                "What are the best practices for caring for this fabric sustainably?",
                "How can I recycle or upcycle items made from this fabric?",
                "What is the environmental impact of this fabric?",
                "How can I reduce water usage when cleaning this fabric?",
                "Are there any certifications I should look for when buying this type of fabric?",
                "How can I extend the lifespan of items made from this fabric?",
                "What are some sustainable dyeing options for this fabric?",
                "How does the production of this fabric impact local communities?",
                "What are some innovative sustainable technologies being used with this type of fabric?",
                "How can I shop more responsibly for this type of fabric?",
                "What are some common misconceptions about the sustainability of this fabric?",
                "How can I advocate for more sustainable practices in the production of this fabric?"
            ]

            st.subheader("Explore Sustainability Options")
            selected_question = st.selectbox("Choose a sustainability question:", ["Select a question..."] + sustainability_questions)

            if selected_question != "Select a question...":
                with st.spinner("Generating sustainability insights..."):
                    answer = get_sustainability_answer(selected_question, fabric_analysis)
                    st.write(answer)

            st.subheader("Ask Your Own Question")
            custom_question = st.text_input("Type your sustainability question here:")
            if custom_question:
                with st.spinner("Answering your question..."):
                    custom_answer = get_sustainability_answer(custom_question, fabric_analysis)
                    st.write(custom_answer)
                    
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            st.write("Please try uploading a different image or check the file format.")

if __name__ == "__main__":
    interactive_sustainable_fabric_advisor()