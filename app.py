import streamlit as st
from faker import Faker
import uuid

import os
from groq import Groq
from dotenv import load_dotenv

dotenv_loaded = load_dotenv(".env")

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

st.set_page_config(page_title="Obas Lab AI", layout="wide")

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
st.sidebar.header("👤 Fake Patients")

patient_id = st.sidebar.selectbox(
    "Select Patient",
    options=list(st.session_state.patients.keys()),
    format_func=lambda x: st.session_state.patients[x]["name"]
)

patient = st.session_state.patients[patient_id]

st.sidebar.write("DOB:", patient["dob"])

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
tab1, tab2 = st.tabs(["📋 SOAP Charting", "💊 Medication Log"])

# TAB 1
with tab1:
    st.subheader("Live Visit Notes")

    transcript = st.text_area("Type notes here", height=250)

    if st.button("Generate SOAP Note"):
        if transcript:
            st.toast("Generating SOAP note... 🧠")

            with st.spinner("AI is analyzing clinical notes..."):
                st.session_state.soap = generate_soap(transcript)

        else:
            st.warning("Add notes first")

if st.session_state.soap:
    st.subheader("Generated SOAP Note")

    st.text_area(
        "Review before use",
        value=st.session_state.soap,
        height=350
    )

    st.success("SOAP note ready for clinician review")    

    st.text_area(
        "Review before use",
        value=st.session_state.soap,
        height=350
    )

    st.success("SOAP note ready for clinician review")

# TAB 2
with tab2:

    st.subheader("Medication Workflow Simulation")

    med = st.text_input("Medication / Follow-up Action")

    if st.button("Send Workflow"):

        if med:

            st.success(f"Workflow prepared for {patient['name']}")

            st.info("Simulation only — no patient data stored or transmitted.")

        else:

            st.warning("Enter medication workflow details first")