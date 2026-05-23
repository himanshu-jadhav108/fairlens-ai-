import json
from typing import List, Dict, Any

BIAS_EXPLANATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "explanation": {
            "type": "string",
            "description": "A detailed Markdown-formatted string explaining the bias, root causes, and suggested mitigation."
        },
        "summary": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "description": "Overall verdict. Either 'fair' or 'biased'."
                },
                "dpd_severity": {
                    "type": "string",
                    "description": "Severity of Demographic Parity Difference: 'low', 'moderate', or 'high'."
                },
                "eod_severity": {
                    "type": "string",
                    "description": "Severity of Equalized Odds Difference: 'low', 'moderate', or 'high'."
                },
                "di_severity": {
                    "type": "string",
                    "description": "Severity of Disparate Impact (e.g., 'low' if >0.8, 'high' if <0.8)."
                }
            },
            "required": ["verdict", "dpd_severity", "eod_severity"]
        }
    },
    "required": ["explanation", "summary"]
}

def build_bias_explanation_prompt(metrics: Dict[str, Any], shap_data: Dict[str, Any]) -> str:
    """
    Constructs the prompt sent to Gemini with full metric and SHAP context.
    """
    # We dump the group stats nicely formatted
    group_stats = metrics.get('group_stats', [])
    group_stats_str = json.dumps(group_stats, indent=2) if group_stats else "None"
    
    # Extract SHAP insights
    global_shap = shap_data.get('global_importance', [])
    top_global = [f["feature"] for f in global_shap[:5]] if global_shap else []
    
    demographic_shap = shap_data.get('demographic_analysis', {})
    top_disparities = demographic_shap.get('top_disparities', [])
    
    shap_context = f"""
Top Influential Features Globally:
{', '.join(top_global) if top_global else 'None available'}

Feature Disparities (Features that impact demographic groups differently):
{json.dumps(top_disparities, indent=2) if top_disparities else 'None available'}
"""
    
    return f"""
You are an expert AI fairness auditor. Analyze the following comprehensive model metrics and feature importances.
Explain the bias clearly, identify potential root causes using the Feature Disparities, and suggest mitigation strategies.

Model Metrics:
- Accuracy: {metrics.get('accuracy', 0) * 100:.1f}%
- Demographic Parity Difference (DPD): {metrics.get('demographic_parity_difference', 0):.4f}
- Equalized Odds Difference (EOD): {metrics.get('equalized_odds_difference', 0):.4f}
- Equal Opportunity Difference (TPR Diff): {metrics.get('equal_opportunity_difference', 0):.4f}
- Disparate Impact Ratio (80% Rule): {metrics.get('disparate_impact_ratio', 0):.4f}
- False Positive Rate Difference: {metrics.get('false_positive_rate_difference', 0):.4f}
- False Negative Rate Difference: {metrics.get('false_negative_rate_difference', 0):.4f}

Group Level Stats (Confusion Matrix & Accuracies):
{group_stats_str}

{shap_context}

Please generate a detailed explanation. Be professional, analytical, and write in Markdown.
"""
