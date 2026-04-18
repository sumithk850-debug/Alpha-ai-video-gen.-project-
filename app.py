import streamlit as st
import requests
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# 1. PDF එකකින් අකුරු ලබා ගැනීම
def extract_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 2. නිල Google Search API
def google_search_official(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'q': query, 'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'num': 3}
    try:
        response = requests.get(url, params=params)
        results = response.json()
        search_text = "\nGoogle සෙවුම් ප්‍රතිඵල:\n"
        for item in results.get('items', []):
            search_text += f"- {item['title']}: {item['snippet']}\n"
        return search_text
    except: return ""

# 3. Groq හරහා පිළිතුරු ලබා ගැනීම
def get_groq_response(prompt, context=""):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    full_content = f"සන්දර්භය (Context): {context}\n\nප්‍රශ්නය: {prompt}\n\nකරුණාකර සිංහලෙන් පිළිතුරු දෙන්න."
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are Alpha AI, a professional assistant created by Hasith."},
            {"role": "user", "content": full_content}
        ],
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

# --- UI SETUP ---
st.set_page_config(page_title="Alpha AI", page_icon="🤖", layout="wide")

# ලස්සන Sidebar එක
with st.sidebar:
    st.markdown("<h1 style='color: #60a5fa;'>🤖 Alpha AI</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712038.png", width=80)
    st.divider()
    
    st.subheader("📁 දැනුම බැංකුව (PDF)")
    uploaded_file = st.file_uploader("ඔබේ PDF එක මෙතනට දාන්න", type="pdf")
    
    pdf_context = ""
    if uploaded_file:
        with st.spinner("PDF එක කියවමින්..."):
            pdf_context = extract_pdf_text(uploaded_file)
            st.success("PDF එක මතකයට ගත්තා!")
            
    st.divider()
    enable_google = st.toggle("Google Search සක්‍රීය කරන්න", value=True)
    st.caption(f"Created by Hasith")

# --- MAIN CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

if prompt := st.chat_input("මොනවාද දැනගන්න ඕනේ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Alpha AI තොරතුරු සොයමින්..."):
            
            # Google සෙවුම (අවශ්‍ය නම් පමණක්)
            search_context = ""
            if enable_google and any(word in prompt.lower() for word in ["price", "today", "news", "weather", "මිල", "අද", "දැන්"]):
                search_context = google_search_official(prompt)
            
            # සියලුම දත්ත එකතු කිරීම (PDF + Google)
            combined_context = f"{pdf_context}\n{search_context}"
            
            response = get_groq_response(prompt, combined_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
