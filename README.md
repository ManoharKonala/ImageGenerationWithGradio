# ✨ GenAI Studio

An advanced, serverless hybrid AI image generation dashboard built with **Gradio** and the **Hugging Face Inference API**. This project demonstrates how to orchestrate multiple state-of-the-art Generative AI models into a single, cohesive, premium interface without requiring high-end local GPUs.

![GenAI Studio Interface](.github/preview.png) *(Preview placeholder)*

## 🚀 Key Features

*   **Hybrid Inference Architecture**: Runs the lightweight UI server locally while securely offloading massive tensor calculations to Hugging Face's cloud A100 GPU clusters via REST API.
*   **State-of-the-Art Models (SOTA)**: Seamlessly switch between the best open-source image generation architectures:
    *   **`FLUX.1-schnell`**: Extremely fast and high-fidelity text-to-image.
    *   **`SDXL-Lightning`**: ByteDance's distilled rapid-prototyping model.
    *   **`Stable Diffusion 3.5 Large`**: Industry-leading prompt adherence and typography.
*   **✨ AI Prompt Co-Pilot**: Integrated with `Mistral-7B-Instruct`. Automatically intercepts simple user ideas and intelligently engineers them into highly detailed, 50-word cinematic prompts before generation.
*   **🪄 Aesthetic Style Vault**: One-click injection of curated aesthetic instructions (Cyberpunk, Studio Ghibli, Claymation, Cinematic Macro) directly into the generation pipeline.
*   **🎞️ Session Filmstrip**: Visual history queue that saves generated images, prompts, and model details during the active session.
*   **Dynamic Aspect Ratios**: Easily generate images tailored for Instagram (1:1), YouTube (16:9), or TikTok (9:16).

## 🛠️ Tech Stack

*   **Frontend**: Gradio (with custom CSS for a Glassmorphism dark-mode aesthetic)
*   **Backend Logic**: Python 3.x
*   **APIs**: `requests`, `huggingface_hub`
*   **Image Processing**: `Pillow` (PIL), `io`
*   **AI Models**: FLUX.1, SDXL, SD3.5, Mistral-7B

## 📦 Installation & Setup

Because this application relies on serverless inference, you do **not** need a local GPU to run it.

1. **Clone the repository** (or navigate to the project folder):
   ```bash
   cd genai_studio
   ```

2. **Set up a Python Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Get a Hugging Face Access Token**:
   * Create a free account at [huggingface.co](https://huggingface.co).
   * Go to **Settings > Access Tokens** and create a new **Write** or **Fine-Grained** token.

5. **Run the Studio**:
   Set your token as an environment variable and launch the app:
   ```bash
   # On macOS/Linux:
   export HF_TOKEN="your_hf_api_token"
   python app.py
   
   # On Windows (Command Prompt):
   set HF_TOKEN=your_hf_api_token
   python app.py
   
   # On Windows (PowerShell):
   $env:HF_TOKEN="your_hf_api_token"
   python app.py
   ```

6. **Open the Dashboard**:
   Navigate to `http://127.0.0.1:7860` in your web browser.

## 🧠 How the Architecture Works (Bypassing API Limits)

This project utilizes a direct manual connection to the `router.huggingface.co` API endpoint using Python's `requests` library. This architecture was explicitly chosen to bypass recent deprecations on the legacy `api-inference.huggingface.co` domain, ensuring robust and reliable access to the newest models like FLUX and Mistral without SDK lock-in.

The **AI Co-Pilot** feature utilizes asynchronous sequential routing:
1. User submits a short idea.
2. The Studio pauses and redirects the idea to an LLM (Mistral).
3. The LLM returns a strictly formatted 50-word engineered prompt.
4. The Studio intercepts the LLM output and forwards it to the Vision Model (e.g., FLUX).
5. The final high-resolution byte stream is piped directly into the Gradio UI.
