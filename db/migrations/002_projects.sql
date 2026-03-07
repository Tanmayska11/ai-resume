-- Projects core

CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    title TEXT,
    project_type TEXT,
    description TEXT,
    scope TEXT,
    github_url TEXT,
    primary_role TEXT
);

CREATE TABLE project_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    outcome TEXT
);

CREATE TABLE project_tech_stack (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    technology TEXT
);
