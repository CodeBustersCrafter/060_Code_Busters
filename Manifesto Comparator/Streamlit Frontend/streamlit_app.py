import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import time

# Load environment variables from .env file
load_dotenv()

# Constants for different API endpoints
MANIFESTO_API_URL = os.getenv("COMPARATOR_URL", "http://127.0.0.1:8000/compare")
WIN_PREDICTOR_API_URL = os.getenv("WIN_PREDICTOR_URL", "http://127.0.0.1:8000/win_predictor")
CHATBOT_API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000/generate")

def generate_manifesto_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt
    }
    try:
        response = requests.post(CHATBOT_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json().get("response", "No response found.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def fetch_win_predictor_data():
    try:
        response = requests.get(WIN_PREDICTOR_API_URL)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return {}

def compare_manifestos(candidate1, candidate2):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "candidate1": candidate1,
        "candidate2": candidate2
    }
    try:
        response = requests.post(MANIFESTO_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json().get("comparison", "No comparison found.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def election_chatbot():
    st.header("🤖 Election Chat Bot")
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    def send_message():
        user_input = st.session_state["user_input"]
        if user_input:
            st.session_state.messages.append({"type": "user", "text": user_input})
            with st.spinner("Generating response..."):
                progress_placeholder = st.empty()
                progress_bar = progress_placeholder.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                response = generate_manifesto_response(user_input)
                progress_placeholder.empty()
            st.session_state.messages.append({"type": "bot", "text": response})
            st.session_state["user_input"] = ""

    st.text_input("You:", key="user_input", on_change=send_message)

    for msg in st.session_state.messages:
        if msg["type"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**Chat Bot:** {msg['text']}")

def win_predictor():
    st.header("📈 Win Predictor")
    data = fetch_win_predictor_data()
    
    if data:
        df = pd.DataFrame(data)
        st.write("### Election Predictions")
        st.dataframe(df)

        st.write("### Prediction Graphs")
        st.line_chart(df.set_index('Date'))
    else:
        st.info("No data available to display.")

def manifesto_comparator():
    st.header("📄 Election Manifesto Comparator")
    
    candidates = [
        "Ranil Wickremesinghe",
        "Sajith Premadasa",
        "Anura Kumara Dissanayake",
        "Namal Rajapaksa",
        "Dilith Jayaweera"
    ]

    col1, col2 = st.columns(2)

    with col1:
        candidate1 = st.selectbox("Select first candidate:", candidates, key="candidate1")
        st.write(f"Manifesto for {candidate1}")

    with col2:
        candidate2 = st.selectbox("Select second candidate:", candidates, key="candidate2")
        st.write(f"Manifesto for {candidate2}")

    if st.button("💡 Compare Manifestos"):
        if candidate1 == candidate2:
            st.warning("Please select two different candidates.")
        else:
            with st.spinner("Generating comparison..."):
                progress_placeholder = st.empty()
                progress_bar = progress_placeholder.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                response = compare_manifestos(candidate1, candidate2)
                progress_placeholder.empty()
                st.success("**Comparison:**")
                st.write(response)

def main():
    st.set_page_config(page_title="Election RAG Assistant", layout="wide")
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Section",
        ["Manifesto Comparator", "Win Predictor", "Election Chat Bot"]
    )

    st.title("🗳️ Election RAG Assistant")
    st.write("Navigate through the sidebar to use different features of the application.")

    if app_mode == "Manifesto Comparator":
        manifesto_comparator()
    elif app_mode == "Win Predictor":
        win_predictor()
    elif app_mode == "Election Chat Bot":
        election_chatbot()

if __name__ == "__main__":
    main()