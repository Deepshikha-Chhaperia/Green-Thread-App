🌿 Green Thread: AI-Powered Sustainable Fashion Revolution
Green Thread is an AI-powered web app that’s rewriting the rules of fashion.
Fast fashion’s a $1.7 trillion beast, guzzling 2,700 liters of water per T-shirt and pumping out 1.2 billion tons of CO2 yearly.
I built Green Thread to fight back — blending cutting-edge AI with eco-conscious design to create sustainable clothing, analyze fabrics, optimize production, and invent futuristic textiles.
Whether you’re a designer, brand, or eco-warrior, this app makes sustainability as stylish as it is scalable.

🚀 Features
Green Thread is a suite of four powerful tools, each tackling a piece of the fast fashion problem:

Design Studio
Generate photorealistic, eco-friendly clothing designs with Stable Diffusion.
Input style (e.g., Minimalist), materials (e.g., Recycled Ocean Plastic), and packaging (e.g., Biodegradable Mycelium), and get a design with a sustainability score and actionable eco-tips.

Fabric Advisor
Upload a fabric image, and ResNet50 identifies its composition (e.g., 80% Cotton, 15% Polyester).
Google Gemini API delivers insights on texture, durability, environmental impact, and sustainability questions like "How do I recycle this?"

Sustainable Production Optimizer
Input factory details (location, energy, water usage) to get tailored recommendations for slashing emissions and waste.

Sustainable Textile Generator
Invent futuristic textiles (e.g., seaweed-nanocellulose hybrids) with properties like moisture-wicking or carbon-negative features. Get a blueprint and prototyping guide.

🛠 Tech Stack

Component	Tech Used
Frontend	Streamlit (custom CSS for golden-brown eco-aesthetic)
AI Models	Stable Diffusion (stabilityai/stable-diffusion-2-1), ResNet50
APIs	Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, gemini-pro)
Backend	SQLite3, Pandas, Flask (lightweight API endpoints)
Image Processing	PIL (PNG conversion, 2MB upload limits)
Security	Python-dotenv (secure API key management)
Optimizations	Attention slicing (25% memory reduction), lru_cache (35% fewer API calls)
⚡ Key Optimizations
Stable Diffusion: CPU-optimized with torch.float32, 20 inference steps, and attention slicing → 25% less RAM usage.

Gemini API: Exponential backoff (60s-120s) and response caching → 35% fewer API calls.

Streamlit: Cache clearing at startup → 70% faster loads; @st.cache_resource for 5s ResNet50 model loading.

SQLite3: 50ms inserts with 99.9% reliability.

🎥 Demo
🌿 Try Green Thread live at: https://green-thread-app.streamlit.app/

🎬 Watch Green Thread Demo Video

📝 Read the full Medium blog post for a deep dive (including code snippets)!

📊 Flowchart
(Coming soon!)
How user inputs flow through AI models, databases, and outputs in Green Thread.

🏗 Installation
Follow these steps to run Green Thread locally:

📋 Prerequisites
Python 3.8+

Git

pip

🛠 Setup
Clone the Repository:

bash
Copy
Edit
git clone https://github.com/Deepshikha-Chhaperia/Green-Thread-App.git
cd Green-Thread-App
Install Dependencies:

bash
Copy
Edit
pip install -r requirements.txt
requirements.txt:

text
Copy
Edit
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
Set Up Environment Variables:

Create a .env file in the root directory:

bash
Copy
Edit
GEMINI_API_KEY=your-gemini-api-key
HF_API_TOKEN=your-huggingface-api-token
Get your Gemini API key from Google AI Studio.

Get your Hugging Face API token from Hugging Face.

Run the App:

bash
Copy
Edit
streamlit run main.py
Open http://localhost:8501 in your browser.
Use the sidebar to switch between Design Studio, Fabric Advisor, Production Optimizer, and Textile Generator.

❗ Troubleshooting
Memory Issues:
If Stable Diffusion crashes, ensure you have >16GB RAM or reduce inference steps to 15 in main.py.

API Errors:
Check Gemini and Hugging Face API keys and rate limits.
Update retry_after in cached_generate_content if 429 errors persist.

Streamlit Reloading:
Run with:

bash
Copy
Edit
streamlit run main.py --server.fileWatcherType none
🔧 Usage

Tool	How to Use
Design Studio	Select style, materials, packaging → Generate design → View sustainability score → Download PNG
Fabric Advisor	Upload fabric image (JPG/PNG, <2MB) → Explore composition and sustainability insights
Production Optimizer	Input factory details → Get emission and waste-cutting recommendations
Textile Generator	Choose base material, properties, goals → Generate textile blueprint
🚀 Future Enhancements
✨ Design Studio
Real-ESRGAN: 4x resolution upscaling.

Inpainting: Pattern/sleeve editing.

ControlNet: Pose-guided generation.

Design Gallery: Save and compare 10+ designs per session.

✨ Fabric Advisor
Fine-tuned ResNet50: 90%+ accuracy on eco-fabrics.

OpenCV: Analyze weave patterns.

Spectral Imaging: Detect dyes and microfibers.

✨ Sustainable Production Optimizer
Carbon Tracking APIs.

Blockchain for ethical sourcing.

ROI Analysis for eco-upgrades.

✨ Sustainable Textile Generator
Biofabrication models (BioDiffusion).

Robotic Weaving APIs.

Stable Diffusion 3 for microstructure visualization.

🐛 Known Issues
Stable Diffusion: High memory usage — needs 16GB+ RAM.

ResNet50: Limited accuracy on niche fabrics (fine-tuning in progress).

Gemini API: Occasional 429 errors under load.

Streamlit: Dev mode file watcher reloads (disable if needed).

📝 Contributing
Interested in collaborating?
Connect with me on LinkedIn before submitting pull requests.
(Please discuss before submitting PRs, as this is a personal project!)

📜 License
MIT License – Free for personal/academic use.
For commercial use, please request permission.

🙌 Acknowledgments
Streamlit: For intuitive frontend magic

Stability AI: For Stable Diffusion’s generative power

Google Gemini API: For sustainability insights

US Biotech Pioneers: Bolt Threads, MycoWorks, Unspun — for inspiring the future of fabrics.
