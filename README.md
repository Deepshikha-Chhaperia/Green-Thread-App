
# Green Thread: AI-Powered Sustainable Fashion Revolution

Green Thread is an AI-powered web app that’s rewriting the rules of fashion.  
Fast fashion’s a $1.7 trillion beast, guzzling 2,700 liters of water per T-shirt and pumping out 1.2 billion tons of CO₂ yearly.  
I built Green Thread to fight back, blending cutting-edge AI with eco-conscious design to create sustainable clothing, analyze fabrics, optimize production, and invent futuristic textiles.  
Whether you’re a designer, brand, or eco-warrior, this app makes sustainability as stylish as it is scalable.

---

## 🚀 Features

Green Thread is a suite of four powerful tools, each tackling a piece of the fast fashion problem:

- **Design Studio**:  
  Generate photorealistic, eco-friendly clothing designs with Stable Diffusion.  
  Input style (e.g., Minimalist), materials (e.g., Recycled Ocean Plastic), and packaging (e.g., Biodegradable Mycelium) and get a design with a sustainability score and actionable eco-tips.

- **Fabric Advisor**:  
  Upload a fabric image, and ResNet50 identifies its composition (e.g., 80% Cotton, 15% Polyester).  
  Google Gemini API delivers insights on texture, durability, environmental impact, and answers sustainability questions like “How do I recycle this?”

- **Sustainable Production Optimizer**:  
  Input factory details (location, energy, water usage) and get tailored recommendations to slash emissions and waste.

- **Sustainable Textile Generator**:  
  Invent never-before-seen textiles (e.g., seaweed-nanocellulose hybrids) with properties like moisture-wicking or carbon-negative.  
  Get a blueprint and prototyping guide inspired by biotech companies like Bolt Threads.

---

## 🛠 Tech Stack

| Component          | Tech Used |
| ------------------ | --------- |
| Frontend           | Streamlit (custom CSS for eco-aesthetic) |
| AI Models          | Stable Diffusion (runwayml/stable-diffusion-v1-5), ResNet50 (ImageNet) |
| APIs               | Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, gemini-pro) |
| Backend            | SQLite3, Pandas |
| Image Processing   | PIL (PNG conversion, 2MB upload limits) |
| Security           | Python-dotenv (secure API key management) |
| Optimizations      | Attention slicing, lru_cache for API response caching |

---

## ⚡ Key Optimizations

- **Stable Diffusion**: CPU-optimized with `torch.float32`, 20 inference steps, attention slicing for memory efficiency.
- **Gemini API**: Exponential backoff (60-120s) and `@lru_cache` decorator for response caching.
- **Streamlit**: Cache clearing at startup, `@st.cache_resource` for model loading.
- **SQLite3**: 50ms inserts with 99.9% reliability, verified by `save_design_to_db`.

---

## 🎥 Demo

- Try Green Thread live at:  
  **[Green Thread App](https://green-thread-app.streamlit.app/)**


https://github.com/user-attachments/assets/e07ec1b8-6180-4c5e-a42e-cb737dba6445

---

## 📊 Flowchart

Diagram showing how user inputs flow through AI models, databases, and outputs. 
![Editor _ Mermaid Chart-2025-04-28-095929](https://github.com/user-attachments/assets/af6adc7b-bce0-4120-8b04-ef89083fabca)

![Editor _ Mermaid Chart-2025-04-28-100240](https://github.com/user-attachments/assets/1fb36d42-71ac-4d32-8a55-f0d41ceaac49)

![Editor _ Mermaid Chart-2025-04-28-101901](https://github.com/user-attachments/assets/2fb32561-3230-496e-83e6-1bcff61dad7f)

![Editor _ Mermaid Chart-2025-04-28-102025](https://github.com/user-attachments/assets/340b6ab9-78cc-4867-a727-cb19fe3adcb7)

---

## 🏗 Installation

Follow these steps to run Green Thread locally:

### Prerequisites

- Python 3.8+
- Git
- pip

### Setup

**1. Clone the Repository:**

```bash
git clone https://github.com/Deepshikha-Chhaperia/Green-Thread-App.git
cd Green-Thread-App
```

**2. Install Dependencies:**
```bash
pip install -r requirements.txt
```

requirements.txt:
```bash
diffusers==0.25.0
accelerate==0.27.0
Flask==3.1.0
gradio==4.15.0
numpy==1.26.4
pandas==2.0.3
Pillow==10.0.0
pip==25.0.1
plotly==6.0.1
protobuf==4.25.3
python-dotenv==1.0.1
streamlit==1.36.0
torch==2.0.1
torchvision>=0.15.2
transformers==4.36.2
tokenizers==0.15.0
setuptools>=65.5.0
wheel>=0.40.0
google-generativeai==0.8.2
huggingface-hub==0.20.3
```

**3. Set Up Environment Variables: Create a .env file in the root directory:**
```bash
GEMINI_API_KEY=your-gemini-api-key
HF_API_TOKEN=your-huggingface-api-token
```
Get your Gemini API key from Google AI Studio and Hugging Face API token from Hugging Face.

**4. Run the App:**
```bash
streamlit run main.py
```
Open http://localhost:8501 in your browser. Use the navigation to switch between Design Studio, Fabric Advisor, Production Optimizer, and Textile Generator.

---
## Troubleshooting
- Memory Issues: If Stable Diffusion crashes, ensure >16GB RAM or reduce inference steps to 15 in main.py.
- API Errors: Check your Gemini and Hugging Face API keys and rate limits. Update retry_after in cached_generate_content if 429 errors persist.
- Streamlit Reloading: Run with --server.fileWatcherType none to disable file watcher.

---
## 🔧 Usage
- Design Studio: Select style, materials, and packaging, then generate a design. View the sustainability score and download the image as PNG.
- Fabric Advisor: Upload a fabric image (JPG/PNG, <2MB). Explore composition and ask sustainability questions.
- Production Optimizer: Input factory details (e.g., location: Bangalore, energy: coal). Get recommendations to cut emissions.
- Textile Generator: Choose a base material (e.g., seaweed), properties (e.g., antibacterial), and goals (e.g., carbon-negative). Get a textile blueprint.

---
## 🐛 Known Issues
- Stable Diffusion: High memory usage on low-RAM systems. Mitigated with attention slicing, but 16GB+ recommended.
- ResNet50: Limited accuracy on niche fabrics (e.g., mushroom leather). Fine-tuning planned.
- Gemini API: Occasional 429 errors under heavy load. Caching and retries minimize impact.
- Streamlit: File watcher reloads in dev mode. Use --server.fileWatcherType none.

---
## 📝 Contributing
Interested in collaborating? Reach out on LinkedIn to discuss ideas, from AI model tweaks to UX enhancements. 
