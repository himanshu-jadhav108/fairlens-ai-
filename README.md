# 👁️ FairLens AI

> **A Responsible AI platform to identify, understand, and mitigate bias in machine learning systems.**

**🏆 3rd Prize Winner - HackNova Online Challenge 2026**

FairLens AI was developed as a solo project during the HackNova Online Challenge between **21–23 May 2026**, and showcased during the final evaluation on **24 May 2026**.

---

## 📖 Project Overview

As machine learning systems increasingly influence critical decisions in healthcare, finance, and hiring, ensuring these models are fair and unbiased is paramount. **FairLens AI** provides an end-to-end, interactive platform that empowers data scientists and developers to audit their models for demographic bias, visualize the root causes using Explainable AI (XAI), and apply state-of-the-art mitigation algorithms to build more equitable systems.

## ✨ Features

- 📊 **Automated Fairness Audits**: Upload tabular datasets and instantly evaluate machine learning models for bias.
- 🎯 **Comprehensive Metrics**: Calculate Disparate Impact, Demographic Parity, and Equalized Odds across sensitive attributes (e.g., gender, age, race).
- 🧠 **SHAP-based Explainability**: Deep dive into global feature importance and localized demographic disparities using integrated SHAP values.
- 🔧 **Bias Mitigation Engine**: Automatically evaluate Pre-processing (Correlation Remover), In-processing (Exponentiated Gradient), and Post-processing (Threshold Optimizer) techniques to improve fairness scores.
- 📈 **Interactive Dashboards**: Generate beautiful, interactive reports and side-by-side comparisons of model fairness before and after mitigation.

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Shadcn UI, Recharts
- **Backend**: FastAPI, Python, Pandas, Scikit-Learn
- **Machine Learning & XAI**: Fairlearn, SHAP
- **Database & Auth**: Firebase Firestore, Firebase Authentication

## 🚀 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/himanshu-jadhav108/fairlens-ai-.git
cd fairlens-ai-
```

### 2. Backend Setup
Navigate to the backend directory, install the Python dependencies, and start the FastAPI server:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
# source venv/bin/activate    # On Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal, navigate to the frontend directory, install the Node packages, and start the Vite dev server:
```bash
cd frontend
npm install
npm run dev
```

### 4. Quick Start
1. Open your browser and navigate to `http://localhost:5173`.
2. Create an account or log in.
3. Use the **Upload Dataset** feature, or try the built-in **Demo Dataset** to instantly see a fairness audit in action!

## 🗓️ Hackathon Timeline

- **17 May 2026**: Idea submission (PPT pitch)
- **20 May 2026**: Top 30 teams announced
- **21–23 May 2026**: Core build phase (active development)
- **24 May 2026**: Project evaluation & live Zoom showcase

## 🎉 Acknowledgements

A special thank you to the **HackNova Startup Committee** for organizing an incredible event and fostering innovation in the AI space.

Awarded the **Certificate of Excellence** and secured the **3rd Prize** overall.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
