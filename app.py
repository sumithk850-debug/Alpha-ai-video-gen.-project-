import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json
import edge_tts
from PIL import Image
import time
import urllib.parse
import random
from duckduckgo_search import DDGS 
from base64 import b64encode

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI PRO | Premium Intelligence", layout="wide", page_icon="⚡")

# --- GOOGLE VERIFICATION TAG ---
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session State Init
# -----------------------
# Main Chat Memory
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# Specialized Tool System Contexts
if "blender_mode" not in st.session_state: st.session_state.blender_mode=False
if "current_system_prompt" not in st.session_state: 
    st.session_state.current_system_prompt = "You are Alpha AI, a premium, intelligent digital assistant created by Hasith. You are helpful, precise, and professional."

# -----------------------
# 3. Custom UI Styling & Logo
# -----------------------

# Alpha Neon Logo (SVG)
logo_svg = """
<svg width="250" height="60" viewBox="0 0 250 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <path d="M15 45L30 15L45 45H15Z" stroke="#00f2fe" stroke-width="3" fill="none" filter="url(#neon-glow)"/>
  <path d="M22 38H38" stroke="#00f2fe" stroke-width="2" fill="none" filter="url(#neon-glow)"/>
  <text x="60" y="42" font-family="Segoe UI, sans-serif" font-size="28" font-weight="bold" fill="white" filter="url(#neon-glow)">ALPHA</text>
  <text x="165" y="42" font-family="Segoe UI, sans-serif" font-size="28" font-weight="bold" fill="#00f2fe" fill-opacity="0.8">AI PRO</text>
</svg>
"""
logo_b64 = b64encode(logo_svg.encode()).decode()

