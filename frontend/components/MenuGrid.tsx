//frontend/components/MenuGrid.tsx

type MenuItem = {
  id: string;
  label: string;
};

const menuItems: MenuItem[] = [
  { id: "profile", label: "👤 Profile" },
  { id: "experience", label: "💼 Experience" },
  { id: "projects", label: "📁 Projects" },
  { id: "skills", label: "🛠 Skills" },
  { id: "education", label: "🎓 Education" },
  { id: "certifications", label: "📜 Certifications" },
  { id: "languages", label: "🌍 Languages" },
  { id: "interests", label: "🏃 Interests" },
  { id: "career", label: "🎯 Career Preferences" },
];

export default function MenuGrid({
  onSelect,
}: {
  onSelect: (id: string) => void;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "12px",
        marginTop: "16px",
      }}
    >
      {menuItems.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect(item.id)}
          style={{
            background: "rgba(20, 83, 45, 0.06)",
            border: "1px solid rgba(0,0,0,0.08)",
            borderRadius: "12px",
            padding: "10px 8px",
            fontSize: "0.8rem",
            cursor: "pointer",
          }}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
