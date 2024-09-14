```markdown
# Election RAG Assistant

![Project Logo](https://via.placeholder.com/150)

**Election RAG Assistant** is a comprehensive application that leverages FastAPI for the backend and Streamlit for the frontend to provide insightful AI-generated responses based on election-related text data. Utilizing advanced technologies like LangChain, FAISS, and OpenAI's LLaMA model, this project offers an interactive interface for users to query and analyze election manifestos and related documents.

## 📚 Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Backend Setup](#2-backend-setup)
    - [3. Frontend Setup](#3-frontend-setup)
5. [Running the Application](#running-the-application)
    - [1. Start the FastAPI Backend](#1-start-the-fastapi-backend)
    - [2. Launch the Streamlit Frontend](#2-launch-the-streamlit-frontend)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Contributing](#contributing)
10. [License](#license)
11. [Acknowledgements](#acknowledgements)

---

## 🛠 Features

- **AI-Powered Responses:** Generate insightful answers based on provided election text data.
- **Interactive Frontend:** User-friendly interface built with Streamlit.
- **Robust Backend:** FastAPI server handling requests efficiently.
- **Contextual Understanding:** Utilizes LangChain and FAISS for context retrieval.
- **Secure Configuration:** Environment variables managed via `.env` files.

---

## ⚙️ Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System:** Windows 10 or later
- **Python:** Version 3.8 or higher
- **Package Manager:** `pip`
- **Git:** Installed and configured

> **Note:** It's highly recommended to use virtual environments to manage dependencies and avoid conflicts.

---



- **Manifesto Comparator/**: Contains the FastAPI backend, including application logic and necessary text data.
- **Streamlit Frontend/**: Houses the Streamlit application for the user interface.
- **`requirements.txt`**: Lists all the dependencies for both backend and frontend.
- **`.env`**: Stores environment variables securely (ensure this file is excluded from version control).

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/yourusername/Election_RAG.git
cd Election_RAG
```

*Replace `yourusername` with your actual GitHub username.*

### 2. Backend Setup

#### a. Navigate to the Backend Directory

```bash
cd "Manifesto Comparator"
```

#### b. Create a Virtual Environment

It's best to create a virtual environment to manage dependencies.

```bash
python -m venv venv
```

#### c. Activate the Virtual Environment

**For PowerShell:**

