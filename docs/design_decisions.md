# Design Decisions

## Purpose

This document outlines the key technical and architectural decisions made during the development of this portfolio.

The intent is not to claim optimality, but to demonstrate **reasoned engineering judgment**, trade-off awareness, and the ability to design systems deliberately.

---

## 1. Treating the Resume as Structured Data

### Decision
Resume content is stored and processed as structured, relational data rather than static text.

### Rationale
- Enables analytics and machine learning use cases
- Supports consistent rendering across UI components
- Allows resume data to act as a single source of truth

### Trade-offs
- Higher initial modeling effort
- Requires schema design

This approach reflects how real enterprise systems treat business information.

---

## 2. Batch-Oriented Data and Feature Pipelines

### Decision
Data processing and feature generation are implemented as batch pipelines.

### Rationale
- Resume data changes infrequently
- Simplifies reproducibility and debugging
- Avoids unnecessary real-time complexity

### Trade-offs
- Not suitable for high-frequency data updates
- Requires re-running pipelines for updates

This mirrors how many production analytics systems are designed.

---

## 3. Choice of PostgreSQL as Primary Data Store

### Decision
PostgreSQL is used as the core database.

### Rationale
- Strong relational modeling
- Mature SQL support
- Widely used in production systems

### Trade-offs
- Not optimized for unstructured or high-volume streaming data

The choice prioritizes clarity and reliability over novelty.

---

## 4. Interpretable Machine Learning Models

### Decision
Simple, interpretable ML models are used instead of complex deep learning approaches.

### Rationale
- Dataset size is limited
- Model outputs must be explainable
- Easier validation and maintenance

### Trade-offs
- Potentially lower ceiling on predictive performance

This aligns with enterprise practices where interpretability is often preferred.

---

## 5. MLflow for Experiment Tracking

### Decision
MLflow is used for local experiment tracking.

### Rationale
- Clear experiment lineage
- Minimal setup overhead
- Industry-recognized tool

### Trade-offs
- Local tracking only (no distributed registry)

This demonstrates familiarity with real ML lifecycle tooling.

---

## 6. Streamlit for the Application Layer

### Decision
Streamlit is used for the interactive application.

### Rationale
- Rapid prototyping with clean Python integration
- Well suited for data-centric applications
- Low operational overhead

### Trade-offs
- Less control than full frontend frameworks
- Not optimized for extremely high traffic

Chosen to focus effort on system behavior rather than UI engineering.

---

## 7. Component-Based Application Structure

### Decision
The application is decomposed into modular components.

### Rationale
- Improves readability and maintainability
- Enables independent evolution of features
- Mirrors production code organization

### Trade-offs
- Slightly higher coordination overhead during development

This approach reflects professional engineering practices.

---

## 8. Conservative Deployment Strategy

### Decision
Deployment complexity is intentionally limited.

### Rationale
- Portfolio context does not require high availability
- Focus is on correctness and clarity
- Avoids over-engineering

### Trade-offs
- No automated scaling or advanced orchestration

This choice reflects an understanding of scope and requirements.

---

## 9. Explicitly Documenting Limitations

### Decision
Limitations and non-goals are explicitly stated in documentation.

### Rationale
- Demonstrates realism and engineering maturity
- Builds reviewer trust
- Avoids misleading claims

### Trade-offs
- Less “flashy” presentation

In professional environments, credibility outweighs exaggeration.

---

## Summary

The design decisions made in this project are intentional and context-driven.  
They prioritize clarity, maintainability, and production relevance over novelty or complexity.

This portfolio is designed to demonstrate **how systems are thought through**, not just how they are implemented.
