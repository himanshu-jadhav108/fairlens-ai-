<div align="center">
  <img src="frontend/public/fairlens-logo.png" alt="FairLens AI Logo" width="120" height="120" />

  <h1>FairLens AI ⚖️</h1>
  
  <p><strong>AI-Powered Fairness Auditing, Explainability, and Bias Mitigation Platform</strong></p>

  <p>
    <em>Empowering developers, students, researchers, and organizations to build responsible, unbiased machine learning systems.</em>
  </p>

  <h3>🥉 3rd Prize Winner – HackNova Online Challenge 2026</h3>

  <!-- Badges Section -->
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
    <img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI" />
    <img src="https://img.shields.io/badge/Fairlearn-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="Fairlearn" />
    <img src="https://img.shields.io/badge/SHAP-FF6F00?style=for-the-badge&logo=python&logoColor=white" alt="SHAP" />
    <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="MIT License" />
    <img src="https://img.shields.io/badge/🏆_Hackathon-Winner-gold?style=for-the-badge" alt="Hackathon Winner" />
  </p>
</div>

---

## 🛑 The Problem Statement

In the era of ubiquitous Artificial Intelligence, models are increasingly making decisions that impact human lives—from loan approvals and hiring to criminal justice and healthcare. However, AI is not inherently neutral. Machine learning systems often inherit, amplify, and perpetuate historical biases present in their training data.

Without proper auditing, biased AI can lead to discriminatory outcomes, legal liabilities, and erosion of public trust. The challenge developers face is that detecting and mitigating these biases often requires specialized knowledge, complex mathematical formulations, and convoluted workflows.

## 💡 Why FairLens AI?

FairLens AI was built to democratize **Responsible AI**. It bridges the gap between complex fairness mathematics and practical engineering.

We provide an intuitive, end-to-end platform that allows anyone—from a solo developer to an enterprise data science team—to:

1. **Audit** models for discriminatory behavior across demographic groups.
2. **Understand** the root causes of model decisions using state-of-the-art explainability (XAI) and Gemini AI insights.
3. **Mitigate** detected bias using automated multi-strategy algorithms, ensuring equitable outcomes.

## ✨ Key Features

| Feature                           | Description                                                                                                                   |
| :-------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| 📊 **Automated Fairness Audits**  | Upload your CSV dataset to instantly identify biased outcomes across sensitive attributes (race, gender, age).               |
| ⚖️ **Comprehensive Bias Metrics** | Calculates standard fairness metrics including Demographic Parity, Equalized Odds, and Disparate Impact Ratio.              |
| 🧠 **SHAP Explainability**        | Dive deep into model decisions with SHAP (SHapley Additive exPlanations) to reveal exact feature contributions to bias.       |
| 🤖 **Gemini AI Natural Language** | Get instant, plain-English executive summaries and actionable recommendations powered by Google Gemini 2.5 Flash.              |
| 🛠️ **Multi-Strategy Mitigation**  | Automatically apply Pre-processing (CorrelationRemover), In-processing (ExponentiatedGradient), and Post-processing (ThresholdOptimizer). |
| 📈 **Interactive Dashboards**     | Visualize complex fairness metrics through responsive React/Recharts charts and side-by-side comparisons.                      |
| 📄 **PDF & CSV Export**           | Export audit reports as clean PDFs or download the mitigated fair dataset for downstream production use.                       |
| 📂 **Instant Demo Datasets**      | Get started immediately with pre-loaded datasets (Adult Census Income, COMPAS recidivism).                                    |

## 🏗️ Architecture Overview

The system uses a decoupled architecture designed for deployment on 100% free cloud hosting.

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#61DAFB,stroke:#333,stroke-width:2px,color:#000;
    classDef backend fill:#009688,stroke:#333,stroke-width:2px,color:#fff;
    classDef ml fill:#FF6F00,stroke:#333,stroke-width:2px,color:#fff;
    classDef db fill:#FFCA28,stroke:#333,stroke-width:2px,color:#000;
    
    subgraph "Frontend Layer (Vercel)"
        UI_Upload("📤 Dataset Upload & Demo"):::frontend
        UI_Dash("📊 Bias Dashboard & XAI"):::frontend
        UI_Report("📄 PDF Reports & Downloads"):::frontend
    end

    subgraph "Backend Layer (Render FastAPI)"
        API("⚡ API Gateway"):::backend
        DP("⚙️ Data Processing Engine"):::backend
        
        subgraph "Machine Learning Core"
            FE("⚖️ Fairness Engine (Fairlearn)"):::ml
            XE("🧠 Explainability Engine (SHAP)"):::ml
            ME("🛠️ Multi-Strategy Mitigation Engine"):::ml
            GAI("🤖 Gemini 2.5 Flash Service"):::ml
        end
    end

    subgraph "Data & Authentication Layer"
        DB[("🔥 Firebase Firestore")]:::db
        Auth("🔐 Firebase Authentication"):::db
    end

    %% Flow of data
    UI_Upload -- "CSV Dataset" --> API
    API -- "Processed Features" --> DP
    DP -- "Feature Matrix" --> FE
    DP -- "Feature Matrix" --> XE
    
    FE -- "Disparity Metrics" --> UI_Dash
    XE -- "SHAP Values" --> UI_Dash
    FE & XE -- "Metrics & SHAP Summary" --> GAI
    GAI -- "Natural Language AI Report" --> UI_Dash
    
    FE -- "High Disparity" --> ME
    ME -- "Fair Predictions" --> UI_Report
    
    %% Storage Interactions
    API <-- "Save Audit History" --> DB
    UI_Upload <-- "Verify User" --> Auth
