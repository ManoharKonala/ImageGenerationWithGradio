import gradio as gr
import os
import io
import random
import requests
from PIL import Image

# ─── Authentication ──────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "")

# ─── Data & Config ───────────────────────────────────────────────
MODELS = {
    "🚀 FLUX.1-schnell (Fastest & Best)": "black-forest-labs/FLUX.1-schnell",
    "⚡ SDXL-Lightning (Fast Prototyping)": "ByteDance/SDXL-Lightning",
    "🎨 Stable Diffusion 3.5 Large (Heavy)": "stabilityai/stable-diffusion-3.5-large"
}

ASPECT_RATIOS = {
    "Square 1:1 (Instagram)": (1024, 1024),
    "Landscape 16:9 (YouTube)": (1280, 720),
    "Portrait 9:16 (TikTok)": (720, 1280)
}

STYLES = {
    "🚫 No Style": "",
    "🎬 Cinematic Macro": "cinematic lighting, macro photography, highly detailed, depth of field, 8k resolution, photorealistic",
    "🤖 Cyberpunk Core": "cyberpunk aesthetic, neon lighting, highly detailed, gritty, glowing elements, 8k, masterpiece",
    "🏮 Ghibli Magic": "Studio Ghibli style, Hayao Miyazaki, anime art, cel shaded, highly detailed background, vibrant colors, magical",
    "🧱 Claymation": "claymation style, Aardman animations, plasticine figure, incredibly detailed, studio lighting, craft"
}

RANDOM_PROMPTS = [
    "A bioluminescent cyberpunk city in the rain at night, neon lights reflecting on wet pavement, cinematic lighting, 8k resolution, photorealistic.",
    "A cozy wooden cabin deep in a snowy pine forest, warm golden light glowing from the windows, starry night sky, hyperdetailed.",
    "A futuristic astronaut holding a glowing blue energy crystal on the surface of Mars, dramatic lighting, highly detailed spacesuit.",
    "A magical fantasy library floating in the clouds, bookshelves extending infinitely into the sky, glowing books, ethereal atmosphere.",
    "A hyper-realistic close-up portrait of a fierce cybernetic samurai woman, glowing red eyes, intricate armor details, cinematic bokeh."
]

# ─── Inference Logic ─────────────────────────────────────────────
def enhance_prompt(prompt, hf_token):
    try:
        sys_prompt = "You are an expert image prompt engineer. User gives an idea, you reply ONLY with a highly detailed, descriptive image generation prompt (max 50 words). No intro, no quotes."
        full_text = f"<s>[INST] {sys_prompt}\n\nIdea: {prompt} \n\nPrompt: [/INST]"
        
        url = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": full_text,
            "parameters": {"max_new_tokens": 100}
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            return prompt, f"Co-pilot API Error: {response.text}"
            
        result = response.json()
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            # Mistral commonly includes the prompt in the output, let's just extract the newly generated part if so,
            # or for text generation API it sometimes just appends or returns the whole thing.
            gen_text = result[0]["generated_text"]
            if "[/INST]" in gen_text:
                gen_text = gen_text.split("[/INST]")[-1].strip()
            return gen_text.strip(' "\\n'), None
        return prompt, "Co-pilot format error."
    except Exception as e:
        print(f"Co-Pilot Error: {e}")
        return prompt, f"Co-pilot error: {str(e)}"

