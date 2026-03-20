from fastapi import APIRouter, Depends, Query, HTTPException, Body
from api.dependencies.auth_admin import require_admin
from db.db import get_db_conn
import uuid
from datetime import datetime
from chatbot.indexing.index_manager import IndexManager
from chatbot.runtime_config import config
from psycopg2.extras import Json






router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)


TABLE_GROUPS = {
    "profile": ["users", "career_preferences"],
    "experience": [
        "experience",
        "experience_responsibilities",
        "experience_tools"
    ],
    "projects": [
        "projects",
        "project_tech_stack",
        "project_outcomes"
    ],
    "skills": [
        "skills",
        "user_skills"
    ],
    "education": [
        "education",
        "education_courses"
    ],
    "others": [
        "certifications",
        "extracurricular_activities",
        "languages",
        "career_timeline"
    ]
}


# =====================================================
# HELPERS
# =====================================================

def validate_table(cur, table: str):
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    valid_tables = [row[0] for row in cur.fetchall()]

    if table not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Invalid table name: {table}")


def get_primary_keys(cur, table: str):
    cur.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
          AND tc.table_name = %s
        ORDER BY kcu.ordinal_position;
    """, (table,))
    return [row[0] for row in cur.fetchall()]


def get_column_metadata(cur, table: str):
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
    """, (table,))
    return {
        row[0]: {
            "data_type": row[1],
            "nullable": row[2] == "YES"
        }
        for row in cur.fetchall()
    }


# =====================================================
# PRODUCTION-GRADE VALUE VALIDATION
# =====================================================

def validate_and_cast(value, column_type, nullable, column_name):

    if value in [None, ""]:
        if not nullable:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{column_name}' cannot be null"
            )
        return None

    try:

        if column_type in ["uuid"]:
            return str(uuid.UUID(str(value)))

        if column_type in ["integer", "bigint"]:
            return int(value)

        if column_type in ["numeric", "double precision", "real"]:
            return float(value)

        if column_type in ["boolean"]:
            if str(value).lower() in ["true", "1"]:
                return True
            if str(value).lower() in ["false", "0"]:
                return False
            raise ValueError()

        if column_type in ["timestamp without time zone", "timestamp with time zone"]:
            return datetime.fromisoformat(str(value))

        

        if "ARRAY" in column_type.upper() or column_type.endswith("[]"):
            if isinstance(value, str):
                value = [v.strip() for v in value.split(",") if v.strip()]

            if isinstance(value, list):
                # Convert to PostgreSQL array literal
                return "{" + ",".join([f'"{v}"' for v in value]) + "}"

            raise HTTPException(
                status_code=400,
                detail=f"Invalid array format for column '{column_name}'"
            )

            
        # text, varchar, etc
        return value

    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value for column '{column_name}' (expected {column_type})"
        )


# =====================================================
# LIST TABLES
# =====================================================

@router.get("/tables")
def list_tables():
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        rows = cur.fetchall()

    return {"tables": [row[0] for row in rows]}


# =====================================================
# GROUP FETCH
# =====================================================

@router.get("/group/{group_name}")
def get_group_data(group_name: str):

    if group_name not in TABLE_GROUPS:
        raise HTTPException(status_code=400, detail="Invalid group")

    tables = TABLE_GROUPS[group_name]
    result = {}

    with get_db_conn() as conn:
        cur = conn.cursor()

        for table in tables:
            validate_table(cur, table)
            cur.execute(f"SELECT * FROM {table};")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            result[table] = [
                dict(zip(columns, row))
                for row in rows
            ]

    return result


# =====================================================
# EXPERIENCE GROUP (DYNAMIC COMPATIBLE)
# =====================================================

@router.get("/group/experience")
def get_experience_group():

    result = {}

    with get_db_conn() as conn:
        cur = conn.cursor()

        # experience
        cur.execute("SELECT * FROM experience ORDER BY start_date DESC;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result["experience"] = [
            dict(zip(columns, row))
            for row in rows
        ]

        # responsibilities
        cur.execute("SELECT * FROM experience_responsibilities;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result["experience_responsibilities"] = [
            dict(zip(columns, row))
            for row in rows
        ]

        # tools
        cur.execute("SELECT * FROM experience_tools;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result["experience_tools"] = [
            dict(zip(columns, row))
            for row in rows
        ]

    return result






# =====================================================
# GROUP UPDATE (ENTERPRISE SAFE)
# =====================================================

