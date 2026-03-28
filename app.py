import streamlit as st
from groq import Groq
import requests, base64, asyncio, json, urllib.parse, random

# -----------------------
# 1. Page Config & Style
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .premium-banner { 
        width:100%; padding:20px; 
        background: linear-gradient(90deg, #00C9FF, #92FE9D); 
        color:#000; border-radius:15px; 
        text-align:center; font-weight:bold; 
        margin-bottom:25px; font-size: 24px;
        box-shadow: 0px 4px 15px rgba(0,201,255,0.3);
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 50px;
        background-color: #1e1e1e; color: #00C9FF;
        border: 2px solid #00C9FF; font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00C9FF; color: #000; }
    .lab-card {
        border: 1px solid #333; padding: 20px;
        border-radius: 15px; background: #161b22;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 2. Session State & Keys
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# Secrets (Make sure these are in your Streamlit Cloud Secrets)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY") # Get from enter.pollinations.ai

client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 3. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">⚡ ALPHA AI CORE ACCESS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pw = st.text_input("Master Key", type="password")
        if st.button("Initialize System"):
            if pw == "Hasith12378":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied!")
    st.stop()

# -----------------------
# 4. Core Functions (Pollinations & Groq)
# -----------------------

def get_pollinations_video(prompt):
    """Generate MP4 Video using Pollinations API"""
    encoded = urllib.parse.quote(prompt)
    # Based on your documentation: GET /video/{prompt}
    url = f"https://gen.pollinations.ai/video/{encoded}?key={POLLINATIONS_KEY}"
    return url

def get_pollinations_audio(text):
    """Text to Speech using Pollinations Audio API"""
    encoded = urllib.parse.quote(text)
    # Based on your documentation: GET /audio/{text}
    url = f"https://gen.pollinations.ai/audio/{encoded}?voice=nova&key={POLLINATIONS_KEY}"
    return url

# -----------------------
# 5. UI Layout
# -----------------------
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

tab_chat, tab_media = st.tabs(["💬 Advanced Chat", "🎬 Media Generation Lab"])

with tab_media:
    col_img, col_vid = st.columns(2)
    
    with col_img:
        st.markdown('<div class="lab-card"><h4>🖼️ Image Engine</h4>', unsafe_allow_html=True)
        img_p = st.text_input("Image Description", placeholder="e.g. A futuristic Sri Lanka")
        if st.button("Generate Image"):
            if img_p:
                seed = random.randint(0, 99999)
                img_url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&key={POLLINATIONS_KEY}"
                st.image(img_url, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vid:
        st.markdown('<div class="lab-card"><h4>🎬 Video Engine (MP4)</h4>', unsafe_allow_html=True)
        vid_p = st.text_input("Video Description", placeholder="e.g. T-Rex fighting Spinosaurus")
        if st.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is rendering video..."):
                    v_url = get_pollinations_video(vid_p)
                    st.video(v_url)
                    st.write(f"[Download MP4]({v_url})")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_chat:
    # Sidebar for Model Selection
    with st.sidebar:
        st.title("Alpha Settings")
        model_choice = st.selectbox("Brain Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
        voice_on = st.checkbox("Voice Response", value=True)
        if st.button("Clear Memory"):
            st.session_state.messages = []
            st.rerun()

    # Chat Interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Command me, Master..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            res_box = st.empty()
            full_res = ""
            
            # System Instruction
            sys_prompt = "You are Alpha AI, a genius assistant created by Hasith from Sri Lanka. You are helpful and witty."
            
            stream = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            
            # Voice Output
            if voice_on:
                audio_url = get_pollinations_audio(full_res[:200]) # Limit to 200 chars for speed
                st.markdown(f'<audio autoplay src="{audio_url}">', unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})

st.markdown("---")
st.caption("Alpha AI Ultimate | Developed by Hasith | Bandarawela Central College")
