# 🚀 FairLens AI — Complete Setup & Architecture Guide

FairLens AI is a robust, production-ready ML fairness auditing platform. It helps data scientists and developers detect, explain, and fix bias in machine learning models mathematically and contextually using Google Vertex AI (Gemini).

This guide provides step-by-step instructions for configuring the cloud dependencies, starting the server, and running the application.

---

## 🛠️ 1. Prerequisites

Before starting, ensure your local environment contains the following:
* **Python 3.10+** (for the FastAPI backend & ML pipelines)
* **Node.js 18+** & npm (for the React/Vite frontend)
* **Git** (optional, for version control)

---

## ☁️ 2. Connecting Google Cloud APIs (Database & Gemini)

FairLens AI uses **Firebase Firestore** for persistent session storage and **Vertex AI (Gemini 1.5 Flash)** for dynamic, human-readable bias explanations. 

To use these features, you must configure a Google Cloud Service Account.

### Step 2.1: Create a Google Cloud Project & Enable APIs
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `fairlens-hackathon`).
3. In the search bar, look for **Vertex AI API** and click **Enable**.
4. In the search bar, look for **Firebase Management API** and click **Enable** (or set up a Firebase project and link it to your existing GCP project).

### Step 2.2: Setup Firebase Firestore Data Repository
1. Go to your [Firebase Console](https://console.firebase.google.com/) or Cloud Firestore in GCP.
2. Under **Build > Firestore Database**, click **Create Database**.
3. Select **Production Mode** (or Test Mode if purely for local dev) and choose a location.
4. *Note: FairLens automatically creates a `sessions` collection on the fly; no manual schema design is necessary.*

### Step 2.3: Generate Service Account Credentials
1. In the Google Cloud Console, navigate to **IAM & Admin > Service Accounts**.
2. Click **Create Service Account**, name it (e.g., `fairlens-api-agent`), and proceed.
3. Grant the following critical Roles:
   * **Vertex AI User** (required for Gemini)
   * **Cloud Datastore User** (required for Firestore read/write)
4. Click **Done**.
5. Click on the newly created service account in the list, go to the **Keys** tab -> **Add Key** -> **Create New Key**.
6. Select **JSON** format and click Create. 
7. Save this `.json` file securely to your local machine (e.g., `C:/keys/fairlens-service-account.json`).

> **💡 MOCK MODE FALLBACK**: If you are running at a hackathon and don't have time to configure Google Cloud immediately, *don't worry*. The backend has an automatic fallback. If credentials are not found, the app gracefully degrades to an in-memory database and provides mock AI explanations so your UI development is unblocked!

---

## ⚙️ 3. Backend Setup (FastAPI + Machine Learning)

The backend runs Python, handling the Scikit-Learn pipelines, SHAP logic, and cloud routing.

### Step 3.1: Environment Configuration
Navigate to the `backend/` directory.

You will see an `.env` file. Open it and paste the absolute path to the `.json` file you downloaded in Step 2:
```bash
# backend/.env 
GOOGLE_APPLICATION_CREDENTIALS="C:\keys\fairlens-service-account.json"
```
*(Mac/Linux users: `/Users/name/keys/...`)*

### Step 3.2: Starting the Server

**Windows (PowerShell - Recommended):**
```powershell
cd backend
.\run_backend.ps1
```

**macOS/Linux:**
```bash
cd backend
bash run_backend.sh
```

**What the scripts do automatically:**
1. Creates an isolated local virtual environment (`backend/venv`).
2. Installs requirements from `requirements.txt` (FastAPI, pandas, shap, fairlearn, firebase-admin, etc).
3. Connects to your GCP Credentials.
4. Starts the API server on `http://localhost:8000`.

*You can verify the backend is running by visiting `http://localhost:8000/docs` in your browser.*

---

## 💻 4. Frontend Setup (React UI)

The frontend is a Vite-powered React dashboard living in the `frontend/` directory.

### Step 4.1: Environment Configuration
Ensure your `frontend/.env` file points to your local backend.
```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 4.2: Starting the React Development Server
Open a **new, separate terminal** tab (leave the backend running).

**Windows (PowerShell):**
```powershell
cd frontend
.\run_frontend.ps1
```

**macOS/Linux:**
```bash
cd frontend
bash run_frontend.sh
```
*The frontend will start and be available at `http://localhost:5173`.*

---

## 🧠 5. Using the Architecture (Under the Hood)

FairLens AI operates on a **Stateless Session Architecture**:

1. **Upload (`/api/upload`)**: You upload a CSV. The backend creates a localized UUID (`session_id`), saves the CSV into `backend/data/`, and creates a session metadata doc in Firestore so large ML data isn't bottlenecking your database.
2. **Detect (`/api/analyze`)**: The frontend calls analyze with the `session_id`. The backend spins up the CSV, trains a Logistic Regression model, assesses it for `Demographic Parity` and `Equalized Odds`, returns a 0-100 Fairness Score, and saves the metrics into Firestore.
3. **Explain (`/api/explain` & `/api/ai-explain`)**: 
   * The `explain` endpoint computes algorithmic SHAP feature attributions on a granular, per-subgroup level.
   * `ai-explain` pulls the statistics from Firestore and sends them natively to Vertex AI (Gemini Flash) for structured contextual interpretation.
4. **Fix (`/api/fix`)**: The Advanced Mitigation Engine concurrently runs three avenues: dropping the sensitive trait, reweighting subgroups, and structurally resampling data. It automatically determines which method resulted in the largest fairness boost without crashing accuracy, and pushes the optimized result back to the user.

---

## 🛟 6. Troubleshooting

- **Server Connection Refused / "No Session Active"**: 
  Make sure your backend is up on port `8000`. The frontend will automatically detect session drops. If the backend is restarted, simply refresh the frontend and re-upload your CSV.
- **Firebase Error / Module Not Found on Startup**: 
  If you encounter `ModuleNotFoundError`, run `pip install -r requirements.txt` again inside the backend to ensure the Cloud integrations (`firebase-admin` and `google-cloud-aiplatform`) properly installed.
- **Gemini Fails to generate text**: Ensure the service account JSON path is physically correct inside `backend/.env` and that the *Vertex AI API* is explicitly enabled in your Google Cloud Dashboard. 
