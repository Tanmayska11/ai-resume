import { ReactNode } from "react";

export default function ChatShell({ children }: { children: ReactNode }) {
  return (
    <div className="chat-card">
      <h1 style={{ textAlign: "center", marginBottom: 12 }}>
        AI Resume Assistant
      </h1>
      {children}
    </div>
  );
}
