# Phase 2 Baseline Model Report

## Run Details

- Generated: 2026-08-03T13:14:15
- Dataset: `F:\ticket-routing-system\data\all_tickets_processed_improved_v3.csv`
- Random seed: 42
- Split strategy: stratified 80% train, 10% validation, 10% test
- Shared vectorizer: TF-IDF, unigram + bigram, max 50,000 features, sublinear TF

## Split Sizes

| Split | Rows |
| --- | --- |
| Train | 38269 |
| Validation | 4784 |
| Test | 4784 |

## Aggregate Metrics

| Model | Split | Accuracy | Precision Macro | Recall Macro | F1 Macro | Precision Weighted | Recall Weighted | F1 Weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-IDF + Logistic Regression | Validation | 0.8574 | 0.8469 | 0.8716 | 0.8575 | 0.8603 | 0.8574 | 0.8580 |
| TF-IDF + Logistic Regression | Test | 0.8616 | 0.8507 | 0.8762 | 0.8622 | 0.8638 | 0.8616 | 0.8620 |
| TF-IDF + Multinomial Naive Bayes | Validation | 0.7728 | 0.8763 | 0.6745 | 0.7321 | 0.8011 | 0.7728 | 0.7674 |
| TF-IDF + Multinomial Naive Bayes | Test | 0.7795 | 0.8802 | 0.6814 | 0.7336 | 0.8074 | 0.7795 | 0.7732 |

## TF-IDF + Logistic Regression Test Per-Class Metrics

| Class | Precision | Recall | F1 Score | Support |
| --- | --- | --- | --- | --- |
| Access | 0.8927 | 0.8864 | 0.8895 | 713 |
| Administrative rights | 0.7286 | 0.8239 | 0.7733 | 176 |
| HR Support | 0.8916 | 0.8515 | 0.8711 | 1091 |
| Hardware | 0.8654 | 0.8260 | 0.8452 | 1362 |
| Internal Project | 0.7886 | 0.9151 | 0.8472 | 212 |
| Miscellaneous | 0.8076 | 0.8739 | 0.8395 | 706 |
| Purchase | 0.9344 | 0.9231 | 0.9287 | 247 |
| Storage | 0.8968 | 0.9097 | 0.9032 | 277 |

## TF-IDF + Logistic Regression Test Confusion Matrix

| Actual \ Predicted | Access | Administrative rights | HR Support | Hardware | Internal Project | Miscellaneous | Purchase | Storage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Access | 632 | 9 | 15 | 26 | 7 | 19 | 2 | 3 |
| Administrative rights | 4 | 145 | 2 | 23 | 1 | 1 | 0 | 0 |
| HR Support | 24 | 5 | 929 | 61 | 19 | 42 | 1 | 10 |
| Hardware | 37 | 31 | 63 | 1125 | 13 | 71 | 13 | 9 |
| Internal Project | 0 | 1 | 3 | 10 | 194 | 3 | 0 | 1 |
| Miscellaneous | 11 | 4 | 20 | 37 | 11 | 617 | 0 | 6 |
| Purchase | 0 | 2 | 3 | 8 | 0 | 6 | 228 | 0 |
| Storage | 0 | 2 | 7 | 10 | 1 | 5 | 0 | 252 |

## TF-IDF + Multinomial Naive Bayes Test Per-Class Metrics

| Class | Precision | Recall | F1 Score | Support |
| --- | --- | --- | --- | --- |
| Access | 0.8652 | 0.7742 | 0.8172 | 713 |
| Administrative rights | 1.0000 | 0.2159 | 0.3551 | 176 |
| HR Support | 0.8153 | 0.8093 | 0.8123 | 1091 |
| Hardware | 0.6699 | 0.9148 | 0.7734 | 1362 |
| Internal Project | 0.9652 | 0.5236 | 0.6789 | 212 |
| Miscellaneous | 0.7865 | 0.7252 | 0.7546 | 706 |
| Purchase | 0.9720 | 0.8421 | 0.9024 | 247 |
| Storage | 0.9676 | 0.6462 | 0.7749 | 277 |

## TF-IDF + Multinomial Naive Bayes Test Confusion Matrix

| Actual \ Predicted | Access | Administrative rights | HR Support | Hardware | Internal Project | Miscellaneous | Purchase | Storage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Access | 552 | 0 | 35 | 99 | 2 | 24 | 0 | 1 |
| Administrative rights | 3 | 38 | 5 | 129 | 0 | 1 | 0 | 0 |
| HR Support | 27 | 0 | 883 | 146 | 0 | 31 | 0 | 4 |
| Hardware | 27 | 0 | 42 | 1246 | 2 | 39 | 6 | 0 |
| Internal Project | 8 | 0 | 36 | 31 | 111 | 26 | 0 | 0 |
| Miscellaneous | 14 | 0 | 52 | 127 | 0 | 512 | 0 | 1 |
| Purchase | 0 | 0 | 1 | 32 | 0 | 6 | 208 | 0 |
| Storage | 7 | 0 | 29 | 50 | 0 | 12 | 0 | 179 |

## Saved Artifacts

- `models/logistic_regression.pkl`
- `models/tfidf_vectorizer.pkl`
- `models/naive_bayes.pkl`
