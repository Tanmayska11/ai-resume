# System Architecture Overview

## Purpose
This portfolio is designed as a **production-style resume system**, not a static personal website.  
It demonstrates how data engineering, analytics, machine learning, and application layers can be combined into an end-to-end system that resembles real-world enterprise projects.

The system is intentionally structured to reflect **industry-standard engineering practices**, including modular design, data pipelines, and deployable services.

---

## High-Level Architecture

The system is composed of five primary layers:

1. **Data Layer**
2. **Data Engineering & Feature Pipelines**
3. **Machine Learning Layer**
4. **Application Layer**
5. **Infrastructure & Deployment**

Each layer is loosely coupled and independently extensible.

---

## 1. Data Layer

**Primary Components**
- PostgreSQL (relational database)
- Structured resume and activity data

**Responsibilities**
- Store normalized resume data (education, experience, skills, projects)
- Persist intermediate and processed datasets
- Act as a single source of truth for analytics and ML features

**Design Considerations**
- Schema-first design
- Separation between raw data and derived features
- SQL-first approach for transparency and auditability

---

## 2. Data Engineering & Feature Pipelines

**Technologies**
- Python
- SQL
- ETL-style batch pipelines

**Responsibilities**
- Extract structured resume and activity data
- Transform raw inputs into clean, analytics-ready datasets
- Generate feature tables used by ML models

**Pipeline Characteristics**
- Batch-oriented processing
- Deterministic transformations
- Explicit feature definitions
- Reusable feature logic across models

This layer mirrors how production analytics pipelines are typically built in enterprise environments.

---

## 3. Machine Learning Layer

**Technologies**
- scikit-learn
- MLflow (experiment tracking)

**Responsibilities**
- Train predictive models on engineered features
- Track experiments, parameters, and metrics
- Produce versioned model artifacts

**Current Use Case**
A lightweight prediction model estimates outcomes such as:
- Probability of securing an entry-level or junior ML role within a defined timeframe

**Design Principles**
- Clear separation between training and inference
- Reproducible experiments
- Model artifacts treated as deployable assets

---

## 4. Application Layer

**Technologies**
- Streamlit
- Python

**Responsibilities**
- Interactive resume dashboard
- Visualization of experience, skills, and timelines
- User-facing ML inference (predictions)
- AI-assisted resume chatbot interface

**Key Characteristics**
- Component-based UI architecture
- Data-driven rendering (no hardcoded content)
- Real-time inference integration
- Resume content exposed as structured data, not static text

This layer demonstrates how analytics and ML outputs are consumed by end users in a practical application.

---

## 5. AI Resume Chatbot (RAG-based)

**Concept**
- Resume content is treated as a structured knowledge base
- User questions are answered based on resume data, not generic templates

**Responsibilities**
- Enable natural language queries over resume content
- Provide contextual, grounded responses
- Demonstrate applied AI usage in an enterprise-style information system

This component highlights practical AI integration rather than experimental usage.

---

## 6. Infrastructure & Deployment

**Current Setup**
- Python virtual environments
- Modular project structure
- Environment-based configuration

**Planned / Extensible Components**
- Docker containerization
- Environment-specific deployments (local / cloud)
- CI-friendly structure

The system is designed so that deployment can be extended without architectural changes.

---

## Architectural Principles Applied

- Modular separation of concerns
- Clear data ownership between layers
- Reproducibility over ad-hoc execution
- Production-oriented structure instead of demo-driven code
- Focus on clarity, maintainability, and extensibility

---

## Summary

This portfolio demonstrates not only technical implementation but also **engineering judgment**.  
It reflects how real systems are designed, scaled, and communicated within professional data and software teams.

The goal is to showcase **how problems are structured and solved**, rather than simply listing tools or technologies.

[Streamlit UI]
      |
      v
[PostgreSQL] <-> [ETL Pipelines]
      |
      v
[Feature Store]
      |
      v
[ML Model] ----> [Predictions]
      |
      v
[Resume Chatbot]
