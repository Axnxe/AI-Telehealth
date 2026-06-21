import streamlit as st
from faker import Faker
import uuid

import os
from groq import Groq
from dotenv import load_dotenv

dotenv_loaded = load_dotenv(".env")

import os

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets")
    st.stop()

client = Groq(api_key=api_key)

st.set_page_config(page_title="Obas Lab AI", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background-color: #f6f8fb;
    }
    h1, h2, h3 {
        color: #1f2a44;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        font-size: 15px;
        font-weight: 600;
    }
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        .main {
            background-color: #0f172a;
            color: white;
        }
        .stTextArea textarea {
            border-radius: 12px;
        }
        .stButton button {
            border-radius: 10px;
            background-color: #2563eb;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 Obas Lab AI Clinical Workflow Assistant")
st.caption("SOAP note generation • Synthetic patients • No PHI stored")

# SESSION STATE
if "soap" not in st.session_state:
    st.session_state.soap = ""

if "patients" not in st.session_state:
    fake = Faker()
    st.session_state.patients = {
        str(uuid.uuid4()): {
            "name": fake.name(),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")
        }
        for _ in range(6)
    }

# SIDEBAR
st.sidebar.title("🧑‍⚕️ Patient Panel")

st.sidebar.markdown("### Active Patient")

patient_id = st.sidebar.selectbox(
    "Select Patient Record",
    options=list(st.session_state.patients.keys()),
    format_func=lambda x: st.session_state.patients[x]["name"]
)

patient = st.session_state.patients[patient_id]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**DOB:** {patient['dob']}")
st.sidebar.markdown("**Status:** 🟢 Active Visit")
st.sidebar.markdown("**Record Type:** Synthetic (No PHI)")

def generate_soap(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical documentation assistant. "
                    "Convert raw patient visit notes into a structured SOAP note. "
                    "Be clear, professional, and concise. "
                    "Do NOT invent medical conditions. Only reorganize provided info."
                )
            },
            {
                "role": "user",
                "content": f"""
Convert these notes into a SOAP note:

{text}

Format:

Subjective:
Objective:
Assessment:
Plan:
"""
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# TABS
tab1, tab2 = st.tabs([
    "📋 Clinical Documentation",
    "💊 Orders & Workflow"
])

# TAB 1
with tab1:
    st.subheader("Clinical Encounter Notes")

    transcript = st.text_area(
        "Enter or paste provider-patient interaction notes",
        height=220,
        placeholder="e.g. Patient presents with..."
    )

    col1, col2 = st.columns(2)

    with col1:
        generate = st.button("⚡ Generate SOAP Note")

    if generate:
        if transcript:
            st.toast("Processing clinical documentation...")

            with st.spinner("AI structuring SOAP note..."):
                st.session_state.soap = generate_soap(transcript)
        else:
            st.warning("No clinical notes detected")

    if st.session_state.soap:
        st.markdown("### 📄 Structured SOAP Output")

        st.text_area(
            "Review & Edit",
            value=st.session_state.soap,
            height=300
        )

        st.success("Ready for clinician review")

# TAB 2
with tab2:
    st.subheader("Medication & Workflow Orders")

    med = st.text_input("Enter medication / clinical action order")

    col1, col2 = st.columns(2)

    with col1:
        send = st.button("📤 Submit Order")

    if send:
        if med:
            st.success(f"Order logged for {patient['name']}")

            st.info("Simulated workflow only — no external systems connected")
        else:
            st.warning("Please enter an order before submitting")