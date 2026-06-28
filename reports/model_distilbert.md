# Phase 4 DistilBERT Model Report

## Run Details

- Generated: 2026-06-02T21:22:21
- Dataset: `D:\DEVELOPMENT\CODEx_PROJECTS\ticket-routing-system\data\all_tickets_processed_improved_v3.csv`
- Model: `distilbert-base-uncased`
- Saved model directory: `D:\DEVELOPMENT\CODEx_PROJECTS\ticket-routing-system\models\distilbert`
- Random seed: 42
- Split strategy: stratified 80% train, 10% validation, 10% test
- Device: NVIDIA GeForce RTX 4060 Ti
- Mixed precision: enabled
- Max length: 128
- Batch size: 16
- Epochs requested: 3
- Early stopping: enabled, monitored validation macro F1
- Checkpointing: enabled, best validation macro F1 restored

## Split Sizes

| Split | Rows |
| --- | --- |
| Train | 38269 |
| Validation | 4784 |
| Test | 4784 |

## Aggregate Metrics

| Split | Accuracy | Precision Macro | Recall Macro | F1 Macro | Precision Weighted | Recall Weighted | F1 Weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Validation | 0.8794 | 0.8820 | 0.8701 | 0.8757 | 0.8795 | 0.8794 | 0.8793 |
| Test | 0.8878 | 0.8922 | 0.8847 | 0.8883 | 0.8878 | 0.8878 | 0.8877 |

## Test Per-Class Metrics

| Class | Precision | Recall | F1 Score | Support |
| --- | --- | --- | --- | --- |
| Access | 0.9076 | 0.9369 | 0.9220 | 713 |
| Administrative rights | 0.8471 | 0.8182 | 0.8324 | 176 |
| HR Support | 0.9033 | 0.8909 | 0.8971 | 1091 |
| Hardware | 0.8776 | 0.8847 | 0.8812 | 1362 |
| Internal Project | 0.8846 | 0.8679 | 0.8762 | 212 |
| Miscellaneous | 0.8362 | 0.8385 | 0.8373 | 706 |
| Purchase | 0.9540 | 0.9231 | 0.9383 | 247 |
| Storage | 0.9270 | 0.9170 | 0.9220 | 277 |

## Test Confusion Matrix

| Actual \ Predicted | Access | Administrative rights | HR Support | Hardware | Internal Project | Miscellaneous | Purchase | Storage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Access | 668 | 1 | 13 | 19 | 1 | 8 | 0 | 3 |
| Administrative rights | 3 | 144 | 2 | 22 | 2 | 3 | 0 | 0 |
| HR Support | 17 | 2 | 972 | 46 | 6 | 36 | 3 | 9 |
| Hardware | 30 | 15 | 43 | 1205 | 7 | 52 | 7 | 3 |
| Internal Project | 2 | 1 | 8 | 7 | 184 | 9 | 0 | 1 |
| Miscellaneous | 15 | 3 | 28 | 55 | 8 | 592 | 1 | 4 |
| Purchase | 0 | 3 | 1 | 11 | 0 | 4 | 228 | 0 |
| Storage | 1 | 1 | 9 | 8 | 0 | 4 | 0 | 254 |

## Comparison With Phase 2 Baselines

| Model | Test Accuracy | Test Macro F1 | Test Weighted F1 |
| --- | --- | --- | --- |
| DistilBERT base uncased | 0.8878 | 0.8883 | 0.8877 |
| TF-IDF + Logistic Regression | 0.8616 | 0.8622 | 0.8620 |
| TF-IDF + Multinomial Naive Bayes | 0.7795 | 0.7336 | 0.7732 |

## Saved Artifacts

- `models/distilbert/`
- `models/distilbert/checkpoint-*`
- `models/distilbert/label_mapping.json`
