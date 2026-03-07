# Deployment and Infrastructure

## Purpose

This document describes how the application is structured for deployment, configuration, and future scalability.

The goal is not to simulate a large production environment, but to demonstrate:
- Environment separation
- Reproducibility
- Deployment readiness
- Infrastructure-aware system design

---

## Application Components

The system is composed of the following major components:

- Streamlit-based web application (UI + orchestration)
- Batch data and feature pipelines
- Machine learning training and inference modules
- Resume-aware AI chatbot
- Persistent data storage

Each component is isolated at the code level and designed to be deployable independently.

---

## Environment Management

### Virtual Environment

- Python virtual environment (`venv`)
- All dependencies are explicitly pinned in `requirements.txt`
- Ensures consistent behavior across machines

### Environment Variables

Configuration values are managed via environment variables, including:

- Database connection strings
- API keys (LLM, external services)
- Environment mode (development / production)

An example configuration is provided via:

.env.example


Sensitive values are never committed to version control.

---

## Containerization Strategy

### Docker (Planned / Partially Implemented)

The application is designed to be containerized using Docker.

Intended container boundaries:

- `app` container – Streamlit UI and API integration
- `ml` container – model training and inference
- `db` container – PostgreSQL instance (local development)

Containerization provides:
- Reproducible builds
- Consistent runtime environment
- Simplified deployment across environments

---

## Infrastructure Layout

ai-resume-portfolio/
├── app/ # UI and application logic
├── ml/ # Feature pipelines and ML models
├── db/ # Database schemas and migrations
├── chatbot/ # AI chatbot logic
├── infra/ # Infrastructure and deployment assets
├── assets/ # Static files and images
└── docs/ # System documentation


This separation reflects common patterns used in production systems.

---

## Deployment Options

### Local Deployment

- Streamlit application runs locally
- PostgreSQL runs as a local service or container
- Suitable for development and testing

### Cloud Deployment (Planned)

The system is designed to support cloud deployment to platforms such as:

- AWS
- Azure
- GCP

Potential services:
- Container registry
- Managed PostgreSQL
- CI/CD-based deployment workflows

---

## CI/CD Considerations

While a full CI/CD pipeline is not implemented, the project structure supports:

- Automated tests execution
- Linting and formatting checks
- Container image builds
- Controlled deployments

This enables straightforward future integration with tools such as GitHub Actions.

---

## Security Considerations

Basic security practices are applied:

- No secrets in source code
- Environment-based configuration
- Read-only access patterns where possible

These practices reflect minimum production hygiene.

---

## Observability and Logging (Planned)

The application includes basic logging for:

- Pipeline execution
- Model inference
- User interaction events

This is intended to be extended with:
- Structured logs
- Centralized log storage
- Simple monitoring metrics

---

## Limitations

This project intentionally avoids:
- High-availability claims
- Auto-scaling configurations
- Complex orchestration tools (e.g., Kubernetes)

The focus is on **clarity and correctness**, not operational scale.

---

## Why This Matters

The deployment and infrastructure design demonstrates:
- Awareness of real-world constraints
- Separation of concerns
- Readiness for production deployment
- Ability to extend the system responsibly

---

## Summary

The application is designed with deployment in mind from the beginning.  
Infrastructure choices prioritize simplicity, reproducibility, and clear boundaries—qualities essential for maintainable production systems.