```

## ⚙️ AI Pipeline: How It Works

1. **Ingestion:** Users upload a dataset (CSV) or load demo data, specifying target and sensitive attributes.
2. **Processing:** Pandas and Scikit-Learn clean data, encode categorical variables, and train a baseline model.
3. **Auditing:** The Fairness Engine calculates disparity metrics across sensitive groups.
4. **Explainability:** The SHAP engine calculates feature importances to reveal drivers of bias.
5. **AI Summarization:** Gemini 2.5 Flash analyzes metrics and generates an executive summary with mitigation recommendations.
6. **Mitigation:** The Multi-Strategy Engine evaluates CorrelationRemover, ExponentiatedGradient, and ThresholdOptimizer to select the optimal fairness/accuracy tradeoff.
7. **Export & Persistence:** Reports can be exported to PDF, mitigated datasets downloaded as CSV, and audit sessions saved to Firebase Firestore.

## 🎥 Project Preview

<div align="center">
  <video src="Public/Videos/Fairlens-AI-Preview.mp4" controls="controls" muted="muted" width="800"></video>
  <br/>
  <i>(If the video doesn't load, you can view it on <a href="https://drive.google.com/file/d/1eroNN4jK3YIyA6n6CxAcboKqtZSCM-HE/view?usp=drive_link">Google Drive</a> or <a href="Public/Videos/Fairlens-AI-Preview.mp4">download it here</a>)</i>
</div>

## 📸 Screenshots

|                                           Bias Detection Dashboard                                           |                                             AI Bias Explanation                                             |
| :----------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------: |
| <img src="Public/Screenshots/Bias-Detection.png" alt="Bias Detection Dashboard"> | <img src="Public/Screenshots/AI-Bias-Explaination.png" alt="AI Bias Explanation"> |
|                            _High-level overview of model fairness health._                             |                       _Deep dive into feature contributions driving the bias._                       |

|                                         Mitigation Results & Fixes                                          |                                          Fairness Report Summary                                          |
| :------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: |
| <img src="Public/Screenshots/Bias-Mitigation-Fix.png" alt="Bias Mitigation Fix"> | <img src="Public/Screenshots/Report.png" alt="Fairness Report"> |
|                    _Comparing fairness metrics before and after mitigation._                     |                      _Comprehensive audit report for compliance._                       |

## 🚀 Live Production Deployment

FairLens AI is configured for 100% free production deployment using **Vercel** (Frontend) and **Render** (Backend).

- 🌐 **Live Frontend (Vercel):** `https://fairlens-ai-nine.vercel.app/`
- ⚡ **Live Backend API (Render):** `https://fairlens-ai-backend-skog.onrender.com`
- 💚 **API Health Check:** `https://fairlens-ai-backend-skog.onrender.com/health`
- 🎯 **API Ready Check:** `https://fairlens-ai-backend-skog.onrender.com/ready`

For step-by-step deployment guide on free hosting platforms, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## 💻 Tech Stack

| Category              | Technologies                                               |
| :-------------------- | :--------------------------------------------------------- |
| **Frontend**          | React 18, TypeScript, Vite, Tailwind CSS, Shadcn UI, Recharts |
| **Backend**           | FastAPI, Uvicorn, Python 3.10                              |
| **Data Science & ML** | Pandas, Scikit-Learn, NumPy                                |
| **Responsible AI**    | Fairlearn, SHAP                                            |
| **Generative AI**     | Google Gemini 2.5 Flash API (Tenacity Retry + Fallback)    |
| **Database & Auth**   | Firebase Firestore, Firebase Authentication                |

## 📁 Project Structure

