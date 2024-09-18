# Sri Lankan Election Insights

Sri Lankan Election Insights is a comprehensive application that leverages FastAPI for the backend and Streamlit for the frontend to provide AI-generated responses and analysis related to the Sri Lankan Elections 2024. Using advanced technologies like LangChain, FAISS, and LLM models, this project offers an interactive interface for users to query election manifestos, compare candidates, and get predictions on election outcomes.

The project is deployed and accessible at: https://bit.ly/SL_Election

## 📚 Table of Contents

1. [Features](#🛠Features)
2. [Prerequisites](#Prerequisites)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Running the Application](#running-the-application)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

## 🛠Features

- **AI-Powered Responses:** Generate insightful answers based on Sri Lankan election data.
- **Candidate Comparison:** Compare policies and manifestos of multiple candidates.
- **Win Predictor:** Analyze polling data and provide election outcome predictions.
- **Multi-language Support:** Responses available in English, Sinhala, and Tamil.
- **Interactive Frontend:** User-friendly interface built with Streamlit.
- **Robust Backend:** FastAPI server handling requests efficiently.

## ⚙️ Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🗂 Project Structure

- **Manifesto Comparator/**: Contains the FastAPI backend and data files.
- **Streamlit Frontend/**: Houses the Streamlit application for the user interface.
- **requirements.txt**: Lists all the dependencies for the project.

## 🚀 Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/CodeBustersCrafter/060_Code_Busters.git
   cd 060_Code_Busters
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   AZURE_TRANSLATE_ENDPOINT=your_azure_translate_endpoint
   AZURE_TRANSLATE_KEY=your_azure_translate_key
   ```

## ▶️ Running the Application

1. Start the FastAPI backend:
   ```
   python "Manifesto Comparator/backend/app.py"
   ```

2. In a new terminal, launch the Streamlit frontend:
   ```
   cd "Manifesto Comparator\Streamlit Frontend"
   streamlit run streamlit_app.py
   ```

## 🖥️ Usage

1. Access the Streamlit app at `http://localhost:8501` or visit the deployed version at https://bit.ly/SL_Election.
2. Use the interface to:
   - Ask questions about the Sri Lankan Elections 2024
   - Compare candidate manifestos
   - View win predictions and polling analysis

## 🐛 Troubleshooting

If you encounter any issues:
- Ensure all dependencies are correctly installed.
- Verify that your `.env` file contains the correct API keys.
- Check if the required ports (8000 for FastAPI, 8501 for Streamlit) are available.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and create a pull request with your features or fixes.

## 📄 License

This project is licensed under the MIT License.
