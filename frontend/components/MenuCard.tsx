//frontend/components/MenuCard.tsx

type Props = {
  title: string;
  items: string[];
  onSelect: (value: string) => void;
};

export default function MenuCard({ title, items, onSelect }: Props) {

  const menuButtonStyle: React.CSSProperties = {
    background: "linear-gradient(135deg, #22c55e, #16a34a)",
    color: "#ffffff",
    fontSize: 12,
    fontWeight: 600,
    borderRadius: 14,
    padding: "12px 10px",
    border: "none",
    cursor: "pointer",
    transition: "transform 0.08s ease, box-shadow 0.08s ease",
    boxShadow: "0 6px 14px rgba(0,0,0,0.15)",
  };





  return (
    <div
      style={{
        background: "rgba(94, 182, 129, 0.06)",
        borderRadius: 16,
        padding: 14,
        marginTop: 14,
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: 12 }}>{title}</p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: 20,
        }}
      >
        {items.map((item) => (
          <button
            key={item}
            onClick={() => onSelect(item)}
            style={menuButtonStyle}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = "scale(0.95)";
              e.currentTarget.style.boxShadow = "0 3px 8px rgba(0,0,0,0.25)";
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = "scale(1)";
              e.currentTarget.style.boxShadow = "0 6px 14px rgba(0,0,0,0.15)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "scale(1)";
              e.currentTarget.style.boxShadow = "0 6px 14px rgba(0,0,0,0.15)";
            }}
          >
            {item}
          </button>

        ))}
      </div>
    </div>
  );
}
