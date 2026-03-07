# Machine Learning Pipeline

## Objective

The machine learning pipeline is designed to demonstrate how structured resume and activity data can be transformed into meaningful predictions using a **reproducible, production-style workflow**.

The current implementation focuses on predicting a simple, interpretable target:
> **Estimated probability of obtaining a Junior ML / Analytics role within a defined time horizon (e.g., 6 months)**

The emphasis is on **pipeline design and integration**, not on claiming predictive certainty.

---

## High-Level Pipeline Stages

1. Feature generation
2. Model training
3. Experiment tracking
4. Model persistence
5. Inference and application integration

Each stage is modular and independently testable.

---

## 1. Feature Pipeline

### Inputs
Features are derived from the structured data model described in `data_model.md`, including:

- Experience history
- Education level
- Skills and proficiency scores
- Project count and recency
- Recent activity indicators (optional)

### Feature Engineering

Key engineered features include:

| Feature Name | Description |
|--------------|------------|
| total_experience_years | Aggregate experience duration |
| total_projects | Number of completed projects |
| avg_skill_score | Mean proficiency across skills |
| has_ml_projects | Binary indicator |
| education_level_encoded | Ordinal encoding of education |
| recent_activity_score | Weighted engagement indicator |

### Pipeline Characteristics

- Implemented as a **batch feature pipeline**
- Deterministic and repeatable
- Produces a single feature table (`ml_features_user`)
- Designed to be re-run without side effects

---

## 2. Model Training

### Model Type

- Scikit-learn based model
- Simple, interpretable algorithms (e.g., Logistic Regression, Random Forest)

The choice prioritizes:
- Transparency
- Explainability
- Stable behavior over small datasets

### Training Flow

1. Load feature table
2. Perform train/validation split
3. Train model
4. Evaluate using standard metrics
5. Persist model artifacts

### Evaluation Metrics

- Accuracy
- Precision / Recall
- ROC-AUC (where applicable)

Metrics are used internally to assess stability, not as performance claims.

---

## 3. Experiment Tracking

### Tooling

- **MLflow** (local tracking)

### Tracked Artifacts

- Model parameters
- Feature version hash
- Evaluation metrics
- Training timestamp

This ensures:
- Reproducibility
- Comparison between experiments
- Clear lineage from data → model

---

## 4. Model Persistence

### Storage

- Serialized model stored as an artifact
- Versioned using timestamp or hash
- Loaded dynamically during inference

### Contract

The model expects input data that conforms exactly to the feature schema produced by the feature pipeline.

This enforces a **feature contract** between training and inference.

---

## 5. Inference Pipeline

### Prediction Flow

1. User opens the "Career Prediction" view
2. Latest feature vector is loaded
3. Model generates probability score
4. Result is displayed with contextual explanation

### Output Example

- Probability score (0–1)
- Confidence band or qualitative interpretation
- Supporting factors (derived from features)

The output is designed to be:
- Understandable by non-technical users
- Transparent about its limitations

---

## Integration with Application

The ML pipeline is integrated directly into the Streamlit application:

- No offline notebooks required
- No manual feature manipulation
- Single source of truth for features and models

This ensures the model is a **functional part of the system**, not a disconnected experiment.

---

## Limitations and Scope

This pipeline intentionally avoids:

- Overfitting claims
- Large-scale model complexity
- Automated retraining

The goal is to demonstrate **correct system design**, not to simulate a production ML team or claim predictive authority.

---

## Why This Pipeline Matters

- Demonstrates understanding of ML lifecycle, not just algorithms
- Shows clean separation of data, features, model, and inference
- Mirrors how ML systems are typically deployed in real products
- Easily extensible to additional targets or models

---

## Summary

The machine learning pipeline is designed as a **first-class system component**, following industry-standard practices for feature engineering, training, tracking, and inference.

It emphasizes clarity, reproducibility, and integration—key requirements for real-world ML systems.