@router.put("/update-group/{group_name}")
def update_group_data(group_name: str, payload: dict = Body(...)):

    

    if group_name not in TABLE_GROUPS:
        raise HTTPException(status_code=400, detail="Invalid group")

    tables = TABLE_GROUPS[group_name]

    with get_db_conn() as conn:
        cur = conn.cursor()

        for table in tables:

            if table not in payload:
                continue

            validate_table(cur, table)
            primary_keys = get_primary_keys(cur, table)
            column_meta = get_column_metadata(cur, table)

            records = payload[table]

            for record in records:

                # Ensure PK exists
                for pk in primary_keys:
                    if pk not in record:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing primary key '{pk}' in table '{table}'"
                        )

                pk_values = {k: record[k] for k in primary_keys}

                non_pk_columns = [
                    k for k in record.keys()
                    if k not in primary_keys
                ]

                if not non_pk_columns:
                    continue

                set_clause_parts = []
                values = []

                for col in non_pk_columns:

                    if col not in column_meta:
                        continue

                    validated_value = validate_and_cast(
                        record[col],
                        column_meta[col]["data_type"],
                        column_meta[col]["nullable"],
                        col
                    )

                    # 🔥 ADD THIS BLOCK HERE
                    print("COLUMN:", col)
                    print("TYPE:", column_meta[col]["data_type"])
                    print("RAW VALUE:", record[col])
                    print("VALIDATED VALUE:", validated_value)
                    print("----")

                    if column_meta[col]["data_type"].endswith("[]"):
                        set_clause_parts.append(f"{col} = %s")
                    else:
                        set_clause_parts.append(f"{col} = %s")
                    values.append(validated_value)

                where_clause = " AND ".join(
                    [f"{pk} = %s" for pk in primary_keys]
                )

                values += [pk_values[pk] for pk in primary_keys]

                query = f"""
                    UPDATE {table}
                    SET {", ".join(set_clause_parts)}
                    WHERE {where_clause}
                """
                print("FINAL VALUES SENT TO DB:", values)
                cur.execute(query, values)

        conn.commit()

    return {"status": "group updated successfully"}




# =====================================================
# ADD EXPERIENCE (RELATIONAL INSERT SAFE)
# =====================================================

@router.post("/add-experience")
def add_experience(payload: dict = Body(...)):

    experience = payload.get("experience")
    responsibilities = payload.get("responsibilities", [])
    tools = payload.get("tools", [])

    if not experience:
        raise HTTPException(status_code=400, detail="Experience data required")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # =====================
        # INSERT EXPERIENCE
        # =====================

        cur.execute("""
        INSERT INTO experience (
            user_id,
            experience_type,
            role,
            company,
            location,
            start_date,
            end_date,
            context,
            notes
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING experience_id
        """, (
            experience["user_id"],
            experience["experience_type"],
            experience.get("role") or None,
            experience.get("company") or None,
            experience.get("location") or None,
            experience.get("start_date") or None,
            experience.get("end_date") or None,
            experience.get("context") or None,
            experience.get("notes") or None,
        ))

        experience_id = cur.fetchone()[0]

        # =====================
        # INSERT RESPONSIBILITIES
        # =====================

        for res in responsibilities:

            responsibility = res.get("responsibility") or None
            learning_outcomes = res.get("learning_outcomes") or None

            cur.execute("""
                INSERT INTO experience_responsibilities (
                    experience_id,
                    responsibility,
                    learning_outcomes
                )
                VALUES (%s,%s,%s)
            """, (
                experience_id,
                responsibility,
                learning_outcomes,
            ))

        # =====================
        # INSERT TOOLS
        # =====================

        for tool in tools:
            cur.execute("""
                INSERT INTO experience_tools (
                    experience_id,
                    tool
                )
                VALUES (%s,%s)
            """, (
                experience_id,
                tool.get("tool"),
            ))

        conn.commit()

    return {"status": "Experience added successfully"}



# =====================================================
# ADD RESPONSIBILITY TO EXISTING EXPERIENCE
# =====================================================

