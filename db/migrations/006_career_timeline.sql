-- Career timeline for UI charts

CREATE TABLE career_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    label TEXT,
    start_period DATE,
    end_period TEXT,
    timeline_type TEXT
);