```text
fairlens-ai/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # RESTful router endpoints
│   │   ├── core/             # Settings, CORS, security, JWT auth
│   │   ├── db/               # Database session & models
│   │   ├── ml/               # Fairness, SHAP, and Mitigation engines
│   │   ├── routes/           # Upload, analyze, explain, fix, history
│   │   └── services/         # Firebase Admin & Gemini AI services
│   ├── requirements.txt      # Python dependencies
│   ├── render.yaml           # Render deployment configuration
│   └── runtime.txt           # Python 3.10.12 runtime specification
├── frontend/                 # React + Vite Application
│   ├── src/
│   │   ├── components/       # UI components (Detect, Explain, Fix, Report)
│   │   ├── context/          # AppContext state management
│   │   ├── lib/              # API client, PDF exporter, Firebase client
│   │   ├── pages/            # Index, History, Login, Register
│   │   └── types/            # TypeScript data contracts
│   ├── package.json          # Node dependencies
│   ├── vercel.json           # Vercel SPA rewrite configuration
│   └── vite.config.ts        # Vite build configuration
└── README.md                 # Project documentation
```

## 🛠️ Installation Guide

Follow these steps to run FairLens AI locally on your machine.

### Prerequisites

- Node.js (v18+)
- Python (3.10+)
- Firebase Project credentials (optional for local dev)

### 1. Clone the Repository

```bash
git clone https://github.com/himanshu-jadhav108/fairlens-ai-.git
cd fairlens-ai-
```

### 2. Setup the Backend

```bash
cd backend
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
```

_The backend API will be available at `http://localhost:8000`_

### 3. Setup the Frontend

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

_The frontend application will be available at `http://localhost:5173`_

## 📖 Usage Guide & Example Workflow

1. **Sign In / Guest Mode:** Launch the application and select a demo dataset to start immediately without uploading data.
2. **Configure Audit:** Select the sensitive attributes you want to audit for (e.g., `gender`, `race`).
3. **Run Audit:** Click "Run Fairness Audit". The backend will process the data and return the fairness metrics.
4. **Analyze Results:** Review the dashboard. Are the Disparate Impact scores below the industry standard of 0.8? Which features are highlighted by SHAP as heavily influencing the bias?
5. **Mitigate:** Navigate to the Mitigation tab. Select a mitigation strategy (e.g., Correlation Remover or Threshold Optimization).
6. **Compare:** View the "Before vs. After" comparison to see how the fairness metrics improved and how model accuracy was affected.

## 🏆 Hackathon Journey

**HackNova Online Challenge 2026**

FairLens AI was conceptualized, designed, and fully developed by a solo developer over a rigorous one-week period for the HackNova Online Challenge.

- **May 17, 2026:** Initial idea submission focusing on the critical need for accessible AI auditing tools.
- **May 20, 2026:** Selected for the Top 30 Development Phase from a highly competitive pool of applicants.
- **May 21–23, 2026:** 72-hour intensive development sprint. Architected the FastAPI backend, integrated Fairlearn/SHAP, built the React frontend, and connected Firebase.
- **May 24, 2026:** Final presentation and evaluation.
- **Result:** 🥉 Awarded **3rd Prize** overall!

## 🚧 Challenges Faced

Building a comprehensive ML platform in 72 hours presented several unique challenges:

- **Mathematical Complexity:** Translating dense fairness mathematics from `Fairlearn` into intuitive, actionable UI components that non-experts can understand.
- **Performance:** Calculating SHAP values for large datasets is computationally expensive. Optimized the backend to sample data appropriately to ensure the API responds in real-time without timing out.
- **State Management:** Managing complex, multi-step ML workflows (Upload -> Audit -> Explain -> Mitigate) seamlessly on the frontend.

## 🗺️ Future Roadmap

FairLens AI is evolving from a hackathon prototype into a robust open-source platform.

### Phase 1: Core Enhancements (Completed)

- [x] Export reports as PDF/CSV.
- [x] Gemini AI-Powered natural language bias explanations.
- [x] Enterprise Firebase Auth & Firestore session tracking.

### Phase 2: Advanced Intelligence

- [ ] **Multi-Model Benchmarking:** Compare the fairness of multiple models side-by-side.
- [ ] **Automated Report Generation:** Schedule automated periodic audits.

### Phase 3: Enterprise Scale

- [ ] **Dataset Drift Monitoring:** Continuous monitoring of data streams for emergent biases over time.
- [ ] **Responsible AI Assistant:** Conversational agent to guide users through the auditing process.
- [ ] **Enterprise Analytics:** Organizational dashboards for compliance tracking.

## 🌍 Impact

FairLens AI is designed to benefit the entire AI ecosystem:

- 🎓 **Students & Educators:** A practical tool to learn and teach the concepts of AI fairness and ethics.
- 🔬 **Researchers:** A visual platform to quickly experiment with and benchmark different bias mitigation techniques.
- 👨‍💻 **Data Scientists:** A streamlined workflow to audit models before deploying them to production.
- 🚀 **Startups & Enterprises:** A compliance tool to ensure AI systems align with ethical guidelines and emerging regulations (e.g., EU AI Act).

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <i>Built with ❤️ for a fairer, more transparent AI future.</i>
</div>
