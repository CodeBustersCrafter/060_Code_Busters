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

def generate_manifesto_response(prompt, language):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "language": language
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

def compare_manifestos(candidates):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "candidates": candidates
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
    
    # Add language selection
    language = st.selectbox(
        "Select Language",
        options=["English", "Sinhala", "Tamil"],
        index=0,
        help="Choose the language for interacting with the chatbot."
    )
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    def send_message():
        user_input = st.session_state["user_input"]
        if user_input:
            st.session_state.messages.append({"type": "user", "text": user_input, "language": language})
            with st.spinner("Generating response..."):
                progress_placeholder = st.empty()
                progress_bar = progress_placeholder.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                response = generate_manifesto_response(user_input, language)
                progress_placeholder.empty()
            st.session_state.messages.append({"type": "bot", "text": response, "language": language})
            st.session_state["user_input"] = ""

    st.text_input("You:", key="user_input", on_change=send_message)

    for msg in st.session_state.messages:
        if msg["type"] == "user":
            st.markdown(f"**You:** {msg['text']} ({msg['language']})")
        else:
            st.markdown(f"**Chat Bot:** {msg['text']} ({msg['language']})")

# Global predicted data
data = None

def win_predictor():
    global data
    st.header("📈 Win Predictor")
    if data is None:
        data = fetch_win_predictor_data()
    temp = data.split("```")
    description = temp[0]
    data = temp[1]
    description = description.replace("`","")
    st.write(description)
    if data:
        import json
        
        try:
            # Convert the string data to JSON
            data = json.loads(data)
            
            # Now json_data is a Python dictionary
            st.success("Data successfully loaded and parsed.")
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON data: {e}")
            return
        for key, value in data.items():
            if value['type'] == "bar":
                st.subheader(key)
                df = pd.DataFrame(value["data"])
                st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])
            elif value['type'] == "line":
                st.subheader(key)
                df = pd.DataFrame(value["data"])
                df = df.set_index(df.columns[0])
                st.line_chart(df)
            elif value['type'] == "pie":
                st.subheader(key)
                df = pd.DataFrame(value["data"])
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                st.pyplot(fig)
            elif value['type'] == "bar_demographic":
                st.subheader(key)
                df = pd.DataFrame(value["data"])
                df = df.set_index(df.columns[0])
                st.bar_chart(df)
            elif value['type'] == "stacked_bar":
                st.subheader(key)
                df = pd.DataFrame(value["data"])
                df = df.set_index(df.columns[0])
                st.bar_chart(df)
            elif value['type'] == "map":
                st.subheader(key)
                import pydeck as pdk

                # Sample Data
                df = pd.DataFrame(value["data"])

                from urllib.error import URLError

                @st.cache_data
                def load_province_data():
                    # Hardcoded province data for Sri Lanka
                    provinces = [
                        {"name": "Western", "latitude": 6.9271, "longitude": 79.8612},
                        {"name": "Central", "latitude": 7.2906, "longitude": 80.6337},
                        {"name": "Southern", "latitude": 6.0535, "longitude": 80.2210},
                        {"name": "Northern", "latitude": 9.0765, "longitude": 80.2586},
                        {"name": "Eastern", "latitude": 7.7941, "longitude": 81.5790},
                        {"name": "North Western", "latitude": 7.7573, "longitude": 80.1887},
                        {"name": "North Central", "latitude": 8.3114, "longitude": 80.4037},
                        {"name": "Uva", "latitude": 6.8791, "longitude": 81.3359},
                        {"name": "Sabaragamuwa", "latitude": 6.7056, "longitude": 80.3847}
                    ]
                    return pd.DataFrame(provinces)

                try:
                    # Load the province data
                    province_data = load_province_data()

                    # Merge the province data with the input DataFrame
                    # Convert the index of df to string to match the 'name' column in province_data
                    df.index = df.index.astype(str)

                    # Use pd.merge to merge province_data and df on 'name'
                    merged_data = pd.merge(province_data, df, left_on='name', right_on='Province', how='left')

                    # Create a ColumnLayer for AKD support
                    akd_layer = pdk.Layer(
                        "ColumnLayer",
                        data=merged_data,
                        get_position=["longitude", "latitude"],
                        get_position_offset=[-0.0001, -0.0001],
                        get_elevation="AKD",
                        elevation_scale=1000,  # Adjust to make the bars visible
                        radius=10000,
                        get_fill_color=[255, 0, 0, 160],  # Red color for AKD
                        pickable=True,
                        auto_highlight=True
                    )

                    # Create a ColumnLayer for Ranil Wickremesinghe support
                    ranil_layer = pdk.Layer(
                        "ColumnLayer",
                        data=merged_data,
                        get_position=["longitude", "latitude"],
                        get_position_offset=[0.0001, 0.0001],
                        get_elevation="Ranil Wickremesinghe",
                        elevation_scale=1000,
                        radius=6000,
                        get_fill_color=[0, 0, 255, 160],  # Blue color for Ranil Wickremesinghe
                        pickable=True,
                        auto_highlight=True
                    )

                    # Create a ColumnLayer for Sajith Premadasa support
                    sajith_layer = pdk.Layer(
                        "ColumnLayer",
                        data=merged_data,
                        get_position=["longitude", "latitude"],
                        get_elevation="Sajith Premadasa",
                        elevation_scale=1000,
                        radius=3000,
                        get_fill_color=[0, 255, 0, 160],  # Green color for Sajith Premadasa
                        pickable=True,
                        auto_highlight=True
                    )

                    # Combine the layers
                    layers = [akd_layer, ranil_layer, sajith_layer]

                    # Render the map with the 3D columns
                    st.pydeck_chart(
                        pdk.Deck(
                            map_style="mapbox://styles/mapbox/light-v9",
                            initial_view_state={
                                "latitude": 7.8731,
                                "longitude": 80.7718,
                                "zoom": 7,
                                "pitch": 50
                            },
                            layers=layers,
                            tooltip={
                                "html": "<b>{Province}</b><br/>AKD: {AKD}<br/>Ranil Wickremesinghe: {Ranil Wickremesinghe}<br/>Sajith Premadasa: {Sajith Premadasa}",
                                "style": {"backgroundColor": "steelblue", "color": "white"}
                            }
                        )
                    )

                except URLError as e:
                    st.error(f"Data load error: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

            else:
                st.write(value)
    else:
        st.info("No data available to display.")

def manifesto_comparator():
    st.header("📄 Election Manifesto Comparator")
    
    candidates = [
        "Ranil",
        "Sajith",
        "Anura",
        "Namal",
        "Dilith"
    ]

    candidate_options = [
        "Ranil Wickremesinghe - Independent (Incumbent President)",
        "Sajith Premadasa - Samagi Jana Balawegaya (SJB)",
        "Anura Kumara Dissanayake - National People's Power (NPP)",
        "Namal Rajapaksa - Sri Lanka Podujana Peramuna (SLPP)",
        "Dilith Jayaweera - Mawbima Janatha Party (MJP)"
    ]

    col1, col2 = st.columns(2)

    with col1:
        selected_candidate1 = st.selectbox(
            "Select first candidate:",
            options=candidate_options,
            index=0
        )

    with col2:
        selected_candidate2 = st.selectbox(
            "Select second candidate:",
            options=candidate_options,
            index=1
        )

    if st.button("💡 Compare Manifestos"):
        if selected_candidate1 == selected_candidate2:
            st.warning("Please select two different candidates.")
        else:
            # Map selected options back to original candidate names
            selected_names = [
                candidates[candidate_options.index(selected_candidate1)],
                candidates[candidate_options.index(selected_candidate2)]
            ]
            
            with st.spinner("Generating comparison..."):
                progress_placeholder = st.empty()
                progress_bar = progress_placeholder.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                response = compare_manifestos(selected_names)
                progress_placeholder.empty()
                st.success("**Comparison:**")
                st.write(response)
                
if 'app_mode' not in st.session_state:
    st.session_state['app_mode'] = "Home"

def set_app_mode(mode):
    st.session_state['app_mode'] = mode

def home():
    st.markdown(
        """
        <style>
        .big-font {
            font-size:30px !important;
            font-weight: bold;
            color: #1E88E5;
        }
        .card {
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="big-font">Welcome to the Election RAG Assistant! 🎉</p>', unsafe_allow_html=True)

    st.write("Explore our powerful tools to stay informed about the upcoming election.")

    col1, col2, col3 = st.columns(3)
# Add CSS styles for the cards and buttons
    st.markdown(
        """
        <style>
            .card-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            .card {
                position: relative;
                width: 100%;
                max-width: 300px;
                height: 300px;
                background-size: cover;
                background-position: center;
                border-radius: 10px;
                overflow: hidden;
                transition: transform 0.3s, box-shadow 0.3s;
                color: white;
            }
            .card:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                box-sizing: border-box;
            }
            .card img {
                margin-bottom: 10px;
            }
            .card-button {
                margin-top: 15px;
                width: 100%;
                display: flex;
                justify-content: center;
            }
            /* Button Styles */
            .stButton > button {
                background-color: #1E88E5;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .stButton > button:hover {
                background-color: #1565C0;
            }
            /* Specific Background Images */
            .manifesto-card {
                background-image: url('https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=800&q=80');
            }
            .win-card {
                background-image: url('https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?auto=format&fit=crop&w=800&q=80');
            }
            .chat-card {
                background-image: url('https://images.unsplash.com/photo-1529101091764-c3526daf38fe?auto=format&fit=crop&w=800&q=80');
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with col1:
        st.markdown(f'''
            <div class="card manifesto-card">
                <div class="overlay">
                    <img src="https://img.icons8.com/color/96/000000/compare.png" width="50">
                    <h2 style="color:white">Manifesto Comparator</h2>
                    <p>Compare the manifestos of different candidates side by side.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.button("Try Manifesto Comparator", on_click=set_app_mode, args=("Manifesto Comparator",))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
            <div class="card win-card">
                <div class="overlay">
                    <img src="https://img.icons8.com/color/96/000000/trophy.png" width="50">
                    <h2 style="color:white">Win Predictor</h2>
                    <p>Get insights into potential election outcomes based on current data.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.button("Explore Win Predictor", on_click=set_app_mode, args=("Win Predictor",))
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="card chat-card">
            <div class="overlay">
                <img src="https://img.icons8.com/color/96/000000/chat.png" width="50">
                <h2 style="color:white">Election Chat Bot</h2>
                <p>Have a conversation with our AI-powered chatbot to learn more about the election.</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
        st.button("Chat with Election Bot", on_click=set_app_mode, args=("Election Chat Bot",))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.write("Stay informed, compare candidates, and make your voice heard in this election!")

def main():
    st.set_page_config(page_title="Election RAG Assistant", layout="wide")
    st.sidebar.title("Navigation")
    
    # Create buttons for each section in the sidebar
    st.sidebar.button("Home", on_click=set_app_mode, args=("Home",), use_container_width=True)
    st.sidebar.button("Manifesto Comparator", on_click=set_app_mode, args=("Manifesto Comparator",), use_container_width=True)
    st.sidebar.button("Win Predictor", on_click=set_app_mode, args=("Win Predictor",), use_container_width=True)
    st.sidebar.button("Election Chat Bot", on_click=set_app_mode, args=("Election Chat Bot",), use_container_width=True)

    st.title("🗳️ Election RAG Assistant")
    st.write("Click on the buttons in the sidebar to use different features of the application.")

    if st.session_state["app_mode"] == "Home":
        home()
    elif st.session_state["app_mode"] == "Manifesto Comparator":
        manifesto_comparator()
    elif st.session_state["app_mode"] == "Win Predictor":
        win_predictor()
    elif st.session_state["app_mode"] == "Election Chat Bot":
        election_chatbot()
    else:
        home()

if __name__ == "__main__":
    main()