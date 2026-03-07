# Data Model Overview

## Purpose
The data model defines how resume, activity, and derived feature data is structured and stored within the system.  
It is designed to support **analytics, machine learning, and application consumption** in a consistent and scalable manner.

Rather than treating the resume as static text, the system models it as **structured, queryable data**.

---

## Design Principles

- Relational, schema-driven structure
- Clear separation between raw entities and derived data
- Readability and transparency over unnecessary abstraction
- Designed to support analytics and ML use cases from day one

---

## Core Entities

### 1. Profile

Stores high-level personal and professional metadata.

**Table:** `profile`

| Column         | Type        | Description                          |
|---------------|------------|--------------------------------------|
| id            | UUID / INT | Primary identifier                   |
| full_name     | TEXT       | Full name                            |
| title         | TEXT       | Professional headline                |
| location      | TEXT       | Current location                     |
| summary       | TEXT       | Professional summary                 |
| created_at    | TIMESTAMP  | Record creation timestamp            |

---

### 2. Experience

Represents professional experience entries in a structured format.

**Table:** `experience`

| Column         | Type        | Description                          |
|---------------|------------|--------------------------------------|
| id            | UUID / INT | Primary identifier                   |
| role          | TEXT       | Job title                            |
| company       | TEXT       | Employer name                        |
| location      | TEXT       | Job location                         |
| start_date    | DATE       | Role start date                     |
| end_date      | DATE / NULL| Role end date (NULL if ongoing)     |
| description   | TEXT       | Role responsibilities and impact     |

**Notes**
- Enables timeline visualizations
- Supports duration-based feature engineering
- Queryable for analytics (e.g., total experience)

---

### 3. Education

Stores formal education records.

**Table:** `education`

| Column         | Type        | Description                          |
|---------------|------------|--------------------------------------|
| id            | UUID / INT | Primary identifier                   |
| degree        | TEXT       | Degree name                          |
| institution   | TEXT       | Institution name                     |
| location      | TEXT       | Institution location                 |
| start_date    | DATE       | Study start date                     |
| end_date      | DATE / NULL| Completion date or NULL if ongoing   |

---

### 4. Skills

Normalized representation of technical and professional skills.

**Table:** `skills`

| Column         | Type        | Description                          |
|---------------|------------|--------------------------------------|
| id            | UUID / INT | Primary identifier                   |
| skill_name    | TEXT       | Skill name                           |
| proficiency   | INT        | Self-assessed level (0–100)          |
| category      | TEXT       | Skill category (optional)            |

**Usage**
- Rendered as progress indicators in the UI
- Used directly as model features

---

### 5. Projects

Represents personal or professional projects.

**Table:** `projects`

| Column         | Type        | Description                          |
|---------------|------------|--------------------------------------|
| id            | UUID / INT | Primary identifier                   |
| title         | TEXT       | Project title                        |
| description   | TEXT       | Short project summary                |
| github_url    | TEXT       | Source code link                     |
| tags          | TEXT[]     | Technologies or themes               |

---

## Derived & Analytics Tables

### 6. Feature Table (ML)

Aggregated and engineered features used for model training and inference.

**Table:** `ml_features_user`

| Column                        | Type   | Description                          |
|------------------------------|--------|--------------------------------------|
| total_experience_years       | FLOAT  | Calculated from experience records   |
| total_projects               | INT    | Project count                        |
| avg_skill_score              | FLOAT  | Average skill proficiency            |
| recent_activity_score        | FLOAT  | Weighted activity indicator          |
| education_level_encoded      | INT    | Encoded education level              |

**Notes**
- Generated via batch pipelines
- Not manually edited
- Treated as a model input contract

---

## Relationships Summary

- `profile` → 1:N → `experience`
- `profile` → 1:N → `education`
- `profile` → 1:N → `skills`
- `profile` → 1:N → `projects`
- Aggregations → `ml_features_user`

---

## Data Flow

1. Raw resume data is stored in normalized tables
2. Analytics queries read directly from core entities
3. Feature pipelines aggregate data into ML-ready feature tables
4. Application layer consumes both raw and derived data

This separation ensures clarity, traceability, and reproducibility.

---

## Why This Data Model Matters

- Enables timeline and analytics visualizations
- Supports ML pipelines without rework
- Keeps resume data consistent across UI, analytics, and AI components
- Mirrors how enterprise data products are typically structured

---

## Summary

The data model treats resume information as a **first-class data asset**.  
It is intentionally designed to be usable by data engineers, analysts, and ML systems—rather than serving only as UI input.

This foundation allows the system to scale beyond a resume into a full analytics and intelligence platform.
