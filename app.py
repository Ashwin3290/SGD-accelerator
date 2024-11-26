import streamlit as st
import gan.gan_app as gan
import gen_ai.gen_ai_app as genai

st.set_page_config(
    page_title="Test data management system",
    layout="wide"
)
st.title("Test data management system")
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #7dd3fc;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Radio Buttons */
    .stRadio {
        padding-top: 40px;
        margin-bottom: 20px;
    }
    .stRadio > label {
        font-weight: 600;
        color: #7dd3fc;
    }
    .stRadio > div {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .stRadio > div > div {
        margin: 10px 0;
        color: #94a3b8;
    }
    .stRadio > div:hover {
        background-color: #2d3748;
        transition: all 0.3s ease;
    }
    
    /* Dropdowns/Selectbox */
    .stSelectbox {
        margin: 15px 0;
    }
    .stSelectbox > label {
        color: #7dd3fc;
        font-weight: 500;
    }
    .stSelectbox > div > div {
        background-color: #1e293b;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stSelectbox > div > div:hover {
        border-color: #7dd3fc;
    }
    
    /* Text Inputs */
    .stTextInput > label {
        color: #7dd3fc;
        font-weight: 500;
    }
    .stTextInput > div > div {
        background-color: #1e293b;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stTextInput > div > div:hover {
        border-color: #7dd3fc;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1e293b;
        color: #7dd3fc;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #2d3748;
        border-color: #7dd3fc;
        color: #7dd3fc;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1e293b !important;
        border-radius: 8px;
    }
            
    </style>
""", unsafe_allow_html=True)


option = st.sidebar.selectbox(
    "Choose Generation Method", 
    ["GAN based generation", "Gen-ai based generation"]
)

if option == "GAN based generation":
    gan.render()
elif option == "Gen-ai based generation":
    genai.render()