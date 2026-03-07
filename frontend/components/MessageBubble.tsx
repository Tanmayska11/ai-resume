//frontend/components/MessageBubble.tsx

import { Role } from "@/types/chat";
import ReactMarkdown from "react-markdown";

type Props = {
  role: Role;
  text: string;
};

export default function MessageBubble({ role, text }: Props) {
  const isBot = role === "assistant";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isBot ? "flex-start" : "flex-end",
        marginBottom: 12,
      }}
    >
      {isBot && <span style={{ marginRight: 8 }}>🤖</span>}

      <div
        style={{
          background: isBot ? "#ede9fe" : "#f8c1f4",
          color: "#000",
          padding: "12px 16px",
          borderRadius: 14,
          maxWidth: "70%",
          lineHeight: 1.6,
        }}
      >
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>

      {!isBot && <span style={{ marginLeft: 8 }}>🧑</span>}
    </div>
  );
}
