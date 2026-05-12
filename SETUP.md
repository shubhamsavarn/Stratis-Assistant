# 🛠️ Setup & Installation Guide: InsightFlow AI

This guide provides detailed, step-by-step instructions to get the **InsightFlow AI Analytics Assistant** running on your local machine.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed:
1. **Ollama**: [Download here](https://ollama.com/). Required for local AI inference.
2. **Python 3.10+**: [Download here](https://www.python.org/). Required for the backend engine.
3. **Node.js 18+**: [Download here](https://nodejs.org/). Required for the React dashboard.
4. **Git**: To clone the repository.

---

## 🤖 1. AI Model Setup (Mandatory)

The system uses the **Qwen2.5:0.5b** model for fast, local execution.
1. Open your terminal.
2. Run the following command:
   ```bash
   ollama pull qwen2.5:0.5b
   ```
3. Ensure Ollama is running in the background (check your system tray).

---

## 🐳 2. Option A: Docker Deployment (Recommended)

This is the fastest way to get the entire stack (Frontend + Backend) running in a single command.

1. **Clone the Repo**:
   ```bash
   git clone <your-repo-url>
   cd Stratis-Assistant
   ```
2. **Launch the Stack**:
   ```bash
   docker-compose up --build
   ```
3. **Access the App**:
   - **Dashboard**: [http://localhost:5173](http://localhost:5173)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## 💻 3. Option B: Manual Setup (Local Development)

Use this method if you want to modify the code or run without Docker.

### Step 1: Backend Setup
1. Navigate to the project root:
   ```bash
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
2. **Initialize Data (ETL)**:
   This step processes the raw CSVs and PDFs into the local databases.
   ```bash
   python scripts/ingest.py
   ```
3. **Start the Backend**:
   ```bash
   python run_backend.py
   ```

### Step 2: Frontend Setup
1. Open a **new terminal** and navigate to the `frontend` folder:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. **Access the Dashboard**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 4. Verifying the Installation

To ensure everything is working correctly:
1. Open the Dashboard.
2. Go to the **AI Inquiry** tab.
3. Ask: *"Which titles performed best in 2025?"*
4. If you see a table and a chart, the **SQL Engine** is working.
5. Ask: *"Why is Stellar Run trending?"*
6. If the AI explains the marketing campaign context, the **PDF Vector Store** is working.

---

## 🛡️ 5. Security Note
The backend is protected by a mandatory API key. By default, the frontend is configured with the development key: `sk-insight-flow-2025`.

To modify this, check the `X-API-KEY` configuration in `backend/main.py`.

---

## ❓ Troubleshooting

- **Ollama Error**: If the AI doesn't respond, run `ollama serve` to ensure the local model server is active.
- **Port Conflict**: If port 8000 is taken, the backend will fail. Ensure no other service is using port 8000.
- **Data Missing**: If the AI says "I found no records," run `python scripts/ingest.py` again to rebuild the local SQLite database.

---
**InsightFlow AI** - *Secure, Traceable, Intelligent Analytics.*
