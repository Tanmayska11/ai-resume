# AI Resume Portfolio & Recruiter Chatbot

An AI-powered interactive resume platform built using Python, Streamlit, PostgreSQL, FAISS, SentenceTransformers, and OpenAI.

This project combines:

- Interactive resume dashboard
- AI recruiter chatbot
- Resume knowledge retrieval using FAISS
- GitHub project grounding
- Streamlit UI
- PostgreSQL-backed resume data model
- Machine learning & analytics showcase

---

# Features

## Interactive Resume Dashboard

- Professional recruiter-focused dashboard
- Skills visualization
- Experience timeline
- Education section
- Projects showcase
- Certifications & languages
- Career prediction section

---

## AI Resume Chatbot

The chatbot can answer questions about:

- Professional experience
- Projects
- Technical skills
- Education
- Certifications
- Languages
- GitHub repositories

All answers are grounded in:

- PostgreSQL resume data
- GitHub README knowledge
- FAISS semantic retrieval

---

## Retrieval-Augmented Generation (RAG)

Architecture includes:

1. Resume knowledge builder
2. GitHub README ingestion
3. Embedding generation
4. FAISS vector indexing
5. Semantic retrieval
6. LLM response generation

---

# Tech Stack

## Frontend

- Streamlit
- HTML/CSS

## Backend

- Python
- PostgreSQL
- psycopg2

## AI / ML

- OpenAI API
- SentenceTransformers
- FAISS
- Hugging Face

## Data Engineering

- ETL pipelines
- Data modeling
- Vector search

---

# Project Structure

```bash
ai-resume-portfolio/
│
├── app/
│   ├── components/
│   ├── styles/
│   ├── utils/
│   ├── _pages/
│   └── main.py
│
├── chatbot/
│   ├── embeddings/
│   ├── knowledge/
│   ├── llm/
│   ├── retrieval/
│   └── service.py
│
├── db/
│   ├── chatbot_queries/
│   ├── migrations/
│   ├── queries/
│   ├── seed/
│   ├── db.py
│   └── schema.sql
│
├── docs/
├── ml/
├── tests/
├── assets/
└── requirements.txt
```

---

# System Architecture

```text
User Question
      ↓
Streamlit Chat UI
      ↓
ResumeChatbotService
      ↓
FAISS Retriever
      ↓
Semantic Search
      ↓
Relevant Resume Chunks
      ↓
OpenAI / Mock LLM
      ↓
Final Recruiter-Facing Answer
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-resume-portfolio.git
cd ai-resume-portfolio
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# PostgreSQL Setup

## 1. Create Database

```sql
CREATE DATABASE ai_resume_portfolio;
```

---

## 2. Configure Environment Variables

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_resume_portfolio
DB_USER=postgres
DB_PASSWORD=your_password

OPENAI_API_KEY=your_openai_key

RESUME_USER_ID=your_user_id

LLM_MODE=mock
```

---

## 3. Run Schema

```bash
psql -U postgres -d ai_resume_portfolio -f db/schema.sql
```

---

## 4. Seed Resume Data

```bash
python db/seed/seed_resume.py
```

---

# Build FAISS Index

Before using the chatbot, build embeddings and FAISS index.

```bash
python -m chatbot.embeddings.build_index
```

Expected output:

```bash
🔹 Building documents...
🔹 Embedding documents...
🔹 Creating FAISS index...
✅ FAISS index built successfully.
```

---

# Run Streamlit Application

```bash
streamlit run app/main.py
```

Default URL:

```text
http://localhost:8501
```

---

# Chatbot Modes

The project supports two chatbot modes.

## Mock Mode (Recommended for Development)

No OpenAI credits required.

```env
LLM_MODE=mock
```

Behavior:

- Uses retrieved resume chunks directly
- No API calls
- Free development/testing
- Stable local development

---

## Live OpenAI Mode

Requires OpenAI API credits.

```env
LLM_MODE=live
```

Behavior:

- Uses OpenAI GPT model
- Better natural language responses
- Production-ready recruiter interaction

---

# Running Tests

```bash
pytest -v
```

Example output:

```bash
7 passed
```

---

# Chatbot Pipeline

## Data Flow

```text
PostgreSQL Resume Data
        ↓
resume_builder.py
        ↓
Normalized Knowledge Chunks
        ↓
github_ingestor.py
        ↓
GitHub README Knowledge
        ↓
embedder.py
        ↓
Vector Embeddings
        ↓
build_index.py
        ↓
FAISS Vector Store
        ↓
retriever.py
        ↓
Relevant Context
        ↓
LLM Client
        ↓
Recruiter-Facing Answer
        ↓
Streamlit Chat UI
```

---

# Key Components

## resume_builder.py

Builds structured resume knowledge:

- Profile
- Experience
- Projects
- Skills
- Education
- Certifications
- Languages

---

## github_ingestor.py

Fetches:

- GitHub README files
- Project repository knowledge
- Technical project context

---

## embedder.py

Uses SentenceTransformers:

```python
all-MiniLM-L6-v2
```

Generates semantic vector embeddings.

---

## retriever.py

Responsible for:

- Query embedding
- FAISS semantic search
- Intent-aware filtering
- Returning relevant chunks

---

## client.py

Handles:

- OpenAI integration
- Mock mode
- Prompt generation
- Recruiter-facing answer generation

---

# Example Questions

Recruiters can ask:

```text
What projects has Tanmay built?
```

```text
What is Tanmay's backend engineering experience?
```

```text
Which machine learning technologies has Tanmay used?
```

```text
What data engineering tools does Tanmay know?
```

```text
Tell me about Tanmay.
```

---

# Deployment

## Recommended Deployment Stack

- Streamlit Cloud
- Render
- Railway
- AWS EC2
- Docker

---

## Production Recommendations

### Use Live LLM

```env
LLM_MODE=live
```

### Protect Secrets

Never commit:

- `.env`
- API keys
- Database passwords

---

## Recommended Improvements

Future enhancements:

- Conversation memory
- Hybrid BM25 + vector search
- Redis caching
- Authentication
- Admin CMS
- Analytics dashboard
- Recruiter interaction tracking
- PDF resume export
- Multi-user architecture

---

# Example Resume Domains Covered

- Data Engineering
- Analytics Engineering
- Backend Development
- Machine Learning
- NLP
- LLM Systems
- ETL Pipelines
- BI & Reporting

---

# Known Limitations

Current version limitations:

- Limited conversational memory
- Single-user architecture
- Local FAISS persistence
- No streaming responses
- Basic intent classification

---

# Author

## Tanmay Santosh Khairnar

Data Engineer | Analytics Engineer | Machine Learning Engineer (Projects)

Munich, Germany

---

# License

This project is intended for:

- Portfolio use
- Recruiter demonstrations
- Learning purposes
- AI engineering showcase

---

# Final Notes

This project demonstrates practical implementation of:

- AI engineering
- Retrieval-Augmented Generation (RAG)
- Semantic search
- Vector databases
- LLM integration
- Data engineering workflows
- Full-stack Python development
- Recruiter-focused AI products

It is designed as both:

1. A professional interactive resume
2. A production-style AI application showcase

