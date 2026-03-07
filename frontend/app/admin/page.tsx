'use client'

import { useAuth0 } from "@auth0/auth0-react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"


const USER_ID = "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"

export default function AdminPage() {
  const {
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    user,
    getAccessTokenSilently,
    logout
  } = useAuth0()

  const [tables, setTables] = useState<string[]>([])
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [records, setRecords] = useState<any[]>([])
  const [editedRecords, setEditedRecords] = useState<any[]>([])
  const [isEditing, setIsEditing] = useState(false)
  const [groupSchema, setGroupSchema] = useState<any>(null)
  const [groupData, setGroupData] = useState<any>(null)
  const [activeGroup, setActiveGroup] = useState<string | null>(null)
  const experienceData = groupData?.experience || []
  const responsibilities = groupData?.experience_responsibilities || []
  const tools = groupData?.experience_tools || []
  const [showAddForm, setShowAddForm] = useState(false)
  const [isPublishing, setIsPublishing] = useState(false)

  const [newExperience, setNewExperience] = useState({
    user_id: "",
    experience_type: "",
    role: "",
    company: "",
    location: "",
    start_date: "",
    end_date: "",
    context: "",
    notes: ""
  })


  const [newResponsibilities, setNewResponsibilities] = useState<any[]>([])
  const [newTools, setNewTools] = useState<any[]>([])

  const [showAddProjectForm, setShowAddProjectForm] = useState(false)

  const [newProject, setNewProject] = useState({
    user_id: USER_ID,
    title: "",
    project_type: "",
    description: "",
    scope: "",
    github_url: "",
    primary_role: ""
  })

  const [newTechStack, setNewTechStack] = useState<any[]>([])
  const [newOutcomes, setNewOutcomes] = useState<any[]>([])

  const [showAddSkillForm, setShowAddSkillForm] = useState(false)

  const [newSkill, setNewSkill] = useState({
    user_id: USER_ID,
    skill_name: "",
    category: "",
    proficiency_level: ""
  })

  const [showAddEducationForm, setShowAddEducationForm] = useState(false)

  const [newEducation, setNewEducation] = useState({
    user_id: USER_ID,
    degree: "",
    institution: "",
    location: "",
    start_year: "",
    end_year: ""
  })

  const [newCourses, setNewCourses] = useState<any[]>([])
  const [activeAddTable, setActiveAddTable] = useState<string | null>(null)
  const [newRecord, setNewRecord] = useState<any>({
    user_id: USER_ID
  })

  const [llmMode, setLlmMode] = useState<"mock" | "live">("mock")






  // ===============================
  // AUTH CHECK
  // ===============================
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect({
        authorizationParams: {
          redirect_uri: `${window.location.origin}/admin`,
          connection: "email"
        }
      })
    }
  }, [isLoading, isAuthenticated])

  // ===============================
  // FETCH TABLES
  // ===============================
  useEffect(() => {
    async function fetchTables() {
      const token = await getAccessTokenSilently()

      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/tables`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      const data = await res.json()
      setTables(data.tables || [])
    }

    if (isAuthenticated) fetchTables()
  }, [isAuthenticated])


  // ===============================
  // FETCH LLM Mode
  // ===============================

  useEffect(() => {
    async function fetchMode() {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
        }
      })

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/llm-mode`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      const data = await res.json()
      setLlmMode(data.mode)
    }

    if (isAuthenticated) fetchMode()
  }, [isAuthenticated])




  // ===============================
  // HANDLE BROWSER BACK BUTTON
  // ===============================
  const router = useRouter()
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/")
    }
  }, [isLoading, isAuthenticated])





  // ===============================
  // FETCH SINGLE TABLE
  // ===============================
  async function fetchRecords(table: string) {
    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/${table}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const data = await res.json()

    setSelectedTable(table)
    setRecords(data.data || [])
    setEditedRecords(data.data || [])
    setGroupData(null)
    setIsEditing(false)
  }

  // ===============================
  // FETCH GROUP
  // ===============================
  async function fetchGroup(group: string) {
    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/group/${group}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const data = await res.json()

    // fetch schema for each table dynamically
    const schemaObj: any = {}

    for (const tableName of Object.keys(data)) {
      const schemaRes = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/schema/${tableName}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      const schemaData = await schemaRes.json()
      schemaObj[tableName] = schemaData.columns
    }

    setGroupSchema(schemaObj)
    setActiveGroup(group)
    setGroupData(data)

    // ✅ ADD THIS BLOCK RIGHT HERE
    if (group === "experience" && data.experience && data.experience.length > 0) {
      setNewExperience(prev => ({
        ...prev,
        user_id: data.experience[0].user_id
      }))
    }

    setSelectedTable(null)
    setIsEditing(false)
  }

  // ===============================
  // SAVE GROUP
  // ===============================
  async function saveGroup() {
    if (!activeGroup) return

    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/update-group/${activeGroup}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(groupData)
    })

    const data = await res.json()

    if (!res.ok) {
      alert(data.detail || "Update failed")
      return
    }

    setIsEditing(false)
    alert("Group updated successfully")
  }



  async function handleAddExperience() {
    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    if (!newExperience.experience_type) {
      alert("Experience type is required")
      return
    }

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-experience`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          experience: newExperience,
          responsibilities: newResponsibilities,
          tools: newTools
        })
      }
    )

    const data = await res.json()

    if (!res.ok) {
      alert(data.detail || "Insert failed")
      return
    }

    alert("Experience Added")
    setNewExperience({
      user_id: newExperience.user_id,
      experience_type: "",
      role: "",
      company: "",
      location: "",
      start_date: "",
      end_date: "",
      context: "",
      notes: ""
    })

    setNewResponsibilities([])
    setNewTools([])
    setShowAddForm(false)
    fetchGroup("experience")
  }


  async function handleAddProject() {

    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    if (!newProject.title) {
      alert("Title is required")
      return
    }

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-project`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          project: newProject,
          tech_stack: newTechStack,
          outcomes: newOutcomes
        })
      }
    )

    const data = await res.json()

    if (!res.ok) {
      alert(data.detail || "Insert failed")
      return
    }

    alert("Project Added")

    setNewProject({
      user_id: newProject.user_id,
      title: "",
      project_type: "",
      description: "",
      scope: "",
      github_url: "",
      primary_role: ""
    })

    setNewTechStack([])
    setNewOutcomes([])
    setShowAddProjectForm(false)

    fetchGroup("projects")
  }


  async function handleAddSkill() {

    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    if (!newSkill.skill_name) {
      alert("Skill name required")
      return
    }

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-skill`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newSkill)
      }
    )

    const data = await res.json()

    if (!res.ok) {
      alert(data.detail || "Insert failed")
      return
    }

    alert("Skill added")

    setNewSkill({
      ...newSkill,
      skill_name: "",
      category: "",
      proficiency_level: ""
    })

    setShowAddSkillForm(false)
    fetchGroup("skills")
  }


  async function handleAddEducation() {

    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-education`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          education: newEducation,
          courses: newCourses
        })
      }
    )

    const data = await res.json()

    if (!res.ok) {
      alert(data.detail || "Insert failed")
      return
    }

    alert("Education added")

    setNewEducation({
      ...newEducation,
      degree: "",
      institution: "",
      location: "",
      start_year: "",
      end_year: ""
    })

    setNewCourses([])
    setShowAddEducationForm(false)
    fetchGroup("education")
  }



  // ===============================
  // PUBLISH DATABASE
  // ===============================
  async function handlePublish() {
    try {
      setIsPublishing(true)

      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
        }
      })

      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/publish`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      const data = await res.json()

      if (!res.ok) {
        alert(data.detail || "Publish failed")
        return
      }

      alert("Database published successfully.")
    } catch (error) {
      alert("Something went wrong while publishing.")
    } finally {
      setIsPublishing(false)
    }
  }


  // ===============================
  // Toggle LLM mode
  // ===============================


  async function toggleLLMMode() {

    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
      }
    })

    const newMode = llmMode === "mock" ? "live" : "mock"

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/llm-mode`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ mode: newMode })
      }
    )

    const data = await res.json()
    setLlmMode(data.mode)
  }








  if (isLoading) return <p>Loading...</p>
  if (!isAuthenticated) return null

  return (
    <div style={{ padding: 40 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <h1 style={{ margin: 0 }}>Admin Panel</h1>

        <button
          style={{
            padding: "8px 16px",
            backgroundColor: isPublishing ? "#555" : "black",
            color: "white",
            borderRadius: "6px",
            cursor: isPublishing ? "not-allowed" : "pointer"
          }}
          onClick={handlePublish}
          disabled={isPublishing}
        >
          {isPublishing ? "Rebuilding Index..." : "Publish Database"}
        </button>

        <button
          onClick={toggleLLMMode}
          style={{
            padding: "8px 16px",
            backgroundColor: llmMode === "mock" ? "green" : "gold",
            color: "white",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          LLM Mode: {llmMode.toUpperCase()}
        </button>




        <button
          style={{
            padding: "8px 16px",
            backgroundColor: "red",
            color: "white",
            borderRadius: "6px",
            cursor: "pointer"
          }}
          onClick={() =>
            logout({
              logoutParams: {
                returnTo: `${window.location.origin}`
              }
            })
          }
        >
          Logout
        </button>
      </div>


      <p>Welcome {user?.email}</p>



      <h2>Tables</h2>
      <ul>

        <li>

          {/* GROUP BUTTON */}
          <button onClick={() => fetchGroup("profile")}>
            Profile
          </button> <br /> <br />
          <button onClick={() => fetchGroup("experience")}>
            Experience
          </button> <br /> <br />
          <button onClick={() => fetchGroup("projects")}>
            Projects
          </button> <br /> <br />
          <button onClick={() => fetchGroup("skills")}>
            Skills
          </button> <br /> <br />
          <button onClick={() => fetchGroup("education")}>
            Education
          </button> <br /> <br />
          <button onClick={() => fetchGroup("others")}>
            Others
          </button> <br />

        </li>

      </ul>

      <hr />


      {/* GROUP VIEW */}
      {groupData && (
        <div>
          <h2>Group View</h2>

          {!isEditing ? (
            <button onClick={() => setIsEditing(true)}>Edit</button>
          ) : (
            <button onClick={saveGroup}>Save All</button>
          )}

          <br /><br />

          {/* ========================= */}
          {/* EXPERIENCE SPECIAL RENDER */}
          {/* ========================= */}
          {activeGroup === "experience" ? (
            <>
              <button onClick={() => setShowAddForm(true)}>
                Add Experience
              </button>
              {["professional", "experimental"].map((type) => {

                const filteredExperience = experienceData.filter(
                  (exp: any) => exp.experience_type === type
                )

                if (filteredExperience.length === 0) return null

                return (
                  <div
                    key={type}
                    style={{
                      border: "2px solid #333",
                      padding: 25,
                      marginBottom: 40,
                      borderRadius: 10
                    }}
                  >
                    <h2 style={{ textTransform: "capitalize" }}>
                      {type} Experience

                    </h2>

                    {filteredExperience.map((exp: any, expIndex: number) => {

                      const relatedResponsibilities = responsibilities.filter(
                        (r: any) => r.experience_id === exp.experience_id
                      )

                      const relatedTools = tools.filter(
                        (t: any) => t.experience_id === exp.experience_id
                      )

                      return (
                        <div
                          key={exp.experience_id}
                          style={{
                            border: "1px solid #ccc",
                            padding: 20,
                            marginBottom: 25,
                            borderRadius: 8
                          }}
                        >

                          <div style={{ marginBottom: 10 }}>
                            <button
                              style={{ color: "red" }}
                              onClick={async () => {

                                if (!confirm("Delete this experience permanently?")) return

                                const token = await getAccessTokenSilently({
                                  authorizationParams: {
                                    audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                  }
                                })

                                const res = await fetch(
                                  `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-experience/${exp.experience_id}`,
                                  {
                                    method: "DELETE",
                                    headers: {
                                      Authorization: `Bearer ${token}`
                                    }
                                  }
                                )

                                const data = await res.json()

                                if (!res.ok) {
                                  alert(data.detail || "Delete failed")
                                  return
                                }

                                fetchGroup("experience")
                              }}
                            >
                              Delete Experience
                            </button>
                          </div>



                          {/* MAIN EXPERIENCE FIELDS */}
                          {Object.entries(exp).map(([key, value]: any) => {

                            if (key === "experience_type") return null

                            const isPrimaryKey =
                              key === "id" || key.endsWith("_id")

                            return (
                              <div key={key} style={{ marginBottom: 12 }}>
                                <label style={{ fontWeight: "bold" }}>
                                  {key}
                                  {isEditing && groupSchema?.experience && (
                                    <span style={{ color: "#888", fontWeight: "normal" }}>
                                      {" "}
                                      ({groupSchema["experience"]
                                        ?.find((c: any) => c.column_name === key)?.data_type})
                                    </span>
                                  )}
                                </label>
                                <br />

                                {!isEditing || isPrimaryKey ? (
                                  <span>{String(value)}</span>
                                ) : (
                                  <textarea
                                    rows={2}
                                    style={{ width: "100%" }}
                                    value={value === null ? "" : String(value)}
                                    onChange={(e) => {
                                      const updated = structuredClone(groupData)
                                      const target = updated.experience.find(
                                        (x: any) => x.experience_id === exp.experience_id
                                      )

                                      const newValue = e.target.value

                                      target[key] = newValue === "" ? null : newValue

                                      setGroupData(updated)
                                    }}
                                  />
                                )}
                              </div>
                            )
                          })}

                          {/* RESPONSIBILITIES */}
                          <h4>
                            {type === "experimental" ? "Key Learning Outcomes" : "Responsibilities"}
                          </h4>
                          {relatedResponsibilities.map((res: any) => {

                            const displayValue =
                              type === "experimental"
                                ? res.learning_outcomes
                                : res.responsibility

                            return (
                              <div key={res.id} style={{ marginBottom: 10 }}>

                                {!isEditing ? (
                                  <div>• {displayValue}</div>
                                ) : (
                                  <textarea
                                    rows={2}
                                    style={{ width: "100%" }}
                                    value={displayValue || ""}
                                    onChange={(e) => {
                                      const updated = structuredClone(groupData)
                                      const target =
                                        updated.experience_responsibilities.find(
                                          (x: any) => x.id === res.id
                                        )

                                      if (type === "experimental") {
                                        target.learning_outcomes = e.target.value || null
                                        target.responsibility = null
                                      } else {
                                        target.responsibility = e.target.value || null
                                        target.learning_outcomes = null
                                      }

                                      setGroupData(updated)
                                    }}
                                  />
                                )}

                                {/* DELETE BUTTON */}
                                <button
                                  style={{ color: "red", marginLeft: 10 }}
                                  onClick={async () => {

                                    if (!confirm(
                                      type === "experimental"
                                        ? "Delete this learning outcome?"
                                        : "Delete this responsibility?"
                                    )) return

                                    const token = await getAccessTokenSilently({
                                      authorizationParams: {
                                        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                      }
                                    })

                                    await fetch(
                                      `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-responsibility/${res.id}`,
                                      {
                                        method: "DELETE",
                                        headers: { Authorization: `Bearer ${token}` }
                                      }
                                    )

                                    fetchGroup("experience")
                                  }}
                                >
                                  Delete
                                </button>

                              </div>
                            )
                          })}

                          {!isEditing && (
                            <button
                              onClick={async () => {

                                const isExperimental = type === "experimental"

                                const text = prompt(
                                  isExperimental
                                    ? "Enter learning outcome"
                                    : "Enter responsibility"
                                )

                                if (!text) return

                                const token = await getAccessTokenSilently({
                                  authorizationParams: {
                                    audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                  }
                                })

                                await fetch(
                                  `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-responsibility/${exp.experience_id}`,
                                  {
                                    method: "POST",
                                    headers: {
                                      "Content-Type": "application/json",
                                      Authorization: `Bearer ${token}`
                                    },
                                    body: JSON.stringify(
                                      isExperimental
                                        ? {
                                          responsibility: null,
                                          learning_outcomes: text
                                        }
                                        : {
                                          responsibility: text,
                                          learning_outcomes: null
                                        }
                                    )
                                  }
                                )

                                fetchGroup("experience")
                              }}
                            >
                              {type === "professional"
                                ? "+ Add Responsibility"
                                : "+ Add Learning Outcome"}
                            </button>
                          )}

                          {/* TOOLS */}
                          <h4>
                            Tools
                            {isEditing && groupSchema?.experience_tools && (
                              <span style={{ color: "#888", fontWeight: "normal" }}>
                                {" "}
                                (
                                {
                                  groupSchema["experience_tools"]
                                    ?.find((c: any) => c.column_name === "tool")
                                    ?.data_type
                                }
                                )
                              </span>
                            )}
                          </h4>
                          {relatedTools.map((tool: any) => (
                            <div key={tool.id} style={{ marginBottom: 8 }}>

                              {!isEditing ? (
                                <>
                                  <span>{tool.tool}</span>

                                  <button
                                    style={{ color: "red", marginLeft: 10 }}
                                    onClick={async () => {

                                      if (!confirm("Delete this tool permanently?")) return

                                      const token = await getAccessTokenSilently({
                                        authorizationParams: {
                                          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                        }
                                      })

                                      const res = await fetch(
                                        `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-tool/${tool.id}`,
                                        {
                                          method: "DELETE",
                                          headers: {
                                            Authorization: `Bearer ${token}`
                                          }
                                        }
                                      )

                                      if (!res.ok) {
                                        alert("Delete failed")
                                        return
                                      }

                                      fetchGroup("experience")
                                    }}
                                  >
                                    Delete
                                  </button>
                                </>
                              ) : (
                                <textarea
                                  rows={1}
                                  style={{ width: "100%" }}
                                  value={tool.tool === null ? "" : tool.tool}
                                  onChange={(e) => {
                                    const updated = structuredClone(groupData)
                                    const target =
                                      updated.experience_tools.find(
                                        (x: any) => x.id === tool.id
                                      )

                                    const newValue = e.target.value
                                    target.tool = newValue === "" ? null : newValue

                                    setGroupData(updated)
                                  }}
                                />
                              )}

                            </div>
                          ))}

                          {!isEditing && (
                            <button
                              onClick={async () => {
                                const text = prompt("Enter tool")
                                if (!text) return

                                const token = await getAccessTokenSilently({
                                  authorizationParams: {
                                    audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                  }
                                })

                                const res = await fetch(
                                  `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-tool/${exp.experience_id}`,
                                  {
                                    method: "POST",
                                    headers: {
                                      "Content-Type": "application/json",
                                      Authorization: `Bearer ${token}`
                                    },
                                    body: JSON.stringify({
                                      tool: text
                                    })
                                  }
                                )

                                const data = await res.json()

                                if (!res.ok) {
                                  alert(data.detail || "Insert failed")
                                  return
                                }

                                fetchGroup("experience")
                              }}
                            >
                              + Add Tool
                            </button>
                          )}

                        </div>
                      )
                    })}
                  </div>
                )
              })}

              {showAddForm && (
                <div style={{
                  border: "2px solid black",
                  padding: 25,
                  marginTop: 30
                }}>

                  <h3>Add New Experience</h3>

                  <label>Experience Type</label>
                  <select
                    value={newExperience.experience_type}
                    onChange={(e) =>
                      setNewExperience({
                        ...newExperience,
                        experience_type: e.target.value
                      })
                    }
                  >
                    <option value="">Select</option>
                    <option value="professional">Professional</option>
                    <option value="experimental">Experimental</option>
                  </select>

                  {["role", "company", "location", "start_date", "end_date", "context", "notes"]
                    .map(field => (
                      <div key={field}>
                        <label>{field}</label>
                        <textarea
                          rows={2}
                          value={(newExperience as any)[field]}
                          onChange={(e) =>
                            setNewExperience({
                              ...newExperience,
                              [field]: e.target.value
                            })
                          }
                        />
                      </div>
                    ))}

                  <h4>
                    {newExperience.experience_type === "experimental"
                      ? "Key Learning Outcomes"
                      : "Responsibilities"}
                  </h4>

                  <button onClick={() =>
                    setNewResponsibilities([
                      ...newResponsibilities,
                      { responsibility: "", learning_outcomes: "" }
                    ])
                  }>
                    Add Item
                  </button>

                  {newResponsibilities.map((res, i) => (
                    <textarea
                      key={i}
                      rows={2}
                      placeholder={
                        newExperience.experience_type === "experimental"
                          ? "Learning Outcome"
                          : "Responsibility"
                      }
                      value={
                        newExperience.experience_type === "experimental"
                          ? res.learning_outcomes
                          : res.responsibility
                      }
                      onChange={(e) => {
                        const copy = [...newResponsibilities]

                        if (newExperience.experience_type === "experimental") {
                          copy[i].learning_outcomes = e.target.value
                          copy[i].responsibility = ""
                        } else {
                          copy[i].responsibility = e.target.value
                          copy[i].learning_outcomes = ""
                        }

                        setNewResponsibilities(copy)
                      }}
                    />
                  ))}
                  <h4>Tools</h4>
                  <button onClick={() =>
                    setNewTools([...newTools, { tool: "" }])
                  }>
                    Add Tool
                  </button>

                  {newTools.map((tool, i) => (
                    <textarea
                      key={i}
                      rows={1}
                      placeholder="Tool"
                      value={tool.tool}
                      onChange={(e) => {
                        const copy = [...newTools]
                        copy[i].tool = e.target.value
                        setNewTools(copy)
                      }}
                    />
                  ))}

                  <br /><br />

                  <button onClick={handleAddExperience}>
                    Save Experience
                  </button>

                  <button onClick={() => setShowAddForm(false)}>
                    Cancel
                  </button>

                </div>
              )}
            </>
          ) : activeGroup === "projects" ? (
            <>
              <button onClick={() => setShowAddProjectForm(true)}>
                Add Project
              </button>

              {showAddProjectForm && (
                <div style={{
                  border: "2px solid black",
                  padding: 25,
                  marginTop: 30
                }}>
                  <h3>Add New Project</h3>

                  {["title", "project_type", "description", "scope", "github_url", "primary_role"]
                    .map(field => (
                      <div key={field}>
                        <label>
                          {field}
                          {groupSchema?.projects && (
                            <span style={{ color: "#888", fontWeight: "normal" }}>
                              {" "}
                              (
                              {
                                groupSchema["projects"]
                                  ?.find((c: any) => c.column_name === field)
                                  ?.data_type
                              }
                              )
                            </span>
                          )}
                        </label>
                        <textarea
                          rows={2}
                          value={(newProject as any)[field]}
                          onChange={(e) =>
                            setNewProject({
                              ...newProject,
                              [field]: e.target.value
                            })
                          }
                        />
                      </div>
                    ))}

                  <h4>Tech Stack</h4>
                  <button onClick={() =>
                    setNewTechStack([...newTechStack, { technology: "" }])
                  }>
                    Add Technology
                  </button>

                  {newTechStack.map((tech, i) => (
                    <textarea
                      key={i}
                      rows={1}
                      placeholder="Technology"
                      value={tech.technology}
                      onChange={(e) => {
                        const copy = [...newTechStack]
                        copy[i].technology = e.target.value
                        setNewTechStack(copy)
                      }}
                    />
                  ))}



                  <h4>Outcomes</h4>
                  <button onClick={() =>
                    setNewOutcomes([...newOutcomes, { outcome: "" }])
                  }>
                    Add Outcome
                  </button>

                  {newOutcomes.map((out, i) => (
                    <textarea
                      key={i}
                      rows={2}
                      placeholder="Outcome"
                      value={out.outcome}
                      onChange={(e) => {
                        const copy = [...newOutcomes]
                        copy[i].outcome = e.target.value
                        setNewOutcomes(copy)
                      }}
                    />




                  ))}

                  <br /><br />

                  <button onClick={handleAddProject}>
                    Save Project
                  </button>

                  <button onClick={() => setShowAddProjectForm(false)}>
                    Cancel
                  </button>
                </div>
              )}

              {groupData?.projects?.map((project: any) => {

                const relatedTech = groupData.project_tech_stack.filter(
                  (t: any) => t.project_id === project.project_id
                )

                const relatedOutcomes = groupData.project_outcomes.filter(
                  (o: any) => o.project_id === project.project_id
                )

                return (
                  <div
                    key={project.project_id}
                    style={{
                      border: "2px solid #333",
                      padding: 25,
                      marginBottom: 40,
                      borderRadius: 10
                    }}
                  >
                    <h2>Project</h2>

                    <div style={{ marginBottom: 10 }}>
                      <button
                        style={{ color: "red" }}
                        onClick={async () => {

                          if (!confirm("Delete this project permanently?")) return

                          const token = await getAccessTokenSilently({
                            authorizationParams: {
                              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                            }
                          })

                          const res = await fetch(
                            `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-project/${project.project_id}`,
                            {
                              method: "DELETE",
                              headers: {
                                Authorization: `Bearer ${token}`
                              }
                            }
                          )

                          const data = await res.json()

                          if (!res.ok) {
                            alert(data.detail || "Delete failed")
                            return
                          }

                          fetchGroup("projects")
                        }}
                      >
                        Delete Project
                      </button>
                    </div>

                    {/* PROJECT MAIN FIELDS */}
                    {Object.entries(project).map(([key, value]: any) => {

                      const isPrimaryKey =
                        key === "id" || key.endsWith("_id")

                      return (
                        <div key={key} style={{ marginBottom: 12 }}>
                          <label style={{ fontWeight: "bold" }}>
                            {key}
                            {isEditing && groupSchema?.projects && (
                              <span style={{ color: "#888", fontWeight: "normal" }}>
                                {" "}
                                (
                                {
                                  groupSchema["projects"]
                                    ?.find((c: any) => c.column_name === key)
                                    ?.data_type
                                }
                                )
                              </span>
                            )}
                          </label>
                          <br />

                          {!isEditing || isPrimaryKey ? (
                            <span>{String(value)}</span>
                          ) : (
                            <textarea
                              rows={2}
                              style={{ width: "100%" }}
                              value={value === null ? "" : String(value)}
                              onChange={(e) => {
                                const updated = structuredClone(groupData)
                                const target = updated.projects.find(
                                  (x: any) =>
                                    x.project_id === project.project_id
                                )

                                const newValue = e.target.value
                                target[key] = newValue === "" ? null : newValue

                                setGroupData(updated)
                              }}
                            />
                          )}
                        </div>
                      )
                    })}

                    {/* TECH STACK */}
                    <h4>Tech Stack</h4>
                    {relatedTech.map((tech: any) => (
                      <div key={tech.id}>
                        {!isEditing ? (
                          <div>• {tech.technology}</div>
                        ) : (
                          <textarea
                            rows={1}
                            style={{ width: "100%" }}
                            value={tech.technology === null ? "" : tech.technology}
                            onChange={(e) => {
                              const updated = structuredClone(groupData)
                              const target =
                                updated.project_tech_stack.find(
                                  (x: any) => x.id === tech.id
                                )

                              const newValue = e.target.value
                              target.technology = newValue === "" ? null : newValue

                              setGroupData(updated)
                            }}
                          />
                        )}
                        <button
                          style={{ color: "red", marginLeft: 10 }}
                          onClick={async () => {

                            if (!confirm("Delete this technology?")) return

                            const token = await getAccessTokenSilently({
                              authorizationParams: {
                                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                              }
                            })

                            const res = await fetch(
                              `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-project-tech/${tech.id}`,
                              {
                                method: "DELETE",
                                headers: {
                                  Authorization: `Bearer ${token}`
                                }
                              }
                            )

                            if (!res.ok) {
                              alert("Delete failed")
                              return
                            }

                            fetchGroup("projects")
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    ))}

                    <button
                      onClick={async () => {
                        const text = prompt("Enter technology")
                        if (!text) return

                        const token = await getAccessTokenSilently({
                          authorizationParams: {
                            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                          }
                        })

                        const res = await fetch(
                          `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-project-tech/${project.project_id}`,
                          {
                            method: "POST",
                            headers: {
                              "Content-Type": "application/json",
                              Authorization: `Bearer ${token}`
                            },
                            body: JSON.stringify({
                              technology: text
                            })
                          }
                        )

                        const data = await res.json()

                        if (!res.ok) {
                          alert(data.detail || "Insert failed")
                          return
                        }

                        fetchGroup("projects")
                      }}
                    >
                      + Add Technology
                    </button>

                    {/* OUTCOMES */}
                    <h4>Outcomes</h4>
                    <button
                      onClick={async () => {
                        const text = prompt("Enter outcome")
                        if (!text) return

                        const token = await getAccessTokenSilently({
                          authorizationParams: {
                            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                          }
                        })

                        const res = await fetch(
                          `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-project-outcome/${project.project_id}`,
                          {
                            method: "POST",
                            headers: {
                              "Content-Type": "application/json",
                              Authorization: `Bearer ${token}`
                            },
                            body: JSON.stringify({
                              outcome: text
                            })
                          }
                        )

                        const data = await res.json()

                        if (!res.ok) {
                          alert(data.detail || "Insert failed")
                          return
                        }

                        fetchGroup("projects")
                      }}
                    >
                      + Add Outcome
                    </button>
                    {relatedOutcomes.map((out: any) => (
                      <div key={out.id}>
                        {!isEditing ? (
                          <div>• {out.outcome}</div>
                        ) : (
                          <textarea
                            rows={2}
                            style={{ width: "100%" }}
                            value={out.outcome === null ? "" : out.outcome}
                            onChange={(e) => {
                              const updated = structuredClone(groupData)
                              const target =
                                updated.project_outcomes.find(
                                  (x: any) => x.id === out.id
                                )

                              const newValue = e.target.value
                              target.outcome = newValue === "" ? null : newValue

                              setGroupData(updated)
                            }}
                          />
                        )}


                        <button
                          style={{ color: "red", marginLeft: 10 }}
                          onClick={async () => {

                            if (!confirm("Delete this outcome?")) return

                            const token = await getAccessTokenSilently({
                              authorizationParams: {
                                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                              }
                            })

                            const res = await fetch(
                              `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-project-outcome/${out.id}`,
                              {
                                method: "DELETE",
                                headers: {
                                  Authorization: `Bearer ${token}`
                                }
                              }
                            )

                            if (!res.ok) {
                              alert("Delete failed")
                              return
                            }

                            fetchGroup("projects")
                          }}
                        >
                          Delete
                        </button>


                      </div>
                    ))}

                  </div>
                )
              })}
            </>
          ) : activeGroup === "education" ? (
            <>
              <button onClick={() => setShowAddEducationForm(true)}>
                Add Education
              </button>

              {showAddEducationForm && (
                <div style={{ border: "2px solid black", padding: 25, marginTop: 20 }}>
                  <h3>Add Education</h3>

                  {["degree", "institution", "location", "start_year", "end_year"]
                    .map(field => (
                      <div key={field}>
                        <label>
                          {field}
                          {groupSchema?.education && (
                            <span style={{ color: "#888" }}>
                              {" "}
                              (
                              {
                                groupSchema["education"]
                                  ?.find((c: any) => c.column_name === field)
                                  ?.data_type
                              }
                              )
                            </span>
                          )}
                        </label>
                        <textarea
                          rows={1}
                          value={(newEducation as any)[field]}
                          onChange={(e) =>
                            setNewEducation({
                              ...newEducation,
                              [field]: e.target.value
                            })
                          }
                        />
                      </div>
                    ))}

                  <h4>Courses</h4>

                  <button onClick={() =>
                    setNewCourses([...newCourses, { course_title: "", grade: "" }])
                  }>
                    Add Course
                  </button>

                  {newCourses.map((course, i) => (
                    <div key={i}>
                      <textarea
                        placeholder="course_title"
                        value={course.course_title}
                        onChange={(e) => {
                          const copy = [...newCourses]
                          copy[i].course_title = e.target.value
                          setNewCourses(copy)
                        }}
                      />
                      <textarea
                        placeholder="grade"
                        value={course.grade}
                        onChange={(e) => {
                          const copy = [...newCourses]
                          copy[i].grade = e.target.value
                          setNewCourses(copy)
                        }}
                      />
                    </div>
                  ))}

                  <br />

                  <button onClick={handleAddEducation}>
                    Save Education
                  </button>

                  <button onClick={() => setShowAddEducationForm(false)}>
                    Cancel
                  </button>
                </div>
              )}

              {groupData?.education?.map((edu: any) => {

                const relatedCourses = groupData.education_courses.filter(
                  (c: any) => c.education_id === edu.education_id
                )

                return (
                  <div
                    key={edu.education_id}
                    style={{
                      border: "2px solid #333",
                      padding: 25,
                      marginBottom: 40,
                      borderRadius: 10
                    }}
                  >
                    <button
                      style={{ color: "red" }}
                      onClick={async () => {

                        if (!confirm("Delete this education permanently?")) return

                        const token = await getAccessTokenSilently({
                          authorizationParams: {
                            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                          }
                        })

                        await fetch(
                          `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-education/${edu.education_id}`,
                          {
                            method: "DELETE",
                            headers: { Authorization: `Bearer ${token}` }
                          }
                        )

                        fetchGroup("education")
                      }}
                    >
                      Delete Education
                    </button>



                    {Object.entries(edu).map(([key, value]: any) => {

                      const isPrimaryKey = key.endsWith("_id")

                      return (
                        <div key={key} style={{ marginBottom: 12 }}>
                          <label style={{ fontWeight: "bold" }}>
                            {key}
                            {isEditing && groupSchema?.education && (
                              <span style={{ color: "#888", fontWeight: "normal" }}>
                                {" "}
                                (
                                {
                                  groupSchema["education"]
                                    ?.find((c: any) => c.column_name === key)
                                    ?.data_type
                                }
                                )
                              </span>
                            )}
                          </label>

                          <br />

                          {!isEditing || isPrimaryKey ? (
                            <span>{String(value)}</span>
                          ) : (
                            <textarea
                              rows={2}
                              style={{ width: "100%" }}
                              value={value === null ? "" : String(value)}
                              onChange={(e) => {
                                const updated = structuredClone(groupData)
                                const target = updated.education.find(
                                  (x: any) => x.education_id === edu.education_id
                                )
                                target[key] = e.target.value === "" ? null : e.target.value
                                setGroupData(updated)
                              }}
                            />
                          )}
                        </div>
                      )
                    })}

                    <h4>Courses</h4>

                    {relatedCourses.map((course: any) => (
                      <div key={course.id}>
                        {!isEditing ? (
                          <div>
                            • {course.course_title} ({course.grade})
                          </div>
                        ) : (
                          <>
                            <textarea
                              value={course.course_title || ""}
                              onChange={(e) => {
                                const updated = structuredClone(groupData)
                                const target = updated.education_courses.find(
                                  (x: any) => x.id === course.id
                                )
                                target.course_title = e.target.value
                                setGroupData(updated)
                              }}
                            />
                            <textarea
                              value={course.grade || ""}
                              onChange={(e) => {
                                const updated = structuredClone(groupData)
                                const target = updated.education_courses.find(
                                  (x: any) => x.id === course.id
                                )
                                target.grade = e.target.value
                                setGroupData(updated)
                              }}
                            />
                          </>
                        )}
                      </div>
                    ))}

                  </div>
                )
              })}
            </>
          ) : activeGroup === "skills" ? (
            <>
              <button onClick={() => setShowAddSkillForm(true)}>
                Add Skill
              </button>

              {showAddSkillForm && (
                <div style={{ border: "2px solid black", padding: 20, marginTop: 20 }}>
                  <h3>Add Skill</h3>

                  {["skill_name", "category", "proficiency_level"].map(field => (
                    <div key={field}>
                      <label>
                        {field}
                        {field !== "proficiency_level" && groupSchema?.skills && (
                          <span style={{ color: "#888" }}>
                            {" "}
                            (
                            {
                              groupSchema["skills"]
                                ?.find((c: any) => c.column_name === field)
                                ?.data_type
                            }
                            )
                          </span>
                        )}
                      </label>
                      <input
                        type="text"
                        value={(newSkill as any)[field]}
                        onChange={(e) =>
                          setNewSkill({
                            ...newSkill,
                            [field]: e.target.value
                          })
                        }
                      />
                    </div>
                  ))}

                  <button onClick={handleAddSkill}>Save</button>
                  <button onClick={() => setShowAddSkillForm(false)}>Cancel</button>
                </div>
              )}

              {groupData?.user_skills?.map((us: any) => {

                const skill = groupData.skills.find(
                  (s: any) => s.skill_id === us.skill_id
                )

                if (!skill) return null

                return (
                  <div
                    key={us.skill_id}
                    style={{
                      border: "2px solid #333",
                      padding: 20,
                      marginBottom: 30,
                      borderRadius: 10
                    }}
                  >
                    {/* Skill Name */}
                    <div>
                      <label style={{ fontWeight: "bold" }}>skill_name</label>
                      <br />
                      {!isEditing ? (
                        <span>{skill.skill_name}</span>
                      ) : (
                        <input
                          type="text"
                          value={skill.skill_name || ""}
                          onChange={(e) => {
                            const updated = structuredClone(groupData)
                            const target = updated.skills.find(
                              (s: any) => s.skill_id === skill.skill_id
                            )
                            target.skill_name = e.target.value
                            setGroupData(updated)
                          }}
                        />
                      )}
                    </div>

                    {/* Category */}
                    <div>
                      <label style={{ fontWeight: "bold" }}>category</label>
                      <br />
                      {!isEditing ? (
                        <span>{skill.category}</span>
                      ) : (
                        <input
                          type="text"
                          value={skill.category || ""}
                          onChange={(e) => {
                            const updated = structuredClone(groupData)
                            const target = updated.skills.find(
                              (s: any) => s.skill_id === skill.skill_id
                            )
                            target.category = e.target.value
                            setGroupData(updated)
                          }}
                        />
                      )}
                    </div>

                    {/* Proficiency */}
                    <div>
                      <label style={{ fontWeight: "bold" }}>proficiency_level</label>
                      <br />
                      {!isEditing ? (
                        <span>{us.proficiency_level}</span>
                      ) : (
                        <input
                          type="number"
                          value={us.proficiency_level || ""}
                          onChange={(e) => {
                            const updated = structuredClone(groupData)
                            const target = updated.user_skills.find(
                              (x: any) =>
                                x.user_id === us.user_id &&
                                x.skill_id === us.skill_id
                            )
                            target.proficiency_level =
                              e.target.value === "" ? null : Number(e.target.value)
                            setGroupData(updated)
                          }}
                        />
                      )}
                    </div>

                    <button
                      style={{ color: "red" }}
                      onClick={async () => {

                        if (!confirm("Delete this skill?")) return

                        const token = await getAccessTokenSilently({
                          authorizationParams: {
                            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                          }
                        })

                        const res = await fetch(
                          `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-skill/${us.user_id}/${us.skill_id}`,
                          {
                            method: "DELETE",
                            headers: { Authorization: `Bearer ${token}` }
                          }
                        )

                        if (!res.ok) {
                          alert("Delete failed")
                          return
                        }

                        fetchGroup("skills")
                      }}
                    >
                      Delete Skill
                    </button>
                  </div>
                )
              })}
            </>
          ) : activeGroup === "others" ? (
            <>
              {Object.entries(groupData).map(([tableName, rows]: any) => {



                return (
                  <div key={tableName} style={{
                    border: "2px solid #333",
                    padding: 25,
                    marginBottom: 40,
                    borderRadius: 10
                  }}>

                    <h3 style={{ textTransform: "capitalize" }}>
                      {tableName}
                    </h3>

                    <button
                      onClick={() =>
                        setActiveAddTable(
                          activeAddTable === tableName ? null : tableName
                        )
                      }
                    >
                      Add {tableName.slice(0, -1)}
                    </button>

                    {activeAddTable === tableName && (
                      <div style={{ marginTop: 15 }}>
                        {groupSchema?.[tableName]?.map((col: any) => {

                          if (
                            col.column_name === "id" ||
                            col.column_name.endsWith("_id")
                          )
                            return null

                          return (
                            <div key={col.column_name}>
                              <label style={{ fontWeight: "bold" }}>
                                {col.column_name}
                                <span style={{ color: "#888", fontWeight: "normal" }}>
                                  {" "}
                                  ({col.data_type})
                                </span>
                              </label>
                              <br />
                              <textarea
                                rows={1}
                                value={newRecord[col.column_name] || ""}
                                onChange={(e) =>
                                  setNewRecord({
                                    ...newRecord,
                                    [col.column_name]: e.target.value
                                  })
                                }
                              />
                            </div>
                          )
                        })}

                        <button
                          onClick={async () => {

                            const token = await getAccessTokenSilently({
                              authorizationParams: {
                                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                              }
                            })

                            const res = await fetch(
                              `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/add-record/${tableName}`,
                              {
                                method: "POST",
                                headers: {
                                  "Content-Type": "application/json",
                                  Authorization: `Bearer ${token}`
                                },
                                body: JSON.stringify(newRecord)
                              }
                            )

                            if (!res.ok) {
                              alert("Insert failed")
                              return
                            }

                            alert("Record added successfully")

                            setNewRecord({
                              user_id: "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"
                            })

                            setActiveAddTable(null)

                            fetchGroup("others")
                          }}
                        >
                          Save
                        </button>
                      </div>
                    )}

                    {rows.map((row: any) => {

                      const pkField = Object.keys(row).find(
                        (k) => k.endsWith("_id") || k === "id"
                      )

                      if (!pkField) return null
                      return (
                        <div
                          key={row[pkField]}
                          style={{
                            marginTop: 20,
                            paddingTop: 20,
                            borderTop: "1px solid #ccc"
                          }}
                        >
                          {Object.entries(row).map(([key, value]: any) => {

                            const isPrimaryKey = key === pkField

                            return (
                              <div key={key} style={{ marginBottom: 12 }}>
                                <label style={{ fontWeight: "bold" }}>
                                  {key}
                                  {isEditing && groupSchema?.[tableName] && (
                                    <span style={{ color: "#888", fontWeight: "normal" }}>
                                      {" "}
                                      (
                                      {
                                        groupSchema[tableName]
                                          ?.find((c: any) => c.column_name === key)
                                          ?.data_type
                                      }
                                      )
                                    </span>
                                  )}
                                </label>
                                <br />

                                {!isEditing || isPrimaryKey ? (
                                  <span>{String(value)}</span>
                                ) : (
                                  <textarea
                                    rows={1}
                                    style={{ width: "100%" }}
                                    value={value || ""}
                                    onChange={(e) => {
                                      const updated = structuredClone(groupData)
                                      const target =
                                        updated[tableName].find(
                                          (x: any) => x[pkField] === row[pkField]
                                        )
                                      target[key] =
                                        e.target.value === "" ? null : e.target.value
                                      setGroupData(updated)
                                    }}
                                  />
                                )}
                              </div>
                            )
                          })}

                          <button
                            style={{ color: "red" }}
                            onClick={async () => {

                              if (!confirm("Delete this record?")) return

                              const token = await getAccessTokenSilently({
                                authorizationParams: {
                                  audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE
                                }
                              })

                              await fetch(
                                `${process.env.NEXT_PUBLIC_BACKEND_URL}/admin/delete-record/${tableName}/${row[pkField]}`,
                                {
                                  method: "DELETE",
                                  headers: { Authorization: `Bearer ${token}` }
                                }
                              )

                              fetchGroup("others")
                            }}
                          >
                            Delete
                          </button>

                        </div>
                      )
                    })}

                  </div>
                )
              })}
            </>
          ) : (
            /* ========================= */
            /* DEFAULT (PROFILE etc)     */
            /* ========================= */
            Object.entries(groupData).map(([tableName, rows]: any) => (
              <div key={tableName} style={{ marginBottom: 40 }}>
                <h3>{tableName}</h3>

                {rows.map((row: any, rowIndex: number) => (
                  <div
                    key={rowIndex}
                    style={{
                      border: "1px solid #ccc",
                      padding: 20,
                      marginBottom: 20,
                      borderRadius: 8
                    }}
                  >
                    {Object.entries(row).map(([key, value]: any) => {

                      const isPrimaryKey =
                        key === "id" ||
                        key.endsWith("_id")

                      return (
                        <div key={key} style={{ marginBottom: 12 }}>
                          <label style={{ fontWeight: "bold" }}>
                            {key}
                            {isEditing && groupSchema?.[tableName] && (
                              <span style={{ color: "#888", fontWeight: "normal" }}>
                                {" "}
                                (
                                {
                                  groupSchema[tableName]
                                    ?.find((c: any) => c.column_name === key)
                                    ?.data_type
                                }
                                )
                              </span>
                            )}
                          </label>
                          <br />

                          {!isEditing || isPrimaryKey ? (
                            <span>{String(value)}</span>
                          ) : (
                            <textarea
                              rows={2}
                              style={{ width: "100%" }}
                              value={value === null ? "" : String(value)}
                              onChange={(e) => {
                                const updated = structuredClone(groupData)
                                const newValue = e.target.value
                                updated[tableName][rowIndex][key] =
                                  newValue === "" ? null : newValue
                                setGroupData(updated)
                              }}
                            />
                          )}
                        </div>
                      )
                    })}
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
