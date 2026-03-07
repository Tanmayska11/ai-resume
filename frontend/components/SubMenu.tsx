type SubMenuItem = {
  label: string;
  value: string;
};

type Props = {
  title: string;
  items: SubMenuItem[];
  onSelect: (value: string) => void;
  onBack: () => void;
};

export default function SubMenu({ title, items, onSelect, onBack }: Props) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>{title}</h3>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {items.map((item) => (
          <button
            key={item.value}
            onClick={() => onSelect(item.value)}
            style={{
              padding: "10px",
              borderRadius: 10,
              border: "1px solid #cbd5f5",
              background: "#f1f5f9",
              cursor: "pointer",
            }}
          >
            {item.label}
          </button>
        ))}

        <button
          onClick={onBack}
          style={{
            marginTop: 6,
            background: "transparent",
            border: "none",
            color: "#2563eb",
            cursor: "pointer",
          }}
        >
          ⬅ Back to Main Menu
        </button>
      </div>
    </div>
  );
}
