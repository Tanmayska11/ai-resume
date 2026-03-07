-- Education & courses

CREATE TABLE education (
    education_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    degree TEXT,
    institution TEXT,
    location TEXT,
    start_year INT,
    end_year TEXT
);

CREATE TABLE education_courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    education_id UUID REFERENCES education(education_id),
    course_title TEXT,
    grade TEXT
);