st.markdown(f"""
<style>
    /* Premium Black Page Background */
    .stApp {{
        background-color: #080a0c;
        color: #e6edf3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* Top Banner with Glassmorphism */
    .premium-banner {{
        width: 100%;
        padding: 15px 30px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }}

    .logo-container {{ display: flex; align-items: center; justify-content: center; }}
    .logo-container img {{ height: 50px; }}

    .header-text {{
        font-size: 14px;
        color: rgba(255,255,255,0.7);
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}

    /* Login Area */
    .login-container {{
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }}

    /* Chat Messages */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        transition: all 0.3s ease;
    }}
    .stChatMessage:hover {{
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0px 0px 10px rgba(0, 242, 254, 0.1);
    }}

    /* Round Neon Chat Input */
    .stChatInput div {{
        border-radius: 35px !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #010204;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }}

    /* Buttons with Neon Effect */
    div.stButton > button {{
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 12px;
        width: 100%;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.4s ease;
    }}
    div.stButton > button:hover {{
        box-shadow: 0px 0px 18px rgba(0, 242, 254, 0.8);
        transform: translateY(-2px);
    }}

    /* Specialized Tool Buttons in Sidebar */
    div.stButton > button.blender-active {{
        background: linear-gradient(45deg, #ff9800, #e65100);
        box-shadow: 0px 0px 15px rgba(255, 152, 0, 0.5);
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.04);
        border-radius: 12px 12px 0px 0px;
        color: white;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(0, 242, 254, 0.15) !important;
        border-bottom: 2px solid #00f2fe !important;
    }}

    /* Utility Boxes */
    .lab-box {{
        border: 1px solid rgba(255,255,255,0.08);
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.01);
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown(f"""
    <div class="login-container">
        <div class="logo-container"><img src="data:image/svg+xml;base64,{logo_b64}" alt="Alpha Logo"></div>
        <p style="color:#e6edf3; font-weight:bold; margin-top:20px; text-transform:uppercase;">Initialize Alpha Core System</p>
        <p style="color:rgba(255,255,255,0.5); font-size:12px;">Developed by Hasith | T.C.Z Projects</p>
    </div>
    """, unsafe_allow_html=True)
    
    name = st.text_input("Operator Name", placeholder="Hasith")
    password = st.text_input("Master Key", type="password", placeholder="••••••••")
    
    if st.button("Authorize Access"):
        # Replace "Hasith12378" with your desired password
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied: Invalid Master Key")
    st.stop()

# -----------------------
# 5. API Setup (Managed via Streamlit Secrets)
# -----------------------
# Make sure these keys are set in .streamlit/secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
POLLINATIONS_API_KEY = st.secrets.get("POLLINATIONS_API_KEY", "") # New API Key

# Validate Keys
if not GROQ_API_KEY or not POLLINATIONS_API_KEY:
    st.error("Missing critical API Keys. Please check system configuration.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
# OpenRouter can be added here if needed, Llama 3 via Groq is used below.

# -----------------------
# 6. Helper Functions & Tools
# -----------------------

# Function 1: Image Generation - UPDATED FOR NEW POLLINATIONS SYSTEM
def generate_image_pollinations(prompt):
    """Generates image using new Pollinations /gen/ endpoint with API key"""
    try:
        # 1. Base URL with 'gen' and encoded prompt
        encoded_prompt = urllib.parse.quote(prompt)
        # Using a fixed seed for quality stability, or random.randint(1, 1000)
        API_URL = f"https://image.pollinations.ai/gen/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"
        
        # 2. Add API Key in Headers
        headers = {
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
        }
        
        # 3. Make the request
        response = requests.get(API_URL, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.content # Returns image bytes
        else:
            # st.error(f"Pollinations Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        # st.error(f"Generation failed: {e}")
        return None

# Function 2: Voice Output (Text to Speech)
async def speak_alpha(text):
    try:
        # US SteffanNeural is a premium sounding male voice
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            # Clean HTML to inject audio
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# Function 3: Web Search
def web_search_tool(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                context = "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
                return context
    except: return ""
    return ""

# Function 4: specialized Blender Assistant Activiator
def activate_blender_tool():
    """Sets the system prompt to a specialized Blender Scripter profile"""
    st.session_state.blender_mode = not st.session_state.blender_mode
    if st.session_state.blender_mode:
        st.session_state.current_system_prompt = """You are Alpha AI: Blender Scripting Expert.
You specialize only in Blender 3D Python API (bpy). 
You write precise, efficient, and well-commented Python scripts for Blender. 
You can explain how to handle objects, materials, textures, rendering, and geometry nodes via code.
If a user asks something unrelated to Blender or Python, politely remind them you are currently in Blender Assistant mode."""
        st.session_state.messages = [] # Optional: Clear chat for new context
    else:
        st.session_state.current_system_prompt = "You are Alpha AI, a premium digital assistant created by Hasith."
        st.session_state.messages = []

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.markdown(f'<div class="logo-container" style="margin-bottom:20px;"><img src="data:image/svg+xml;base64,{logo_b64}" alt="Alpha Logo"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-text" style="text-align:center; color:#e6edf3;">Operator: {st.session_state.user_full_name}</div>', unsafe_allow_html=True)
    st.divider()
    
    # Mode Selection
    mode = st.radio("Intelligence Level", ["Llama 3.3 70B (Fast)", "DeepSeek R1 (Advanced)"], index=0)
    web_search_on = st.checkbox("Web Search (Real-time)", value=False)
    voice_on = st.checkbox("Voice Output", value=True)
    
    st.divider()
    
    # SPECIALIZED TOOLS SECTION
    st.subheader("🛠️ Specialized Tools")
    
    # 1. Blender Scripting Assistant
    blender_btn_label = "Blender Assistant (ACTIVE)" if st.session_state.blender_mode else "Activate Blender Assistant"
    # Dynamic CSS class based on state
    css_class = "blender-active" if st.session_state.blender_mode else ""
    
    # Streamlit buttons don't support dynamic CSS classes easily, 
    # but we can use st.markdown with a custom unsafe container if needed.
    # For now, we use a simple button and change label.
    if st.button(blender_btn_label, key="blender_tool"):
        activate_blender_tool()
        st.rerun()

    if st.session_state.blender_mode:
        st.info("Alpha is now optimized for Blender Python API.")

    st.divider()
    
    # User Control
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Alpha AI PRO v2.1 | Created by Hasith")
    # Link to YouTube or project page
    st.markdown("[T.C.Z YouTube Channel](https://youtube.com/@tcz)", unsafe_allow_html=True)

# -----------------------
# 8. Main UI Layout
# -----------------------

# Main Banner
st.markdown(f"""
<div class="premium-banner">
    <div class="logo-container">
        <img src="data:image/svg+xml;base64,{logo_b64}" alt="Alpha Logo">
    </div>
    <div class="header-text">ULITMATE INTELLIGENCE | {mode}</div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_chat, tab_lab = st.tabs(["💬 Core Chat Intelligence", "🧪 Multimodal Lab (Alpha Gen)"])

# -----------------------
# TAB 1: Core Chat
# -----------------------
with tab_chat:
    # Handle Blender Mode Notification
    if st.session_state.blender_mode:
        st.warning("⚠️ ATTENTION: Alpha is currently operating under specialized 'Blender Scripting' context. Answers are optimized for Blender Python API.")

    # Display Chat Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    placeholder_text = "Ask Alpha Blender questions..." if st.session_state.blender_mode else "Awaiting operator input..."
    if prompt := st.chat_input(placeholder_text):
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. AI Response Generation
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""
            
            # 2a. Handle Web Search (If enabled and not in Blender mode)
            context = ""
            if web_search_on and not st.session_state.blender_mode:
                with st.spinner("Searching Intelligence Grid..."):
                    context = web_search_tool(prompt)
                    if context:
                        prompt_with_context = f"Context from Web:\n{context}\n\nUser Question: {prompt}"
                    else:
                        prompt_with_context = prompt
            else:
                prompt_with_context = prompt

            # 2b. Prepare Messages payload
            messages_payload = [{"role": "system", "content": st.session_state.current_system_prompt}]
            # Add past chat history for context (optional, can limit to last X messages)
            for m in st.session_state.messages[-5:]:
                messages_payload.append({"role": m["role"], "content": m["content"]})
            # Current prompt with context
            messages_payload[-1]["content"] = prompt_with_context

            # 2c. Determine Model
            model_name = "llama-3.3-70b-versatile" if "Llama 3.3" in mode else "deepseek-r1-distill-llama-70b"

            # 2d. Stream Response from Groq
            try:
                stream = groq_client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=0.4,
                    stream=True
                )
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
            except Exception as e:
                full_response = "An error occurred in Neural Core."
                st.error(f"Error: {e}")

            # 3. Add Assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # 4. Handle Voice Output
            if voice_on:
                asyncio.run(speak_alpha(full_response))

