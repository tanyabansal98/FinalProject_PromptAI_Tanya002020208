# Model Evaluation Metrics
## Classification
- Accuracy: correct/total (misleading with imbalanced data)
- Precision: TP/(TP+FP) — how many predicted positives are correct
- Recall: TP/(TP+FN) — how many actual positives are found
- F1: harmonic mean of precision and recall
- AUC-ROC: model's ability to distinguish classes
## Regression
- MSE: mean squared error (penalizes large errors)
- MAE: mean absolute error (more robust to outliers)
- R²: proportion of variance explained
## Common misconceptions
- High accuracy doesn't mean good model (check for class imbalance)
- Always use multiple metrics
