import streamlit as st
import requests
import json

# --- CONFIGURATION (Secrets) ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

# --- API FUNCTIONS ---
def get_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are Alpha AI, a sophisticated, professional, and helpful assistant created by Hasith."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5 # වඩාත් නිවැරදි පිළිතුරු සඳහා අඩු කළා
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "කණගාටුයි, Groq සම්බන්ධතාවයේ දෝෂයක් පවතී."

def search_google(query):
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    data = json.dumps({"q": query})
    try:
        response = requests.post(url, headers=headers, data=data)
        results = response.json()
        search_text = "සජීවී සෙවුම් ප්‍රතිඵල (Google Search):\n"
        for result in results.get('organic', [])[:3]:
            search_text += f"- {result['title']}: {result['snippet']}\n"
        return search_text
    except:
        return ""

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Alpha AI", page_icon="🤖", layout="wide")

# Custom CSS for modern look
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Input Box */
    .stChatInputContainer {
        border-radius: 20px;
        border: 1px solid #334155;
        background-color: #1e293b;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .stSidebar h1 {
        color: #60a5fa;
        font-size: 24px;
        font-weight: 700;
    }

    /* Chat Messages */
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 15px;
        padding: 15px;
        max-width: 80%;
    }
    .stChatMessage.user {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        align-self: flex-end;
    }
    .stChatMessage.assistant {
        background-color: #1f2937;
        color: #e2e8f0;
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1>🤖 Alpha AI Panel</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712038.png", width=100)
    st.divider()
    
    st.markdown("### System Status")
    st.success("Core: Online")
    st.info("Groq API: Connected")
    st.warning("Google Search: Available")
    
    st.divider()
    st.markdown("### Control Center")
    enable_google = st.toggle("Enable Live Google Search", value=True)
    
    st.divider()
    st.caption(f"© 2024 Alpha AI by Hasith")

# --- MAIN CHAT INTERFACE ---
st.markdown("<h2 style='text-align: center; color: #60a5fa;'>Alpha AI Dashboard</h2>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages with a container
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("මොනවාද අද දැනගන්න ඕනේ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Alpha AI තොරතුරු සොයමින්..."):
            
            # පියවර 1: ගූගල් සෙවුම සක්‍රීය නම් පමණක් සෙවීම
            search_context = ""
            if enable_google:
                keywords = ["price", "today", "news", "weather", "මිල", "අද", "දැන්", "මොනවාද", "කවුද"]
                if any(word in prompt.lower() for word in keywords):
                    st.write("🔍 සජීවී දත්ත පරීක්ෂා කරමින්...")
                    search_context = search_google(prompt)
            
            # පියවර 2: Groq හරහා පිළිතුර සැකසීම
            final_prompt = f"සන්දර්භය (Context): {search_context}\n\nප්‍රශ්නය: {prompt}\n\nකරුණාකර සිංහලෙන් පිළිතුරු දෙන්න."
            response = get_groq_response(final_prompt)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
