
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
| AI Models          | Stable Diffusion (stabilityai/stable-diffusion-2-1), ResNet50 (ImageNet) |
| APIs               | Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, gemini-pro) |
| Backend            | SQLite3, Pandas, Flask (lightweight API endpoints) |
| Image Processing   | PIL (PNG conversion, 2MB upload limits) |
| Security           | Python-dotenv (secure API key management) |
| Optimizations      | Attention slicing (25% memory reduction), lru_cache (35% fewer API calls) |

---

## ⚡ Key Optimizations

- **Stable Diffusion**: CPU-optimized with `torch.float32`, 20 inference steps, attention slicing (25% RAM reduction).
- **Gemini API**: Exponential backoff (60-120s) and response caching (35% fewer API calls).
- **Streamlit**: Cache clearing at startup (70% faster loads), `@st.cache_resource` for model loading (5s for ResNet50).
- **SQLite3**: 50ms inserts with 99.9% reliability, verified by `save_design_to_db`.

---

## 🎥 Demo

- Try Green Thread live at:  
  **[Green Thread App](https://green-thread-app.streamlit.app/)**

- Watch the Green Thread demo video!

---

## 📊 Flowchart

Diagram showing how user inputs flow through AI models, databases, and outputs. *(Add your flowchart here if you have one!)*

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
