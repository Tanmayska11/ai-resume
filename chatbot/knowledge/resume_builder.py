# chatbot/resume_builder.py

"""
Builds a complete, normalized resume knowledge base
for chatbot grounding.

Output:
- List[str] → text chunks
- Each chunk is factual, resume-backed, and embeddable
"""

from typing import List,Dict,Any

from db.chatbot_queries.profile import fetch_profile_context
from db.chatbot_queries.experience import fetch_experience_context
from db.chatbot_queries.projects import fetch_projects_context
from db.chatbot_queries.skills import fetch_skills_context
from db.chatbot_queries.education import fetch_education_context
from db.chatbot_queries.certifications import fetch_certifications_context
from db.chatbot_queries.languages import fetch_languages_context
from db.chatbot_queries.extracurricular_activities import fetch_extracurricular_activities_context


def build_resume_knowledge_base(user_id: str) -> List[Dict[str, Any]]:
    """
    Aggregate resume data from PostgreSQL
    and convert it into LLM-ready knowledge chunks.
    """

    chunks: List[Dict[str, Any]] = []

    # ============================
    # PROFILE
    # ============================
    profile = fetch_profile_context(user_id)

    if profile:
        chunks.extend([
            {
                "text": f"Full name: {profile['name']}",
                "metadata": {"source": "profile", "section": "profile", "field": "name"},
            },
            {
                "text": f"Professional title: {profile['title']}",
                "metadata": {"source": "profile", "section": "profile", "field": "title"},
            },
            {
                "text": f"Location: {profile['location']}",
                "metadata": {"source": "profile", "section": "profile", "field": "location"},
            },
            {
                "text": f"Professional summary: {profile['summary']}",
                "metadata": {"source": "profile", "section": "profile", "field": "summary"},
            },
        ])

        if profile["career_preferences"]["target_roles"]:
            chunks.append({
                "text": "Target roles: " + ", ".join(profile["career_preferences"]["target_roles"]),
                "metadata": {"source": "profile", "section": "profile", "field": "target_roles"},
            })

        if profile["career_preferences"]["preferred_locations"]:
            chunks.append({
                "text": "Preferred locations: " + ", ".join(profile["career_preferences"]["preferred_locations"]),
                "metadata": {"source": "profile", "section": "profile", "field": "preferred_locations"},
            })

        if profile["career_preferences"]["work_type"]:
            chunks.append({
                "text": "Work type: " + ", ".join(profile["career_preferences"]["work_type"]),
                "metadata": {"source": "profile", "section": "profile", "field": "work_type"},
            })


    # ============================
    # EXPERIENCE (STRUCTURED)
    # ============================
    experiences = fetch_experience_context(user_id)

    for exp in experiences:
        exp_type = exp["experience_type"]  # professional | experimental
        role = exp["role"]
        company = exp["company"]
        location = exp["location"]

        role_id = f"{role}__{company or 'experimental'}"

        # Header chunk (used for grouping)
        title_parts = [role]
        if company:
            title_parts.append(company)

        chunks.append({
            "text": " | ".join(title_parts),
            "metadata": {
                "source": "experience",
                "section": "experience",
                "experience_type": exp_type,
                "role_id": role_id,
                "field": "header",
            },
        })

        # Duration (only if present)
        if exp["duration"]["start_date"]:
            chunks.append({
                "text": f"Duration: {exp['duration']['start_date']} – {exp['duration']['end_date']}",
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "duration",
                },
            })

        # Location
        if location:
            chunks.append({
                "text": f"Location: {location}",
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "location",
                },
            })

        # Summary / context
        if exp["summary"]:
            chunks.append({
                "text": f"Context: {exp['summary']}",
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "context",
                },
            })

        # Responsibilities (professional)
        for r in exp["key_responsibilities"]:
            chunks.append({
                "text": r,
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "responsibility",
                },
            })

        # Learning outcomes (experimental)
        for l in exp["learning_outcomes"]:
            chunks.append({
                "text": l,
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "learning_outcome",
                },
            })

        # Tools
        if exp["tools_used"]:
            chunks.append({
                "text": "Tools: " + ", ".join(exp["tools_used"]),
                "metadata": {
                    "source": "experience",
                    "section": "experience",
                    "experience_type": exp_type,
                    "role_id": role_id,
                    "field": "tools",
                },
            })



    # ============================
    # PROJECTS (STRUCTURED)
    # ============================
    projects = fetch_projects_context(user_id)

    for project in projects:
        project_id = project["title"].lower().replace(" ", "_")

        # Header
        chunks.append({
            "text": project["title"],
            "metadata": {
                "source": "projects",
                "section": "projects",
                "project_id": project_id,
                "field": "header",
            },
        })

        # Description
        if project["description"]:
            chunks.append({
                "text": f"Description: {project['description']}",
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "description",
                },
            })

        # Scope
        if project["scope"]:
            chunks.append({
                "text": f"Scope: {project['scope']}",
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "scope",
                },
            })

        # Primary role
        if project["primary_role"]:
            chunks.append({
                "text": f"Role: {project['primary_role']}",
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "role",
                },
            })

        # Outcomes
        for o in project["key_outcomes"]:
            chunks.append({
                "text": o,
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "outcome",
                },
            })

        # Technologies
        # if project["technologies_used"]:
        #     chunks.append({
        #         "text": "Technologies: " + ", ".join(project["technologies_used"]),
        #         "metadata": {
        #             "source": "projects",
        #             "section": "projects",
        #             "project_id": project_id,
        #             "field": "tools",
        #         },
        #     })


        for tech in project["technologies_used"]:
            chunks.append({
                "text": tech,
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "technology",
                },
            })


        # GitHub
        if project["github_url"]:
            chunks.append({
                "text": f"GitHub: {project['github_url']}",
                "metadata": {
                    "source": "projects",
                    "section": "projects",
                    "project_id": project_id,
                    "field": "link",
                    "url": project["github_url"],
                },
            })


    # ============================
    # SKILLS (STRUCTURED)
    # ============================
    skills = fetch_skills_context(user_id)

    for s in skills:
        chunks.append({
            "text": s["skill_name"],
            "metadata": {
                "source": "skills",
                "section": "skills",
                "category": s["category"],
                "field": "skill",
            },
        })


    # ============================
    # EDUCATION (STRUCTURED)
    # ============================
    education = fetch_education_context(user_id)

    for edu in education:
        edu_id = edu["education_id"]
        degree_text = edu["degree"]
        degree_lower = degree_text.lower()


        # Header
        chunks.append({
            "text": f"{edu['degree']} | {edu['institution']}",
            "metadata": {
                "source": "education",
                "section": "education",
                "education_id": edu_id,
                "degree": degree_lower,
                "field": "header",
            },
        })


        # Duration
        chunks.append({
            "text": f"Duration: {edu['start_year']} – {edu['end_year']}",
            "metadata": {
                "source": "education",
                "section": "education",
                "education_id": edu_id,
                "degree": degree_lower,
                "field": "duration",
            },
        })


        # Location
        chunks.append({
            "text": f"Location: {edu['location']}",
            "metadata": {
                "source": "education",
                "section": "education",
                "education_id": edu_id,
                "degree": degree_lower,
                "field": "location",
            },
        })


        # Courses (ONLY for that education_id)
        for c in edu["relevant_coursework"]:
            chunks.append({
                "text": f"{c['title']} ({c['grade']})" if c["grade"] else c["title"],
                "metadata": {
                    "source": "education",
                    "section": "education",
                    "education_id": edu_id,
                    "degree": degree_lower,
                    "field": "course",
                },
            })




    # ============================
    # CERTIFICATIONS (STRUCTURED)
    # ============================
    certifications = fetch_certifications_context(user_id)

    for cert in certifications:
        cert_id = cert["certification_id"]

        # Header (NAME → bold title)
        chunks.append({
            "text": cert["certificate_name"],
            "metadata": {
                "source": "certifications",
                "section": "certifications",
                "certification_id": cert_id,
                "field": "header",
            },
        })

        # Issuer
        if cert["issuer"]:
            chunks.append({
                "text": f"Issued by: {cert['issuer']}",
                "metadata": {
                    "source": "certifications",
                    "section": "certifications",
                    "certification_id": cert_id,
                    "field": "issuer",
                },
            })

        # Credential link
        if cert["credential_url"]:
            chunks.append({
                "text": f"Credential: {cert['credential_url']}",
                "metadata": {
                    "source": "certifications",
                    "section": "certifications",
                    "certification_id": cert_id,
                    "field": "link",
                    "url": cert["credential_url"],
                },
            })   



    # ============================
    # LANGUAGES (ATOMIC)
    # ============================
    languages = fetch_languages_context(user_id)

    for l in languages:
        chunks.append({
            "text": f"{l['language']}: {l['proficiency_level']}",
            "metadata": {
                "source": "languages",
                "section": "languages",
                "field": "language",
            }
        })

    

    # ============================
    # EXTRACURRICULAR ACTIVITIES (ATOMIC)
    # ============================
    activities = fetch_extracurricular_activities_context(user_id)

    for a in activities:
        chunks.append({
            "text": a["activity"],
            "metadata": {
                "source": "extracurricular_activities",
                "section": "extracurricular_activities",
                "field": "activity",
            }
        })

    return chunks
