import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import time
import plotly.graph_objects as go
import datetime
# Load environment variables from .env file
load_dotenv()

# Constants for different API endpoints
MANIFESTO_API_URL = os.getenv("COMPARATOR_URL", "http://127.0.0.1:8000/compare")
WIN_PREDICTOR_API_URL = os.getenv("WIN_PREDICTOR_URL", "http://127.0.0.1:8000/win_predictor")
CHATBOT_API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000/generate")
FAKE_DETECTION_API_URL = os.getenv("FAKE_DETECTION_URL", "http://127.0.0.1:8000/fake_detection")

def generate_response(prompt, language):
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
    
    # Add language selection with more user-friendly options
    language_options = {
        "English 🇬🇧": "English",
        "සිංහල 🇱🇰": "Sinhala",
        "தமிழ் 🇱🇰": "Tamil"
    }
    selected_language = st.selectbox(
        "Choose your preferred language",
        options=list(language_options.keys()),
        index=0,
        help="Select the language you'd like to use for chatting with the Election Bot."
    )
    language = language_options[selected_language]
    
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
                response = generate_response(user_input, language)
                progress_placeholder.empty()
            st.session_state.messages.append({"type": "bot", "text": response, "language": language})
            st.session_state["user_input"] = ""

    st.text_input("Type your message here:", key="user_input", on_change=send_message)

    for msg in st.session_state.messages:
        if msg["type"] == "user":
            st.markdown(f"**You:** {msg['text']} ({selected_language.split()[0]})")
        else:
            st.markdown(f"**Election Bot:** {msg['text']} ({selected_language.split()[0]})")

# Global predicted data
data = None

def win_predictor():
    global data
    st.empty()  # Clear the previous content
    st.header("📈 Win Predictor")
    
    if st.button("Run the Predictor"):
        if data is None:
            # Custom progress bar
            with st.empty():
                col1, col2, col3 = st.columns([1, 6, 1])
                with col2:
                    progress_placeholder = st.empty()
                    progress_text = st.empty()
                    for i in range(101):
                        progress_placeholder.progress(i)
                        if i < 33:
                            progress_text.text("Analyzing historical election data...")
                        elif i < 66:
                            progress_text.text("Crunching numbers...")
                        else:
                            progress_text.text("Predicting winners...")
                        time.sleep(0.03)
                    
                    # Add a simple animation for prediction reveal
                    for _ in range(3):
                        progress_text.markdown("🔮 **Predicting winners** 🔮")
                        time.sleep(0.5)
                        progress_text.markdown("🔮 **Predicting winners.** 🔮")
                        time.sleep(0.5)
                        progress_text.markdown("🔮 **Predicting winners..** 🔮")
                        time.sleep(0.5)
                        progress_text.markdown("🔮 **Predicting winners...** 🔮")
                        time.sleep(0.5)
            
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
                    # Define a custom month order
                    month_order = ['March', 'April', 'May', 'June', 'July', 'August']
                    # Sort the DataFrame by the custom month order
                    df = df.reindex(month_order)
                    # Create a custom color palette
                    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080']  # Red, Green, Blue, Orange, Purple
                    fig = go.Figure()
                    for i, column in enumerate(df.columns):
                        fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines+markers', name=column, line=dict(color=colors[i % len(colors)])))
                    fig.update_layout(title=key, xaxis_title='Month', yaxis_title='Percentage', legend_title='Candidates')
                    st.plotly_chart(fig, use_container_width=True)
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
                elif value['type'] == "stacked bar" or "stacked_bar":
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

                        # Create a TextLayer for province names
                        text_layer = pdk.Layer(
                            "TextLayer",
                            data=merged_data,
                            get_position=["longitude", "latitude"],
                            get_text="name",
                            get_size=16,
                            get_color=[0, 0, 0, 255],
                            get_angle=0,
                            get_text_anchor="middle",
                            get_alignment_baseline="center"
                        )

                        # Combine the layers
                        layers = [akd_layer, ranil_layer, sajith_layer, text_layer]

                        # Render the map with the 3D columns and province names
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
        "Ranil Wickremesinghe",
        "Sajith Premadasa",
        "Anura Kumara Dissanayake",
        "Namal Rajapaksa",
        "Dilith Jayaweera"
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

