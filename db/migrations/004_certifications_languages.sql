-- Certifications

CREATE TABLE certifications (
    certification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    name TEXT,
    issuer TEXT,
    credential_url TEXT
);

-- Languages

CREATE TABLE languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    language TEXT,
    proficiency TEXT
);
