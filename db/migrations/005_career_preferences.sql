-- Career preferences (ML features)

CREATE TABLE career_preferences (
    user_id UUID REFERENCES users(user_id),
    target_roles TEXT[],
    preferred_locations TEXT[],
    work_type TEXT[]
);