def common():
    # Add two new buttons with a unique style before the poll data
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <style>
            .custom-button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 12px;
                width: 100%;
            }
            </style>
            <a href="https://eservices.elections.gov.lk/pages/myVoterRegistrationElection.aspx" target="_blank">
                <button class="custom-button">Check Your Eligibility</button>
            </a>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <style>
            .custom-button {
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 12px;
                width: 100%;
            }
            </style>
            <a href="https://eservices.elections.gov.lk/pages/ec_ct_KYC_PRE_RP.aspx?ref=MTE%3d" target="_blank">
                <button class="custom-button">Know Your Candidates</button>
            </a>
            """, 
            unsafe_allow_html=True
        )

    # Hardcoded poll data
    poll1_data = {
        'Candidate': ['Anura Dissanayake', 'Sajith Premadasa', 'Ranil Wickremesinghe', 'Namal Rajapaksa', 'Other'],
        'Votes': [36, 32, 28, 3, 1]
    }
    
    poll2_data = {
        'Candidate': ['Anura Dissanayake', 'Sajith Premadasa', 'Ranil Wickremesinghe', 'Namal Rajapaksa', 'Other'],
        'Votes': [36, 30, 25, 6, 3]
    }

    poll3_data = {
        'Candidate': ['Anura Dissanayake', 'Sajith Premadasa', 'Ranil Wickremesinghe', 'Namal Rajapaksa', 'Other'],
        'Votes': [88, 3.4, 6.2, 0.7, 1.7]
    }

    st.subheader("Sri Lankan Presidential Election Polls")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure(go.Bar(
            y=poll1_data['Candidate'],
            x=poll1_data['Votes'],
            orientation='h',
            marker=dict(
                color=['#FF0000', '#FFFF00', '#00FF00', '#8B0000', '#808080'],
                line=dict(color='rgba(50, 171, 96, 1.0)', width=1)
            )
        ))
        fig1.update_layout(
            title='IHP Poll: Voting Intentions (August 2023)',
            xaxis_title='Votes (%)',
            yaxis_title='Candidate',
            height=300,
            xaxis=dict(range=[0, max(poll1_data['Votes']) + 5])
        )
        chart1 = st.plotly_chart(fig1, use_container_width=True)
        st.markdown("[Source: IHP Press Release](https://www.ihp.lk/press-releases/ak-dissanayake-and-sajith-premadasa-led-august-voting-intent-amongst-all-adults)")

    with col2:
        fig2 = go.Figure(go.Bar(
            y=poll2_data['Candidate'],
            x=poll2_data['Votes'],
            orientation='h',
            marker=dict(
                color=['#FF0000', '#FFFF00', '#00FF00', '#8B0000', '#808080'],
                line=dict(color='rgba(128, 0, 128, 1.0)', width=1)
            )
        ))
        fig2.update_layout(
            title='Numbers.lk Poll: Voting Intentions (August 2023)',
            xaxis_title='Votes (%)',
            yaxis_title='Candidate',
            height=300,
            xaxis=dict(range=[0, max(poll2_data['Votes']) + 5])
        )
        chart2 = st.plotly_chart(fig2, use_container_width=True)
        st.markdown("[Source: Numbers.lk Release](https://numbers.lk/analysis/presidential-election-2024-voter-perception-analysis)")

    col3, col4 = st.columns(2)

    with col3:
        fig3 = go.Figure(go.Bar(
            y=poll3_data['Candidate'],
            x=poll3_data['Votes'],
            orientation='h',
            marker=dict(
                color=['#FF0000', '#FFFF00', '#00FF00', '#8B0000', '#808080'],
                line=dict(color='rgba(55, 128, 191, 1.0)', width=1)
            )
        ))
        fig3.update_layout(
            title='Helakuru Poll: Voting Intentions (September 2023)',
            xaxis_title='Votes (%)',
            yaxis_title='Candidate',
            height=300,
            xaxis=dict(range=[0, max(poll3_data['Votes']) + 5])
        )
        chart3 = st.plotly_chart(fig3, use_container_width=True)
        st.markdown("[Source: Helakuru Poll Results](https://drive.google.com/file/d/1n5UoAic9Piyq-PlE-fP42qj2pKgQ8ddB/view)")

    with col4:
        st.markdown("""
            <div style="background-color: #000000; border-radius: 10px; padding: 15px; border: 1px solid red;">
                <h3 style="color: red;">Disclaimer</h3>
                <p style="color: red;">These charts represent poll data from various sources and time periods. The accuracy and methodology of each poll may vary. Please interpret the results with caution and refer to the original sources for more detailed information.</p>
                <p style="color: red;">Note: Poll results may not be indicative of final election outcomes.</p>
            </div>
        """, unsafe_allow_html=True)

    # Animate the charts
    for i in range(1, 6):  # Reduced number of steps for faster animation
        time.sleep(0.05)  # Reduced delay for faster animation
        fig1.update_traces(x=[v * i / 5 for v in poll1_data['Votes']])
        chart1.plotly_chart(fig1, use_container_width=True)

        fig2.update_traces(x=[v * i / 5 for v in poll2_data['Votes']])
        chart2.plotly_chart(fig2, use_container_width=True)

        fig3.update_traces(x=[v * i / 5 for v in poll3_data['Votes']])
        chart3.plotly_chart(fig3, use_container_width=True)

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
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        @media (max-width: 768px) {
            .big-font {
                font-size: 24px !important;
            }
            .card {
                padding: 15px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .card-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .card {
                position: relative;
                width: 100%;
                max-width: 300px;
                height: 300px;
                border-radius: 10px;
                overflow: hidden;
                color: white;
                padding: 20px;
                box-sizing: border-box;
                animation: fadeIn 0.5s ease-out;
            }
            .card-content {
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .card img {
                width: 50px;
                height: 50px;
                margin-bottom: 10px;
                transition: transform 0.3s;
            }
            .card:hover img {
                transform: rotate(360deg);
            }
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            /* Specific Card Styles */
            .manifesto-card {
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
            }
            .win-card {
                background: linear-gradient(135deg, #2196F3, #1565C0);
            }
            .chat-card {
                background: linear-gradient(135deg, #FF9800, #F57C00);
            }
            .past-elections-card {
                background: linear-gradient(135deg, #9C27B0, #6A1B9A);
            }
            .card-button {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin-top: 10px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .card-button:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            @media (max-width: 768px) {
                .card {
                    height: auto;
                    min-height: 200px;
                }
                .card-container {
                    flex-direction: column;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h2 class='big-font'>Welcome to Sri Lankan Election Insights</h2>", unsafe_allow_html=True)
    st.write("Explore our comprehensive tools to stay informed about the upcoming Sri Lankan Presidential Election.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('''
            <div class="card manifesto-card">
                <div class="card-content">
                    <div class="card-header">
                        <img src="https://img.icons8.com/color/96/000000/compare.png" width="50">
                    </div>
                    <h3>Manifesto Comparator</h3>
                    <p>Compare the manifestos of different candidates side by side.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.button("Comparator Manifestos", key="manifesto_button", on_click=set_app_mode, args=("Manifesto Comparator",))

    with col2:
        st.markdown('''
            <div class="card win-card">
                <div class="card-content">
                    <div class="card-header">
                        <img src="https://img.icons8.com/color/96/000000/trophy.png" width="50">
                    </div>
                    <h3>Win Predictor</h3>
                    <p>Get insights into potential election outcomes based on current data.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.button("Predict the Winner", key="win_predictor_button", on_click=set_app_mode, args=("Win Predictor",))

    with col3:
        st.markdown('''
        <div class="card chat-card">
            <div class="card-content">
                <div class="card-header">
                    <img src="https://img.icons8.com/color/96/000000/chat.png" width="50">
                </div>
                <h3>Election Chat Bot</h3>
                <p>Have a conversation with our AI-powered chatbot to learn more about the election.</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
        st.button("Chat Now", key="chat_bot_button", on_click=set_app_mode, args=("Election Chat Bot",))

    with col4:
        st.markdown('''
        <div class="card past-elections-card">
            <div class="card-content">
                <div class="card-header">
                    <img src="https://img.icons8.com/color/96/000000/historical.png" width="50">
                </div>
                <h3>Past Elections</h3>
                <p>Explore the results and details of past Sri Lankan elections.</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
        st.button("View Election History", key="history_button", on_click=set_app_mode, args=("Past Elections",))

    # Call the common function here to display the poll results
    common()

def past_elections():
    st.header("🗳️ Past Sri Lankan Elections")

    elections = [
        {
            "year": 2019,
            "image": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sri_Lankan_Presidential_Election_2019.png",
            "winner": {
                "name": "Gotabaya Rajapaksa",
                "party": "SLPP",
                "votes": 6924255,
                "percentage": 52.25
            },
            "runner_up": {
                "name": "Sajith Premadasa",
                "party": "NDF",
                "votes": 5564239,
                "percentage": 41.99
            },
            "others": {
                "votes": 764005,
                "percentage": 5.76
            },
            "total_votes": 13252499,
            "turnout": 83.72
        },
        {
            "year": 2015,
            "image": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Sri_Lankan_Presidential_Election_2015.png",
            "winner": {
                "name": "Maithripala Sirisena",
                "party": "NDF",
                "votes": 6217162,
                "percentage": 51.28
            },
            "runner_up": {
                "name": "Mahinda Rajapaksa",
                "party": "SLFP",
                "votes": 5768090,
                "percentage": 47.58
            },
            "others": {
                "votes": 138200,
                "percentage": 1.14
            },
            "total_votes": 12123452,
            "turnout": 81.52
        },
        {
            "year": 2010,
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/89/Sri_Lankan_Presidential_Election_2010.png",
            "winner": {
                "name": "Mahinda Rajapaksa",
                "party": "SLFP",
                "votes": 6015934,
                "percentage": 57.88
            },
            "runner_up": {
                "name": "Sarath Fonseka",
                "party": "NDF",
                "votes": 4173185,
                "percentage": 40.14
            },
            "others": {
                "votes": 204494,
                "percentage": 1.97
            },
            "total_votes": 10393613,
            "turnout": 74.50
        },
        {
            "year": 2005,
            "image": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Sri_Lankan_Presidential_Election_2005.png",
            "winner": {
                "name": "Mahinda Rajapaksa",
                "party": "SLFP",
                "votes": 4887152,
                "percentage": 50.29
            },
            "runner_up": {
                "name": "Ranil Wickremesinghe",
                "party": "UNP",
                "votes": 4706366,
                "percentage": 48.43
            },
            "others": {
                "votes": 123521,
                "percentage": 1.28
            },
            "total_votes": 9717039,
            "turnout": 73.73
        },
        {
            "year": 1999,
            "image": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Sri_Lankan_Presidential_Election_1999.png",
            "winner": {
                "name": "Chandrika Kumaratunga",
                "party": "SLFP",
                "votes": 4312157,
                "percentage": 51.12
            },
            "runner_up": {
                "name": "Ranil Wickremesinghe",
                "party": "UNP",
                "votes": 3602748,
                "percentage": 42.71
            },
            "others": {
                "votes": 520849,
                "percentage": 6.17
            },
            "total_votes": 8435754,
            "turnout": 73.31
        },
        {
            "year": 1994,
            "image": "https://upload.wikimedia.org/wikipedia/commons/1/16/Sri_Lankan_Presidential_Election_1994.png",
            "winner": {
                "name": "Chandrika Kumaratunga",
                "party": "SLFP",
                "votes": 4709205,
                "percentage": 62.28
            },
            "runner_up": {
                "name": "Srima Dissanayake",
                "party": "UNP",
                "votes": 2715283,
                "percentage": 35.91
            },
            "others": {
                "votes": 137038,
                "percentage": 1.81
            },
            "total_votes": 7561526,
            "turnout": 70.47
        },
        {
            "year": 1988,
            "image": "https://upload.wikimedia.org/wikipedia/commons/5/54/Sri_Lankan_Presidential_Election_1988.png",
            "winner": {
                "name": "Ranasinghe Premadasa",
                "party": "UNP",
                "votes": 2569199,
                "percentage": 50.43
            },
            "runner_up": {
                "name": "Sirimavo Bandaranaike",
                "party": "SLFP",
                "votes": 2289860,
                "percentage": 44.95
            },
            "others": {
                "votes": 235719,
                "percentage": 4.63
            },
            "total_votes": 5094778,
            "turnout": 55.32
        },
        {
            "year": 1982,
            "image": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Sri_Lankan_presidential_election_1982.png",
            "winner": {
                "name": "J. R. Jayewardene",
                "party": "UNP",
                "votes": 3450811,
                "percentage": 52.91
            },
            "runner_up": {
                "name": "Hector Kobbekaduwa",
                "party": "SLFP",
                "votes": 2548438,
                "percentage": 39.07
            },
            "others": {
                "votes": 522898,
                "percentage": 8.02
            },
            "total_votes": 6522147,
            "turnout": 81.06
        }
    ]

    for election in elections:
        st.subheader(f"{election['year']} Presidential Election")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(election['image'], caption=f"{election['year']} Election", use_column_width=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: #000000; border-radius: 15px; padding: 25px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); border: 1px solid #e0e0e0;">
                <h3 style="color: #1E88E5; margin-bottom: 20px; font-size: 24px; text-align: center;">Election Results</h3>
                <div style="margin-bottom: 20px; background-color: #e8f5e9; padding: 15px; border-radius: 10px;">
                    <strong style="color: #4CAF50; font-size: 18px;">Winner:</strong> 
                    <span style="font-size: 18px; font-weight: bold; color: #000000;">{election['winner']['name']} ({election['winner']['party']})</span><br>
                    <span style="margin-left: 20px; font-size: 16px; color: #000000;">Votes: {election['winner']['votes']:,} ({election['winner']['percentage']:.2f}%)</span>
                </div>
                <div style="margin-bottom: 20px; background-color: #fff3e0; padding: 15px; border-radius: 10px;">
                    <strong style="color: #FFA000; font-size: 18px;">Runner-up:</strong> 
                    <span style="font-size: 18px; font-weight: bold; color: #000000;">{election['runner_up']['name']} ({election['runner_up']['party']})</span><br>
                    <span style="margin-left: 20px; font-size: 16px; color: #000000;">Votes: {election['runner_up']['votes']:,} ({election['runner_up']['percentage']:.2f}%)</span>
                </div>
                <div style="background-color: #f3e5f5; padding: 15px; border-radius: 10px;">
                    <strong style="color: #7E57C2; font-size: 18px;">Others:</strong> 
                    <span style="font-size: 16px; color: #000000;">{election['others']['votes']:,} votes ({election['others']['percentage']:.2f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 40px 0; border: 0; border-top: 2px solid #e0e0e0;'>", unsafe_allow_html=True)


def presidential_election(availability):
    st.header("🗳 Presidential Elections")
    if availability:
        getData()
    else:
        st.write("Comming Soon...")
def getData():
    sheet_id = "1NCLSJbgstmJu2zI-VGB7p-7yKs9X13po2O1XKgIAhz0"
    import pandas as pd
    
    # Get the list of all sheet names
    sheet_list = pd.read_excel(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx", sheet_name=None).keys()
    
    # Remove the last sheet and put it first
    sheet_list = list(sheet_list)
    last_sheet = sheet_list.pop()
    sheet_list.insert(0, last_sheet)

    # Create tabs for each sheet
    tabs = st.tabs(sheet_list)
    
    # Create a dictionary to store the loaded data for each sheet
    sheet_data = {}

    # Loop through each tab and sheet
    for tab, sheet_name in zip(tabs, sheet_list):
        with tab:
            st.subheader(f"Data from sheet: {sheet_name}")
            
            # Check if the data for this sheet has already been loaded
            if sheet_name not in sheet_data:
                # If not, load the data when the tab is clicked
                if st.button(f"Load data for {sheet_name}"):
                    with st.spinner(f"Loading data for {sheet_name}..."):
                        df = pd.read_excel(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx", sheet_name=sheet_name)
                        sheet_data[sheet_name] = df
                    st.success(f"Data for {sheet_name} loaded successfully!")
            
            # If the data is loaded, display it and create visualizations
            if sheet_name in sheet_data:
                col1,col2 = st.columns(2,gap='large')
                with col1:
                    st.markdown("""
                        <style>
                            .stDataFrame {
                                background-color: #f0f8ff;
                                border-radius: 10px;
                                padding: 10px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }
                            .stDataFrame [data-testid="stDataFrameDataCell"] {
                                font-family: 'Arial', sans-serif;
                                color: #333;
                            }
                            .stDataFrame [data-testid="stDataFrameDataCell"]:nth-child(even) {
                                background-color: #e6f3ff;
                            }
                        </style>
                    """, unsafe_allow_html=True)
                    
                        # Start of Selection
                        # Start of Selection
                    st.markdown("### 📊 Election Data")
                    
                    column_config = {}
                    
                    # Hide the first column by excluding it from the displayed dataframe
                    df_display = sheet_data[sheet_name].copy()
                    first_column = df_display.columns[0]
                    df_display.drop(columns=[first_column], inplace=True)
                    
                    # Freeze the second column by keeping it first in the display
                    second_column = df_display.columns[0]
                    column_config[second_column] = st.column_config.Column()
                    
                    # Configure the remaining columns
                    for col in df_display.columns[1:]:
                        if df_display[col].dtype in ['float64', 'int64']:
                            column_config[col] = st.column_config.NumberColumn(
                                format="{:.2f}%",
                                help=f"Percentage for {col}",
                                min_value=0,
                                max_value=100,
                                step=0.01,
                                color="blue"
                            )
                    
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True,
                        height=1000,  # Adjust this value as needed to fit all rows
                        column_config=column_config
                    )
                    st.markdown("🔍 Hover over column headers for more information.")
                with col2:
                    visualize_data(sheet_data[sheet_name])
            else:
                st.info(f"Click the button above to load data for {sheet_name}")

def visualize_data(df):
    import plotly.express as px
    
    # Define color mapping for candidates
    color_map = {
        'RW': 'green',
        'Sajith': 'yellowgreen',
        'AKD': 'purple',
        'Namal': 'red',
        'Dilith': 'blue',
        'Other': 'white'
    }

    # Filter out the 'TOTAL' and 'PRECENTAGE' rows
    df_filtered = df[~df['Electoral Division'].isin(['TOTAL', 'PRECENTAGE'])]
    
    # Create the map
    import pydeck as pdk
    from urllib.error import URLError

    @st.cache_data
    def load_electoral_district_data():
        # Updated electoral district data for Sri Lanka
        districts = [
            {"name": "Colombo", "latitude": 6.9271, "longitude": 79.8612},
            {"name": "Gampaha", "latitude": 7.0917, "longitude": 80.0000},
            {"name": "Kalutara", "latitude": 6.5854, "longitude": 79.9607},
            {"name": "Kandy", "latitude": 7.2906, "longitude": 80.6337},
            {"name": "Matale", "latitude": 7.4675, "longitude": 80.6234},
            {"name": "Nuwara Eliya", "latitude": 6.9497, "longitude": 80.7891},
            {"name": "Galle", "latitude": 6.0535, "longitude": 80.2210},
            {"name": "Matara", "latitude": 5.9549, "longitude": 80.5550},
            {"name": "Hambantota", "latitude": 6.1429, "longitude": 81.1212},
            {"name": "Jaffna", "latitude": 9.6615, "longitude": 80.0255},
            {"name": "Vanni", "latitude": 8.7514, "longitude": 80.4997},
            {"name": "Batticaloa", "latitude": 7.7170, "longitude": 81.7000},
            {"name": "Digamadulla", "latitude": 7.2853, "longitude": 81.6716},
            {"name": "Trincomalee", "latitude": 8.5711, "longitude": 81.2335},
            {"name": "Kurunegala", "latitude": 7.4818, "longitude": 80.3609},
            {"name": "Puttalam", "latitude": 8.0408, "longitude": 79.8394},
            {"name": "Anuradhapura", "latitude": 8.3114, "longitude": 80.4037},
            {"name": "Polonnaruwa", "latitude": 7.9403, "longitude": 81.0188},
            {"name": "Badulla", "latitude": 6.9934, "longitude": 81.0550},
            {"name": "Monaragala", "latitude": 6.8872, "longitude": 81.3501},
            {"name": "Ratnapura", "latitude": 6.7056, "longitude": 80.3847},
            {"name": "Kegalle", "latitude": 7.2513, "longitude": 80.3464}
        ]
        return pd.DataFrame(districts)

    try:
        # Load the electoral district data
        district_data = load_electoral_district_data()

        # Merge the district data with the input DataFrame
        df_filtered.index = df_filtered.index.astype(str)
        merged_data = pd.merge(district_data, df_filtered, left_on='name', right_on='Electoral Division', how='left')

        # Create layers for each candidate
        layers = []
        candidates = ['RW', 'Sajith', 'AKD', 'Namal', 'Dilith']
        colors = [[0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 165, 0], [128, 0, 128]]

        for candidate, color in zip(candidates, colors):
            layer = pdk.Layer(
                "ColumnLayer",
                data=merged_data,
                get_position=["longitude", "latitude"],
                get_elevation=candidate,
                elevation_scale=100,
                radius=10000,
                get_fill_color=color + [160],
                pickable=True,
                auto_highlight=True
            )
            layers.append(layer)

        # Create a TextLayer for district names
        text_layer = pdk.Layer(
            "TextLayer",
            data=merged_data,
            get_position=["longitude", "latitude"],
            get_text="name",
            get_size=16,
            get_color=[0, 0, 0, 255],
            get_angle=0,
            get_text_anchor="middle",
            get_alignment_baseline="center"
        )
        layers.append(text_layer)

        # Render the map with the 3D columns and district names
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
                    "html": "<b>{name}</b><br/>RW: {RW}<br/>Sajith: {Sajith}<br/>AKD: {AKD}<br/>Namal: {Namal}<br/>Dilith: {Dilith}",
                    "style": {"backgroundColor": "steelblue", "color": "white"}
                }
            )
        )

    except URLError as e:
        st.error(f"Data load error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    # Create the stacked bar chart
    df_melt = df_filtered.melt(id_vars=['Electoral Division'], 
                               value_vars=['RW', 'Sajith', 'AKD', 'Namal', 'Dilith', 'Other'],
                               var_name='Candidate', value_name='Votes')
    
    fig_bar = px.bar(df_melt, x='Electoral Division', y='Votes', color='Candidate',
                     title='Votes by Candidate and Division',
                     color_discrete_map=color_map)
    
    st.plotly_chart(fig_bar)
    
    # Create the leaderboard
    leaderboard = df.loc[df['Electoral Division'] == 'TOTAL', ['RW', 'Sajith', 'AKD', 'Namal', 'Dilith', 'Other']].T
    if not leaderboard.empty:
        leaderboard = leaderboard.sort_values(by=leaderboard.columns[0], ascending=False)
        leaderboard.columns = ['Total Votes']
        
        st.subheader("Leaderboard")
        st.table(leaderboard.style.background_gradient(cmap='YlOrRd'))
    else:
        st.warning("No data available for the leaderboard.")

def fake_detection():
    st.header("🕵️ Fake News Detection")
    
    claim = st.text_area("Enter the claim you want to verify:", height=100)
    
    if st.button("Verify Claim"):
        if claim:
            with st.spinner("Analyzing claim..."):
                try:
                    headers = {
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "prompt": claim
                    }
                    response = requests.post(FAKE_DETECTION_API_URL, headers=headers, data=json.dumps(payload))
                    if response.status_code == 200:
                        result = response.json()
                        st.subheader("Final Verdict")
                        st.info(result["response"])
                        
                        st.subheader("Detailed Analysis")
                        for verification in result["verifications"]:
                            with st.expander(f"Subclaim: {verification['subclaim']}"):
                                st.write(verification['verification'])
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a claim to verify.")

def main():
    st.set_page_config(page_title="Sri Lankan Election Insights", layout="wide")
    
    today = datetime.datetime.now()
    election_date = datetime.datetime(2024, 9, 21, 8, 0, 0)
    time_until_election = election_date - today
    days_until_election = time_until_election.days
    hours_until_election = time_until_election.seconds // 3600
    minutes_until_election = (time_until_election.seconds % 3600) // 60
    
    # Create a more professional looking sidebar
    with st.sidebar:
        st.title("Election Dashboard")
        st.markdown("---")
        if st.button("🏠 Home", use_container_width=True):
            set_app_mode("Home")
        if st.button("📊 Manifesto Comparator", use_container_width=True):
            set_app_mode("Manifesto Comparator")
        if st.button("🏆 Win Predictor", use_container_width=True):
            set_app_mode("Win Predictor")
        if st.button("💬 Election Chat Bot", use_container_width=True):
            set_app_mode("Election Chat Bot")
        if st.button("🕵️ Fake News Detection", use_container_width=True):
            set_app_mode("Fake News Detection")
        if st.button("🗳 Past Elections", use_container_width=True):
            set_app_mode("Past Elections")
        if st.button("🗳 Presidential Elections", use_container_width=True):
            set_app_mode("Presidential Elections")
        st.markdown("---")
        st.info("Select a feature from above to get started.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🗳 Sri Lankan Election Insights")
    with col2:
        st.markdown(f"""
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        .countdown-container {{
            background-color: #000000;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            animation: pulse 2s infinite;
            border: 2px solid #1E88E5;
        }}
        .countdown-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .countdown-number {{
            font-size: 28px;
            font-weight: bold;
            margin: 5px 0;
        }}
        .countdown-label {{
            font-size: 14px;
            text-transform: uppercase;
        }}
        .countdown-unit {{
            display: inline-block;
            margin: 0 10px;
        }}
        </style>
        <div class='countdown-container'>
            <div class='countdown-title'>Election Countdown</div>
            <div class='countdown-unit'>
                <div class='countdown-number'>{days_until_election}</div>
                <div class='countdown-label'>Days</div>
            </div>
            <div class='countdown-unit'>
                <div class='countdown-number'>{hours_until_election:02d}</div>
                <div class='countdown-label'>Hours</div>
            </div>
            <div class='countdown-unit'>
                <div class='countdown-number'>{minutes_until_election:02d}</div>
                <div class='countdown-label'>Minutes</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state["app_mode"] == "Home":
        home()
    elif st.session_state["app_mode"] == "Manifesto Comparator":
        manifesto_comparator()
    elif st.session_state["app_mode"] == "Win Predictor":
        win_predictor()
    elif st.session_state["app_mode"] == "Election Chat Bot":
        election_chatbot()
    elif st.session_state["app_mode"] == "Fake News Detection":
        fake_detection()
    elif st.session_state["app_mode"] == "Past Elections":
        past_elections()
    elif st.session_state["app_mode"] == "Presidential Elections":
        presidential_election(True)
    else:
        home()


    # Add a footer
    st.markdown("---")
    st.markdown("""
    <div style='background-color: transparent; padding: 10px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #1E88E5;'>
        <p style='font-style: italic; color: #1E88E5;'>Empowering voters with data-driven insights and impartial information, powered by advanced AI.<br>Explore our comprehensive tools to stay informed about the upcoming Sri Lankan Presidential Election.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>© 2023 Sri Lankan Election Insights. All rights reserved.</p>
            <p>Developed with ❤ for a better informed electorate.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

