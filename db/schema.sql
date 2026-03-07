-- schema.sql
-- Base schema v1.0
-- Purpose: minimal, stable foundation
-- DO NOT MODIFY after initial creation

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -------------------------
-- Core user (flattened profile + contact)
-- -------------------------
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    title TEXT,
    location TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    linkedin_url TEXT,
    portfolio_url TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------
-- Skills master
-- -------------------------
CREATE TABLE skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name TEXT UNIQUE NOT NULL,
    category TEXT
);

-- -------------------------
-- User ↔ Skills bridge
-- -------------------------
CREATE TABLE user_skills (
    user_id UUID REFERENCES users(user_id),
    skill_id UUID REFERENCES skills(skill_id),
    proficiency_level INT CHECK (proficiency_level BETWEEN 0 AND 100),
    PRIMARY KEY (user_id, skill_id)
);


-- -------------------------
-- prediction table
-- -------------------------


CREATE TABLE job_match_predictions (
  id SERIAL PRIMARY KEY,
  job_description TEXT,
  match_score FLOAT,
  strengths JSONB,
  gaps JSONB,
  recommendations JSONB,
  created_at TIMESTAMP DEFAULT now()
);