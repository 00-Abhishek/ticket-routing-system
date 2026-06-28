# Phase 1 EDA Report

## Dataset

- Path: `D:\DEVELOPMENT\CODEx_PROJECTS\ticket-routing-system\data\all_tickets_processed_improved_v3.csv`
- Rows: 47,837
- Columns: 2
- Target column: `Topic_group`
- Text column: `Document`

## Data Quality

- Duplicate rows: 0
- Missing documents: 0
- Missing labels: 0
- Rows containing URLs: 0
- Rows containing emails: 0
- Rows containing numbers: 0
- Very short rows under 3 words: 14

## Class Distribution

- Number of classes: 8
- Smallest class size: 1,760
- Largest class size: 13,617
- Imbalance ratio: 7.7369

| Topic_group | ticket_count | percentage |
| --- | --- | --- |
| Hardware | 13617 | 28.47 |
| HR Support | 10915 | 22.82 |
| Access | 7125 | 14.89 |
| Miscellaneous | 7060 | 14.76 |
| Storage | 2777 | 5.81 |
| Purchase | 2464 | 5.15 |
| Internal Project | 2119 | 4.43 |
| Administrative rights | 1760 | 3.68 |

## Ticket Length

- Average raw character length: 291.88
- Median raw character length: 175.00
- Average cleaned character length: 291.87
- Median cleaned character length: 175.00
- Average word count: 43.60
- Median word count: 26.00

| percentile | word_count |
| --- | --- |
| 0.25 | 17.0 |
| 0.5 | 26.0 |
| 0.75 | 46.0 |
| 0.9 | 91.0 |
| 0.95 | 136.0 |
| 0.99 | 284.0 |

## Preprocessing Pipeline

The preprocessing pipeline in `src/preprocessing/text.py` performs:

- Unicode normalization
- Lowercasing
- URL removal
- Email removal
- Control character normalization
- Technical-token-friendly character filtering
- Whitespace normalization

## Recommendations

- Class imbalance is meaningful; use stratified splits, macro-F1, weighted-F1, and class weights where supported.
- Very short tickets exist; keep a minimum-text validation step before model inference.
- Ticket length is sufficient for contextual models; cap transformer max length after reviewing percentiles.
- Use DistilBERT as the final model and keep TF-IDF baselines for comparison.

## Generated Artifacts

- `class_distribution.csv`
- `class_distribution.png`
- `ticket_word_count_distribution.png`
- `ticket_clean_length_distribution.png`
- `text_quality_signals.png`
- `sample_tickets_by_class.csv`
- `preprocessed_ticket_preview.csv`
- `dataset_profile.json`
