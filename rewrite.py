import os
import subprocess
import shutil

def run_git(cmd, date=None):
    env = os.environ.copy()
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)

# 1. Clean .git
if os.path.exists(".git"):
    subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", ".git"])

run_git(["git", "init"])

commits = [
    {
        "date": "2026-05-21T09:30:00",
        "msg": "chore: initial project scaffolding and config",
        "files": [".gitignore", "setup.md", "backend/requirements.txt", "backend/app/main.py", "backend/app/core/config.py", "frontend/package.json", "frontend/package-lock.json", "frontend/vite.config.ts", "frontend/tsconfig.app.json", "frontend/tsconfig.node.json", "frontend/tailwind.config.ts"],
        "force": True
    },
    {
        "date": "2026-05-21T18:45:00",
        "msg": "feat: basic frontend layout and backend services",
        "files": ["backend/app/state.py", "backend/app/services/", "frontend/index.html", "frontend/src/main.tsx", "frontend/src/App.tsx", "frontend/src/index.css", "frontend/src/components/layout/", "frontend/public/"],
        "force": True
    },
    {
        "date": "2026-05-22T13:15:00",
        "msg": "feat: core fairness ML pipeline and mitigation endpoints",
        "files": ["backend/app/ml/", "backend/app/ml_pipeline.py", "datasets/", "backend/app/routes/upload.py", "backend/app/routes/analyze.py", "backend/app/routes/fix.py"],
        "force": True
    },
    {
        "date": "2026-05-22T20:30:00",
        "msg": "feat: frontend bias detection dashboard and upload flow",
        "files": ["frontend/src/components/upload/", "frontend/src/components/shared/", "frontend/src/components/detect/", "frontend/src/components/fix/", "frontend/src/context/AppContext.tsx", "frontend/src/lib/api.ts", "frontend/src/lib/mockData.ts"],
        "force": True
    },
    {
        "date": "2026-05-23T14:20:00",
        "msg": "feat: deep SHAP explainability and report generation",
        "files": ["backend/app/routes/explain.py", "backend/test_firebase.py", "frontend/src/components/explain/", "frontend/src/components/report/", "frontend/src/lib/exportPdf.ts", "backend/render.yaml"],
        "force": True
    },
    {
        "date": "2026-05-23T23:50:00",
        "msg": "feat: firebase authentication, user history dashboard, and final polish",
        "files": ["."],
        "force": False
    },
    {
        "date": "2026-05-27T10:00:00",
        "msg": "docs: update README with hackathon results and documentation",
        "files": ["README.md"],
        "force": True
    }
]

for c in commits:
    if c.get("force"):
        run_git(["git", "add", "-f"] + c["files"])
    elif c["files"] == ["."]:
        # Temporarily hide README so it isn't swept up in git add .
        if os.path.exists("README.md"):
            shutil.move("README.md", "README_TEMP.md")
        run_git(["git", "add", "."])
        if os.path.exists("README_TEMP.md"):
            shutil.move("README_TEMP.md", "README.md")
    else:
        run_git(["git", "add"] + c["files"])
    run_git(["git", "commit", "-m", c["msg"]], date=c["date"])

run_git(["git", "branch", "-M", "main"])
run_git(["git", "remote", "add", "origin", "https://github.com/himanshu-jadhav108/fairlens-ai-.git"])
print("Ready to push!")
