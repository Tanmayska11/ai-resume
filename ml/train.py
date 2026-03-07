# ml/train.py

import random
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

from ml.matching.feature_builder import build_features


MODEL_DIR = Path("ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "resume_match_xgb.pkl"


# ===============================
# Synthetic Data Generator
# ===============================

SKILL_POOL = [
    "python", "sql", "postgresql", "databricks", "aws",
    "machine learning", "streamlit", "docker", "fastapi",
    "pandas", "numpy", "spark"
]

DEGREES = [
    "msc data science",
    "bsc computer science",
    "msc business analytics",
    "bsc mechanical engineering",
    None
]


def generate_resume() -> Dict[str, Any]:
    skills = random.sample(SKILL_POOL, random.randint(4, 8))

    return {
        "profile": {
            "summary": "Experienced data professional"
        },
        "skills": [
            {"name": s, "category": "technical", "level": random.randint(2, 5)}
            for s in skills
        ],
        "experience": {
            "total_years": round(random.uniform(0, 6), 2),
            "roles": ["Data Engineer", "Backend Developer"],
            "tools": skills[:3],
            "domains": ["Data", "Engineering"]
        },
        "projects": {
            "count": random.randint(1, 6),
            "technologies": skills[:4],
            "types": ["Personal"],
            "outcomes": ["Dashboard"]
        },
        "education": {
            "degrees": [random.choice(DEGREES)] if random.random() > 0.2 else []
        },
        "certifications": [],
        "languages": []
    }


def generate_job_description(required_skills: List[str]) -> str:
    text = (
        "We are looking for a candidate with experience in "
        + ", ".join(required_skills)
        + ". Experience with data pipelines and backend systems is a plus."
    )
    return text


# ===============================
# Labeling Logic (Transparent)
# ===============================

def assign_label(features: Dict[str, Any]) -> int:
    """
    Weak but defensible labeling rule.
    """

    if (
        features["skill_match_ratio"] >= 0.5
        and features["total_experience_years"] >= 1.0
    ):
        return 1
    return 0


# ===============================
# Training Pipeline
# ===============================

def build_dataset(n_samples: int = 1000):
    X = []
    y = []

    for _ in range(n_samples):
        resume = generate_resume()
        jd_skills = random.sample(SKILL_POOL, random.randint(3, 6))
        jd_text = generate_job_description(jd_skills)

        features = build_features(resume, jd_text)

        X.append([
            features["skill_match_ratio"],
            features["total_experience_years"],
            int(features["has_relevant_degree"]),
            len(features["matched_skills"]),
            len(features["missing_skills"]),
        ])

        y.append(assign_label(features))

    return np.array(X), np.array(y)


def train():
    print("🔧 Building dataset...")
    X, y = build_dataset(n_samples=1500)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("🚀 Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )

    model.fit(X_train, y_train)

    val_probs = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, val_probs)

    print(f"✅ Validation ROC-AUC: {auc:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
