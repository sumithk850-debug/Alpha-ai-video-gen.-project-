import streamlit as st
from groq import Groq
import requests, base64, asyncio, json, urllib.parse, random, time

# 1. Config & Theme
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
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 50px;
        background-color: #1e1e1e; color: #00C9FF;
        border: 2px solid #00C9FF; font-weight: bold;
    }
    .lab-card {
        border: 1px solid #333; padding: 20px;
        border-radius: 15px; background: #161b22;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. State & Keys
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# 3. Login
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">⚡ ALPHA AI SYSTEM LOGIN</div>', unsafe_allow_html=True)
    pw = st.text_input("Master Key", type="password")
    if st.button("Enter"):
        if pw == "Hasith12378":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# 4. Stable Video Engine (Wan 2.1)
def generate_wan_video(prompt):
    """Wan 2.1 Stable Engine for Pollinations"""
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(0, 1000000)
    # ස්ථිරවම Wan මොඩල් එක පාවිච්චි කිරීම
    video_url = f"https://gen.pollinations.ai/video/{encoded}?model=wan&seed={seed}&key={POLLINATIONS_KEY}"
    
    with st.spinner("Alpha is directing Wan 2.1... (Wait ~20 seconds)"):
        # සර්වර් එකට වීඩියෝ එක රෙන්ඩර් කරන්න කාලය දීම
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.2) # තත්පර 20ක් පමණ
            progress_bar.progress(i + 1)
        
        # වීඩියෝ එක ඇත්තටම තියෙනවද කියලා චෙක් කරනවා
        try:
            check = requests.head(video_url, timeout=10)
            if check.status_code == 200 or check.status_code == 302:
                return video_url, None
            else:
                return None, "Video is still processing. Please try again."
        except:
            return video_url, None # Link එක වැඩ නම් පෙන්වන්න

# 5. UI Tabs
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)
tab_chat, tab_media = st.tabs(["💬 Advanced Chat", "🎬 Video & Image Lab"])

with tab_media:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="lab-card"><h4>🖼️ Art Studio</h4>', unsafe_allow_html=True)
        img_p = st.text_input("Describe Image")
        if st.button("Generate Image"):
            seed = random.randint(0, 9999)
            url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&key={POLLINATIONS_KEY}"
            st.image(url)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="lab-card"><h4>🎬 Wan 2.1 Video Engine</h4>', unsafe_allow_html=True)
        vid_p = st.text_input("Describe Video Scene (e.g., T-Rex hunt)")
        if st.button("Generate Wan Video"):
            if vid_p:
                v_url, err = generate_wan_video(vid_p)
                if v_url:
                    st.video(v_url)
                    st.write(f"[Direct Link]({v_url})")
                else: st.error(err)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if p := st.chat_input("Ask Alpha..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI created by Hasith."}] + st.session_state.messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            
            # Voice output
            voice_url = f"https://gen.pollinations.ai/audio/{urllib.parse.quote(full_res[:200])}?voice=nova&key={POLLINATIONS_KEY}"
            st.markdown(f'<audio autoplay src="{voice_url}">', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

st.caption("Alpha AI Project | Created by Hasith")
