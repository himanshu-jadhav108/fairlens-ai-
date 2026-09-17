# 8. Limitations & Threats to Validity

<!-- PROVISIONAL SCAFFOLD ONLY -->

## 8.1 Dataset Limitations & Historical Biases
- Tabular benchmarks (Adult, COMPAS, German Credit) encode historical societal biases and proxy measurement errors.
- Binarization of continuous sensitive attributes (e.g., age thresholds in German Credit) obscures non-linear disparities.

## 8.2 Scope Limitations
- Focus restricted to binary tabular classification; results may not generalize to computer vision, speech, or LLMs.

## 8.3 Statistical Limitations
- Five random seeds capture split sensitivity, not independent sampling observations.
- Sample sizes within intersectional subgroups are limited in smaller benchmarks.
