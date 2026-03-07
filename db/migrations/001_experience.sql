-- Professional + Experimental experience

CREATE TABLE experience (
    experience_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    experience_type TEXT CHECK (experience_type IN ('professional', 'experimental')),
    role TEXT,
    company TEXT,
    location TEXT,
    start_date DATE,
    end_date DATE,
    context TEXT,
    notes TEXT
);

CREATE TABLE experience_responsibilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_id UUID REFERENCES experience(experience_id),
    responsibility TEXT
);

CREATE TABLE experience_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_id UUID REFERENCES experience(experience_id),
    tool TEXT
);