# -----------------------
# TAB 2: Multimodal Lab
# -----------------------
with tab_lab:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.markdown("### 🎨 Alpha Image Generation Lab")
    st.markdown(f'<p style="color:rgba(255,255,255,0.6); font-size:12px;">Powered by New Pollinations.ai "Gen" System (Key Active)</p>', unsafe_allow_html=True)
    
    # Prompt Input
    img_prompt = st.text_area("Describe your visual vision...", placeholder="A futuristic Transformer robot standing in a neon-lit cyberpunk city, photorealistic, 8k...")
    
    # Model/Style Aspect Ratio
    col_ratio, col_style = st.columns(2)
    # Pollinations usually handles ratio via prompt or dimensions, using prompt approach.
    img_style = col_style.selectbox("Style Preset", ["Photorealistic", "Digital Art", "Anime/Manga", "Oil Painting", "Conceptual Art"])

    st.markdown("---")
    
    # Generate Button
    if st.button("Initialize Visual Synthesis"):
        if not img_prompt:
            st.error("Please provide a prompt for visual synthesis.")
        else:
            with st.spinner("Synthesizing imagery via Pollinations Gen Core..."):
                # Enhancing prompt with style
                final_prompt = f"{img_prompt}, {img_style} style, high quality, detailed, {col_ratio} aspect ratio"
                
                # Call NEW function
                img_bytes = generate_image_pollinations(img_prompt)
                
                if img_bytes:
                    # Display Image
                    image = Image.open(io.BytesIO(img_bytes))
                    st.image(image, caption=f"Synthesized Visual: {img_prompt}", use_column_width=True)
                    
                    # Download Button
                    st.download_button(
                        label="Save Visual to Grid",
                        data=img_bytes,
                        file_name=f"alpha_gen_{random.randint(1000,9999)}.png",
                        mime="image/png"
                    )
                else:
                    st.error("Visual synthesis failed. Critical error in Pollinations connection.")
    st.markdown('</div>', unsafe_allow_html=True)
