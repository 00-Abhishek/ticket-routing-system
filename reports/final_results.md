# Final Results Summary

## Dataset

- Dataset: `data/all_tickets_processed_improved_v3.csv`
- Rows: 47,837
- Classes: 8
- Split: stratified 80% train, 10% validation, 10% test

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Naive Bayes | 0.7795 | 0.8802 | 0.6814 | 0.7336 |
| Logistic Regression | 0.8616 | 0.8507 | 0.8762 | 0.8622 |
| DistilBERT | 0.8878 | 0.8922 | 0.8847 | 0.8883 |

## Final Model Recommendation

DistilBERT is the recommended final model for the project because it achieved the strongest test performance:

- Accuracy: 0.8878
- Macro Precision: 0.8922
- Macro Recall: 0.8847
- Macro F1: 0.8883

## System Components Completed

- EDA report and charts
- Baseline model training and metrics
- DistilBERT training and metrics
- Rule-based NER
- Rule-based priority assignment
- Routing engine
- FastAPI backend
- Streamlit dashboard
- SQLite persistence
- Docker deployment files
- Final integration tests