@router.post("/add-responsibility/{experience_id}")
def add_responsibility(experience_id: str, payload: dict = Body(...)):

    responsibility = payload.get("responsibility")
    learning_outcomes = payload.get("learning_outcomes")

    if not responsibility and not learning_outcomes:
        raise HTTPException(
            status_code=400,
            detail="Either responsibility or learning_outcomes required"
        )

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure experience exists
        cur.execute(
            "SELECT 1 FROM experience WHERE experience_id = %s",
            (experience_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Experience not found")

        cur.execute("""
            INSERT INTO experience_responsibilities (
                experience_id,
                responsibility,
                learning_outcomes
            )
            VALUES (%s,%s,%s)
        """, (
            experience_id,
            responsibility,
            learning_outcomes
        ))

        conn.commit()

    return {"status": "Responsibility added"}




# =====================================================
# DELETE EXPERIENCE (CASCADE SAFE)
# =====================================================

@router.delete("/delete-experience/{experience_id}")
def delete_experience(experience_id: str):

    try:
        experience_id = str(uuid.UUID(experience_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid experience_id")
    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure exists
        cur.execute(
            "SELECT 1 FROM experience WHERE experience_id = %s",
            (experience_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Experience not found")

        # Delete children first
        cur.execute(
            "DELETE FROM experience_responsibilities WHERE experience_id = %s",
            (experience_id,)
        )

        cur.execute(
            "DELETE FROM experience_tools WHERE experience_id = %s",
            (experience_id,)
        )

        # Delete parent
        cur.execute(
            "DELETE FROM experience WHERE experience_id = %s",
            (experience_id,)
        )

        conn.commit()

    return {"status": "Experience deleted"}




# =====================================================
# DELETE EXPERIENCE RESPONSIBILITY
# =====================================================

@router.delete("/delete-responsibility/{id}")
def delete_responsibility(id: str):

    try:
        id = str(uuid.UUID(id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM experience_responsibilities WHERE id = %s",
            (id,)
        )

        conn.commit()

    return {"status": "Deleted"}


# =====================================================
# DELETE TOOL
# =====================================================

@router.delete("/delete-tool/{tool_id}")
def delete_tool(tool_id: str):

    try:
        tool_id = str(uuid.UUID(tool_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM experience_tools WHERE id = %s",
            (tool_id,)
        )

        conn.commit()

    return {"status": "Tool deleted"}



# =====================================================
# ADD TOOL TO EXISTING EXPERIENCE
# =====================================================

@router.post("/add-tool/{experience_id}")
def add_tool(experience_id: str, payload: dict = Body(...)):

    tool = payload.get("tool")

    if not tool:
        raise HTTPException(status_code=400, detail="Tool required")

    # Validate UUID format
    try:
        experience_id = str(uuid.UUID(experience_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid experience_id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure experience exists
        cur.execute(
            "SELECT 1 FROM experience WHERE experience_id = %s",
            (experience_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Experience not found")

        cur.execute("""
            INSERT INTO experience_tools (
                experience_id,
                tool
            )
            VALUES (%s,%s)
        """, (
            experience_id,
            tool
        ))

        conn.commit()

    return {"status": "Tool added"}



# =====================================================
# ADD PROJECT (RELATIONAL INSERT SAFE)
# =====================================================

@router.post("/add-project")
def add_project(payload: dict = Body(...)):

    project = payload.get("project")
    tech_stack = payload.get("tech_stack", [])
    outcomes = payload.get("outcomes", [])

    if not project:
        raise HTTPException(status_code=400, detail="Project data required")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # =====================
        # INSERT PROJECT
        # =====================
        cur.execute("""
            INSERT INTO projects (
                user_id,
                title,
                project_type,
                description,
                scope,
                github_url,
                primary_role
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING project_id
        """, (
            project["user_id"],
            project.get("title"),
            project.get("project_type"),
            project.get("description"),
            project.get("scope"),
            project.get("github_url"),
            project.get("primary_role"),
        ))

        project_id = cur.fetchone()[0]

        # =====================
        # INSERT TECH STACK
        # =====================
        for tech in tech_stack:
            cur.execute("""
                INSERT INTO project_tech_stack (
                    project_id,
                    technology
                )
                VALUES (%s,%s)
            """, (
                project_id,
                tech.get("technology")
            ))

        # =====================
        # INSERT OUTCOMES
        # =====================
        for out in outcomes:
            cur.execute("""
                INSERT INTO project_outcomes (
                    project_id,
                    outcome
                )
                VALUES (%s,%s)
            """, (
                project_id,
                out.get("outcome")
            ))

        conn.commit()

    return {"status": "Project added successfully"}



# =====================================================
# DELETE PROJECT (CASCADE SAFE)
# =====================================================

@router.delete("/delete-project/{project_id}")
def delete_project(project_id: str):

    try:
        project_id = str(uuid.UUID(project_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure project exists
        cur.execute(
            "SELECT 1 FROM projects WHERE project_id = %s",
            (project_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete children first
        cur.execute(
            "DELETE FROM project_tech_stack WHERE project_id = %s",
            (project_id,)
        )

        cur.execute(
            "DELETE FROM project_outcomes WHERE project_id = %s",
            (project_id,)
        )

        # Delete parent
        cur.execute(
            "DELETE FROM projects WHERE project_id = %s",
            (project_id,)
        )

        conn.commit()

    return {"status": "Project deleted"}

    

# =====================================================
# DELETE PROJECT TECH
# =====================================================

@router.delete("/delete-project-tech/{tech_id}")
def delete_project_tech(tech_id: str):

    try:
        tech_id = str(uuid.UUID(tech_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM project_tech_stack WHERE id = %s",
            (tech_id,)
        )

        conn.commit()

    return {"status": "Technology deleted"}



# =====================================================
# ADD OUTCOME TO EXISTING PROJECT
# =====================================================

@router.post("/add-project-outcome/{project_id}")
def add_project_outcome(project_id: str, payload: dict = Body(...)):

    outcome = payload.get("outcome")

    if not outcome:
        raise HTTPException(status_code=400, detail="Outcome required")

    try:
        project_id = str(uuid.UUID(project_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure project exists
        cur.execute(
            "SELECT 1 FROM projects WHERE project_id = %s",
            (project_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found")

        cur.execute("""
            INSERT INTO project_outcomes (
                project_id,
                outcome
            )
            VALUES (%s,%s)
        """, (project_id, outcome))

        conn.commit()

    return {"status": "Outcome added"}


# =====================================================
# DELETE PROJECT OUTCOME
# =====================================================

@router.delete("/delete-project-outcome/{outcome_id}")
def delete_project_outcome(outcome_id: str):

    try:
        outcome_id = str(uuid.UUID(outcome_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM project_outcomes WHERE id = %s",
            (outcome_id,)
        )

        conn.commit()

    return {"status": "Outcome deleted"}




# =====================================================
# ADD TECH TO EXISTING PROJECT
# =====================================================

@router.post("/add-project-tech/{project_id}")
def add_project_tech(project_id: str, payload: dict = Body(...)):

    technology = payload.get("technology")

    if not technology:
        raise HTTPException(status_code=400, detail="Technology required")

    try:
        project_id = str(uuid.UUID(project_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM projects WHERE project_id = %s",
            (project_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found")

        cur.execute("""
            INSERT INTO project_tech_stack (
                project_id,
                technology
            )
            VALUES (%s,%s)
        """, (project_id, technology))

        conn.commit()

    return {"status": "Technology added"}



# =====================================================
# ADD SKILL FOR USER
# =====================================================

@router.post("/add-skill")
def add_skill(payload: dict = Body(...)):

    skill_name = payload.get("skill_name")
    category = payload.get("category")
    proficiency_level = payload.get("proficiency_level")
    user_id = payload.get("user_id")

    if not skill_name or not user_id:
        raise HTTPException(status_code=400, detail="Skill name and user_id required")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Check if skill already exists
        cur.execute(
            "SELECT skill_id FROM skills WHERE skill_name = %s",
            (skill_name,)
        )
        row = cur.fetchone()

        if row:
            skill_id = row[0]
        else:
            cur.execute("""
                INSERT INTO skills (skill_name, category)
                VALUES (%s,%s)
                RETURNING skill_id
            """, (skill_name, category))
            skill_id = cur.fetchone()[0]

        # Insert into user_skills
        cur.execute("""
            INSERT INTO user_skills (user_id, skill_id, proficiency_level)
            VALUES (%s,%s,%s)
        """, (user_id, skill_id, proficiency_level))

        conn.commit()

    return {"status": "Skill added"}




# =====================================================
# DELETE SKILL FOR USER (SAFE FULL DELETE)
# =====================================================

@router.delete("/delete-skill/{user_id}/{skill_id}")
def delete_skill(user_id: str, skill_id: str):

    try:
        user_id = str(uuid.UUID(user_id))
        skill_id = str(uuid.UUID(skill_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Delete from user_skills first
        cur.execute(
            "DELETE FROM user_skills WHERE user_id = %s AND skill_id = %s",
            (user_id, skill_id)
        )

        # Check if skill still used by any user
        cur.execute(
            "SELECT 1 FROM user_skills WHERE skill_id = %s",
            (skill_id,)
        )

        still_exists = cur.fetchone()

        # If no more references, delete skill
        if not still_exists:
            cur.execute(
                "DELETE FROM skills WHERE skill_id = %s",
                (skill_id,)
            )

        conn.commit()

    return {"status": "Skill deleted"}



# =====================================================
# ADD EDUCATION (RELATIONAL INSERT SAFE)
# =====================================================

@router.post("/add-education")
def add_education(payload: dict = Body(...)):

    education = payload.get("education")
    courses = payload.get("courses", [])

    if not education:
        raise HTTPException(status_code=400, detail="Education data required")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Insert education
        cur.execute("""
            INSERT INTO education (
                user_id,
                degree,
                institution,
                location,
                start_year,
                end_year
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING education_id
        """, (
            education.get("user_id"),
            education.get("degree"),
            education.get("institution"),
            education.get("location"),
            education.get("start_year"),
            education.get("end_year"),
        ))

        education_id = cur.fetchone()[0]

        # Insert courses
        for course in courses:
            cur.execute("""
                INSERT INTO education_courses (
                    education_id,
                    course_title,
                    grade
                )
                VALUES (%s,%s,%s)
            """, (
                education_id,
                course.get("course_title"),
                course.get("grade"),
            ))

        conn.commit()

    return {"status": "Education added"}




# =====================================================
# DELETE EDUCATION (CASCADE SAFE)
# =====================================================

@router.delete("/delete-education/{education_id}")
def delete_education(education_id: str):

    try:
        education_id = str(uuid.UUID(education_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid education_id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        # Ensure exists
        cur.execute(
            "SELECT 1 FROM education WHERE education_id = %s",
            (education_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Education not found")

        # Delete children first
        cur.execute(
            "DELETE FROM education_courses WHERE education_id = %s",
            (education_id,)
        )

        # Delete parent
        cur.execute(
            "DELETE FROM education WHERE education_id = %s",
            (education_id,)
        )

        conn.commit()

    return {"status": "Education deleted"}



# =====================================================
# ADD RECORD (GENERIC FOR OTHERS)
# =====================================================

@router.post("/add-record/{table}")
def add_record(table: str, payload: dict = Body(...)):

    allowed_tables = [
        "certifications",
        "extracurricular_activities",
        "languages",
        "career_timeline"
    ]

    if table not in allowed_tables:
        raise HTTPException(status_code=400, detail="Invalid table")

    with get_db_conn() as conn:
        cur = conn.cursor()

        validate_table(cur, table)
        column_meta = get_column_metadata(cur, table)

        columns = []
        values = []
        placeholders = []

        for col, value in payload.items():

            if col not in column_meta:
                continue

            validated_value = validate_and_cast(
                value,
                column_meta[col]["data_type"],
                column_meta[col]["nullable"],
                col
            )

            columns.append(col)
            values.append(validated_value)
            placeholders.append("%s")

        query = f"""
            INSERT INTO {table}
            ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
        """

        cur.execute(query, values)
        conn.commit()

    return {"status": "Record added"}



# =====================================================
# DELETE RECORD (GENERIC FOR OTHERS)
# =====================================================

@router.delete("/delete-record/{table}/{record_id}")
def delete_record(table: str, record_id: str):

    allowed_tables = [
        "certifications",
        "extracurricular_activities",
        "languages",
        "career_timeline"
    ]

    if table not in allowed_tables:
        raise HTTPException(status_code=400, detail="Invalid table")

    try:
        record_id = str(uuid.UUID(record_id))
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    with get_db_conn() as conn:
        cur = conn.cursor()

        primary_keys = get_primary_keys(cur, table)

        if len(primary_keys) != 1:
            raise HTTPException(status_code=400, detail="Unsupported PK structure")

        pk = primary_keys[0]

        cur.execute(
            f"DELETE FROM {table} WHERE {pk} = %s",
            (record_id,)
        )

        conn.commit()

    return {"status": "Record deleted"}





@router.post("/publish")
def publish_resume():
    IndexManager.rebuild()
    return {"status": "Resume published successfully. Index rebuilt."}






@router.post("/llm-mode")
def set_llm_mode(payload: dict = Body(...)):

    mode = payload.get("mode")

    if mode not in ["mock", "live"]:
        raise HTTPException(status_code=400, detail="Invalid mode")

    config.llm_mode = mode

    return {
        "status": "ok",
        "mode": config.llm_mode
    }


@router.get("/llm-mode")
def get_llm_mode():
    return {"mode": config.llm_mode}




# =====================================================
# SCHEMA METADATA
# =====================================================

@router.get("/schema/{table}")
def get_schema(table: str):

    with get_db_conn() as conn:
        cur = conn.cursor()

        validate_table(cur, table)

        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
        """, (table,))

        columns = [
            {
                "column_name": row[0],
                "data_type": row[1],
                "nullable": row[2] == "YES"
            }
            for row in cur.fetchall()
        ]

    return {"columns": columns}