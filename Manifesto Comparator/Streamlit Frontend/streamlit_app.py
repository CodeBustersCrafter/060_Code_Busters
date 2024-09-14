import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000/generate")

def generate_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt
    }
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json().get("response", "No response found.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def main():
    st.set_page_config(page_title="Election RAG Assistant", layout="centered")
    st.title("🗳️ Election RAG Assistant")
    st.write("Enter a prompt related to the election data, and receive insightful responses powered by AI.")

    prompt = st.text_area("🔍 Enter your prompt:", height=150)

    if st.button("💡 Generate Response"):
        if prompt.strip() == "":
            st.warning("Please enter a valid prompt.")
        else:
            with st.spinner("Generating response..."):
                response = generate_response(prompt)
                st.success("**Response:**")
                st.write(response)

if __name__ == "__main__":
    main()