If you encounter execution policy issues, refer to the [Troubleshooting](#troubleshooting) section.

```powershell
.\venv\Scripts\Activate.ps1
```

**For Command Prompt (CMD):**

Alternatively, you can use CMD to avoid execution policy restrictions.

```cmd
venv\Scripts\activate.bat
```

#### d. Install Backend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### e. Configure Environment Variables

Create a `.env` file in the `Manifesto Comparator` directory with the following content:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

> **Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key. **Do not** share or expose this key publicly.

### 3. Frontend Setup

#### a. Navigate to the Frontend Directory

Open a new terminal or command prompt window, then run:

```bash
cd "Streamlit Frontend"
```

#### b. Create a Virtual Environment

```bash
python -m venv venv
```

#### c. Activate the Virtual Environment

**For PowerShell:**

Refer to the [Troubleshooting](#troubleshooting) section if you encounter issues.

```powershell
.\venv\Scripts\Activate.ps1
```

**For Command Prompt (CMD):**

```cmd
venv\Scripts\activate.bat
```

#### d. Install Frontend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### e. Configure Environment Variables

Create a `.env` file in the `Streamlit Frontend` directory with the following content:

```env
FASTAPI_URL=http://127.0.0.1:8000/generate
```

> **Note:** If your FastAPI backend runs on a different host or port, update the `FASTAPI_URL` accordingly.

---

## ▶️ Running the Application

### 1. Start the FastAPI Backend

Ensure you have activated the backend virtual environment.

```bash
cd "Manifesto Comparator"
uvicorn app:app --reload
```

- **Server URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Launch the Streamlit Frontend

Ensure you have activated the frontend virtual environment.

```bash
cd "Streamlit Frontend"
streamlit run streamlit_app.py
```

- **App URL:** Typically [http://localhost:8501](http://localhost:8501)

---

## 🖥️ Usage

1. **Access the Streamlit App:**
   - Open your web browser and navigate to [http://localhost:8501](http://localhost:8501).

2. **Enter Your Prompt:**
   - In the text area labeled 🔍 **"Enter your prompt:"**, input your query related to election data. For example:
     ```
     What are the main political parties mentioned in the text?
     ```

3. **Generate Response:**
   - Click the 💡 **"Generate Response"** button.
   - The AI-generated response will appear below the button.

4. **View Responses:**
   - Responses are generated based on the context provided in `text_file_db.txt`.

---

## 🐛 Troubleshooting

### 1. **Virtual Environment Activation Issues**

**Error Message:**

```
Activate.ps1 cannot be loaded. The file ... is not digitally signed.
```

**Solution:**

Refer to the [Troubleshooting](#troubleshooting) section for guidance on modifying PowerShell's execution policies or using alternative activation methods.

### 2. **Indentation Errors in `app.py`**

**Error Message:**

```
IndentationError: unexpected indent
```

**Solution:**

- Ensure that all top-level code in `app.py` starts at the beginning of the line without unnecessary spaces or tabs.
- Use a reliable code editor like VS Code to visualize and correct indentation.
- Refer to the corrected `app.py` provided earlier.

### 3. **File Not Found Error for `text_file_db.txt`**

**Error Message:**

```
Error reading file: [Errno 2] No such file or directory: 'text_file_db.txt'
```

**Solution:**

- Ensure that `text_file_db.txt` is located in the `Manifesto Comparator` directory.
- Confirm that the file name is correctly spelled and matches the reference in `main.py`.
- Verify the dynamic path resolution in `main.py` as outlined in the [Backend Setup](#2-backend-setup).

### 4. **CORS Errors When Frontend Communicates with Backend**

**Solution:**

- Ensure that the `CORSMiddleware` in `app.py` includes the correct origins:
  ```python
  origins = [
      "http://localhost",
      "http://localhost:8501",
      "http://127.0.0.1:8501",
  ]
  ```
- Restart the FastAPI server after making changes to `app.py`.

### 5. **FastAPI Server Not Starting**

**Possible Reasons:**

- Missing dependencies.
- Incorrect environment variable configurations.
- Port already in use.

**Solution:**

- Ensure all dependencies are installed via `requirements.txt`.
- Verify that the `.env` file contains the correct `OPENAI_API_KEY`.
- Check if port `8000` is free or use a different port by modifying the `uvicorn` command:
  ```bash
  uvicorn app:app --reload --port 8001
  ```

---

## 💡 Best Practices

- **Secure Environment Variables:**
  - Never commit your `.env` files to version control.
  - Add `.env` to your `.gitignore` file:
    ```
    # .gitignore
    *.env
    ```

- **Use Virtual Environments:**
  - Isolate project dependencies to avoid conflicts.
  - Regularly update dependencies to their latest stable versions.

- **Consistent Code Formatting:**
  - Use tools like **Black** or **autopep8** to maintain consistent code style.
  - Example with **Black**:
    ```bash
    pip install black
    black .
    ```

- **Logging and Monitoring:**
  - Implement comprehensive logging to track application behavior and errors.
  - Use logging levels (`INFO`, `WARNING`, `ERROR`) appropriately.

- **Version Control:**
  - Use Git for tracking changes and collaborating.
  - Commit frequently with meaningful messages.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make Your Changes**

4. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature Description"
   ```

5. **Push to the Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Create a Pull Request**

   - Describe your changes and the purpose behind them.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [FAISS](https://faiss.ai/)
- [OpenAI](https://openai.com/)
- [Python Dotenv](https://github.com/theskumar/python-dotenv)

---

**Happy Coding!** 🚀

```
