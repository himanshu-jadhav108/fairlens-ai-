# 9. Reproducibility Statement

## 9.1 Hardware & Environment Details
- OS: Windows 11 / Linux compatible
- Python Version: >= 3.10, <= 3.13
- Key Libraries: `scikit-learn==1.8.0`, `fairlearn==0.14.0`, `shap==0.50.0`, `xgboost==3.4.1`, `pandas==3.0.5`, `numpy==2.3.5`, `scipy==1.17.0`
- Pinned specifications in `research/requirements-research.txt`.

## 9.2 Code & Artifact Traceability
- Repository: `https://github.com/himanshu-jadhav108/fairlens-ai-`
- Branch: `research/fairness-xai-study`
- Traceability chain: `Paper Table/Figure` → `research/results/processed/summary_table.csv` → `research/results/raw/*.json` → `research/results/manifests/*.json` → `git_commit_hash`.

## 9.3 Exact Reproduction Commands
```bash
# Smoke test
python research/scripts/run_experiment.py --dataset adult --model logistic_regression --mitigation correlation_remover --seed 42 --smoke-test

# Batch runner
python research/scripts/run_matrix.py --smoke-test

# Result aggregation & figure generation
python research/scripts/aggregate_results.py
python research/scripts/generate_figures.py
```