def generate_image(prompt, model_name, ratio_name, style_name, use_magic):
    if not HF_TOKEN:
        raise gr.Error("No HF_TOKEN found. Please pass it as an environment variable.")
        
    # Extract settings
    model_id = MODELS[model_name]
    width, height = ASPECT_RATIOS[ratio_name]
    
    final_prompt = prompt
    status_msg = f"Generating with {model_name}..."
    
    # Magic Prompt Co-Pilot
    if use_magic:
        enhanced, p_err = enhance_prompt(prompt, HF_TOKEN)
        if not p_err:
            final_prompt = enhanced
            status_msg = f"✨ Co-Pilot Enhanced: {final_prompt}\n\nGenerating with {model_name}..."
        else:
            print(p_err)
            
    # Aesthetic Injection
    if STYLES[style_name]:
        final_prompt = f"{final_prompt}, {STYLES[style_name]}"
        
    try:
        url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": final_prompt,
            "parameters": {
                "width": width,
                "height": height
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image, final_prompt, status_msg
        elif response.status_code in [503, 504]:
            raise gr.Error("The model is currently loading into Hugging Face's server cache. Please try again in 1-2 minutes.")
        else:
            raise gr.Error(f"API Error [{response.status_code}]: {response.text}")
            
    except Exception as e:
        raise gr.Error(f"Unexpected Error: {str(e)}")

def surprise_me():
    return random.choice(RANDOM_PROMPTS)

# ─── Gradio UI ───────────────────────────────────────────────────
custom_css = """
.gradio-container {
    background: radial-gradient(circle at 10% 10%, #0d1117 0%, #010409 100%);
    color: #c9d1d9;
    font-family: 'Inter', sans-serif;
}
h1 {
    background: linear-gradient(90deg, #ff7eb3, #ff758c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    text-align: center;
}
.glass-box {
    background: rgba(22, 27, 34, 0.6) !important;
    border: 1px solid rgba(240, 246, 252, 0.1) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
}
.primary-btn {
    background: linear-gradient(90deg, #ff7eb3, #ff758c) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
}
"""

with gr.Blocks(css=custom_css, title="GenAI Studio") as demo:
    gr.Markdown("# ✨ GEN-AI STUDIO")
    gr.Markdown("<p style='text-align: center; color: #8b949e; font-size: 1.1rem;'>Serverless Hybrid Inference Dashboard</p>")
    
    if not HF_TOKEN:
        gr.Warning("⚠️ A Hugging Face Token is required to use the Studio. Please set your HF_TOKEN environment variable.")
    
    with gr.Row():
        # Left Column - Inputs
        with gr.Column(scale=1):
            with gr.Group(elem_classes="glass-box"):
                gr.Markdown("### 🎨 Creation Studio")
                
                with gr.Row():
                    gr.Markdown("**1. What do you want to see?**")
                    surprise_btn = gr.Button("🎲 Surprise Me", size="sm")
                    
                prompt_input = gr.Textbox(
                    placeholder="Describe your masterpiece...",
                    lines=4,
                    show_label=False
                )
                
                surprise_btn.click(fn=surprise_me, outputs=prompt_input)
                
                gr.Markdown("### ⚙️ Engine Settings")
                model_dropdown = gr.Dropdown(
                    choices=list(MODELS.keys()),
                    value=list(MODELS.keys())[0],
                    label="AI Architecture"
                )
                
                ratio_dropdown = gr.Dropdown(
                    choices=list(ASPECT_RATIOS.keys()),
                    value=list(ASPECT_RATIOS.keys())[0],
                    label="Aspect Ratio"
                )
                
                gr.Markdown("### 🪄 Unique Features")
                style_dropdown = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value=list(STYLES.keys())[0],
                    label="Aesthetic Style Vault"
                )
                
                magic_checkbox = gr.Checkbox(
                    label="✨ AI Prompt Co-Pilot",
                    info="Uses Mistral-7B to intelligently expand your simple idea into a highly-detailed prompt.",
                    value=False
                )
                
                generate_btn = gr.Button("🚀 Render High-Fidelity Image", variant="primary", elem_classes="primary-btn")
                
        # Right Column - Outputs
        with gr.Column(scale=1.5):
            with gr.Group(elem_classes="glass-box"):
                gr.Markdown("### 🖼️ Output Gallery")
                
                output_image = gr.Image(
                    label="Generated Image",
                    type="pil",
                    format="png"
                )
                
                status_text = gr.Markdown("Ready to generate...", visible=True)
                
                generate_btn.click(
                    fn=generate_image,
                    inputs=[prompt_input, model_dropdown, ratio_dropdown, style_dropdown, magic_checkbox],
                    outputs=[output_image, prompt_input, status_text]
                )
                
                gr.Markdown("---")
                gr.Markdown("<span style='color: #ff7eb3;'>💡 **Hardware Status**: App running locally. Tensor math offloaded to Hugging Face A100 GPU clusters via secure REST API.</span>")

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
